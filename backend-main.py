# Backend aplikacji IMGW - FastAPI + SQLite
# main.py

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import sqlite3
import requests
import json
from datetime import datetime, timedelta
import logging
import asyncio
import os
from typing import List, Optional
from pydantic import BaseModel
import schedule
import time
import threading

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('weather_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Modele Pydantic
class WeatherStation(BaseModel):
    id_stacji: str
    stacja: str
    data_pomiaru: str
    godzina_pomiaru: str
    temperatura: Optional[str] = None
    predkosc_wiatru: Optional[str] = None
    kierunek_wiatru: Optional[str] = None
    wilgotnosc_wzgledna: Optional[str] = None
    suma_opadu: Optional[str] = None
    cisnienie: Optional[str] = None

class WeatherResponse(BaseModel):
    stations: List[WeatherStation]
    total_count: int
    last_update: str

# FastAPI aplikacja
app = FastAPI(
    title="IMGW Weather API",
    description="System monitorowania danych meteorologicznych z API IMGW",
    version="1.0.0"
)

# Konfiguracja bazy danych
DATABASE_PATH = "weather_data.db"
IMGW_API_URL = "https://danepubliczne.imgw.pl/api/data/synop"

class DatabaseManager:
    """Klasa do zarządzania bazą danych SQLite"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicjalizacja bazy danych i utworzenie tabel"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS weather_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_stacji TEXT NOT NULL,
                        stacja TEXT NOT NULL,
                        data_pomiaru TEXT NOT NULL,
                        godzina_pomiaru TEXT NOT NULL,
                        temperatura TEXT,
                        predkosc_wiatru TEXT,
                        kierunek_wiatru TEXT,
                        wilgotnosc_wzgledna TEXT,
                        suma_opadu TEXT,
                        cisnienie TEXT,
                        timestamp_dodania TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(id_stacji, data_pomiaru, godzina_pomiaru)
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS api_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status TEXT,
                        records_count INTEGER,
                        error_message TEXT
                    )
                ''')
                
                conn.commit()
                logger.info("Baza danych została zainicjalizowana")
        except Exception as e:
            logger.error(f"Błąd podczas inicjalizacji bazy danych: {str(e)}")
    
    def insert_weather_data(self, data: List[dict]) -> int:
        """Wstawia dane pogodowe do bazy danych"""
        inserted_count = 0
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for record in data:
                    try:
                        cursor.execute('''
                            INSERT OR REPLACE INTO weather_data 
                            (id_stacji, stacja, data_pomiaru, godzina_pomiaru, 
                             temperatura, predkosc_wiatru, kierunek_wiatru, 
                             wilgotnosc_wzgledna, suma_opadu, cisnienie)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            record.get('id_stacji'),
                            record.get('stacja'),
                            record.get('data_pomiaru'),
                            record.get('godzina_pomiaru'),
                            record.get('temperatura'),
                            record.get('predkosc_wiatru'),
                            record.get('kierunek_wiatru'),
                            record.get('wilgotnosc_wzgledna'),
                            record.get('suma_opadu'),
                            record.get('cisnienie')
                        ))
                        inserted_count += 1
                    except sqlite3.IntegrityError:
                        # Rekord już istnieje, pomijamy
                        continue
                
                conn.commit()
                logger.info(f"Wstawiono {inserted_count} nowych rekordów")
                
        except Exception as e:
            logger.error(f"Błąd podczas wstawiania danych: {str(e)}")
            
        return inserted_count
    
    def get_latest_data(self, limit: int = 100) -> List[dict]:
        """Pobiera najnowsze dane pogodowe"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM weather_data 
                    WHERE (id_stacji, data_pomiaru, godzina_pomiaru) IN (
                        SELECT id_stacji, data_pomiaru, godzina_pomiaru
                        FROM weather_data
                        GROUP BY id_stacji
                        HAVING MAX(data_pomiaru || godzina_pomiaru)
                    )
                    ORDER BY stacja
                    LIMIT ?
                ''', (limit,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Błąd podczas pobierania danych: {str(e)}")
            return []
    
    def get_historical_data(self, days_back: int = 7) -> List[dict]:
        """Pobiera dane historyczne z określonego okresu"""
        try:
            start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM weather_data 
                    WHERE data_pomiaru >= ?
                    ORDER BY data_pomiaru DESC, godzina_pomiaru DESC
                ''', (start_date,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Błąd podczas pobierania danych historycznych: {str(e)}")
            return []
    
    def log_api_call(self, status: str, records_count: int = 0, error_message: str = None):
        """Loguje wywołanie API"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO api_logs (status, records_count, error_message)
                    VALUES (?, ?, ?)
                ''', (status, records_count, error_message))
                conn.commit()
        except Exception as e:
            logger.error(f"Błąd podczas logowania API: {str(e)}")

class WeatherDataFetcher:
    """Klasa do pobierania danych z API IMGW"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def fetch_data_from_imgw(self) -> bool:
        """Pobiera dane z API IMGW i zapisuje do bazy danych"""
        try:
            logger.info("Rozpoczynam pobieranie danych z API IMGW")
            
            response = requests.get(IMGW_API_URL, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                logger.warning("Brak danych w odpowiedzi API")
                self.db_manager.log_api_call("WARNING", 0, "Brak danych w odpowiedzi")
                return False
            
            inserted_count = self.db_manager.insert_weather_data(data)
            
            logger.info(f"Pomyślnie pobrano i zapisano {inserted_count} rekordów")
            self.db_manager.log_api_call("SUCCESS", inserted_count)
            
            return True
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Błąd HTTP podczas pobierania danych: {str(e)}"
            logger.error(error_msg)
            self.db_manager.log_api_call("ERROR", 0, error_msg)
            return False
            
        except json.JSONDecodeError as e:
            error_msg = f"Błąd dekodowania JSON: {str(e)}"
            logger.error(error_msg)
            self.db_manager.log_api_call("ERROR", 0, error_msg)
            return False
            
        except Exception as e:
            error_msg = f"Nieoczekiwany błąd: {str(e)}"
            logger.error(error_msg)
            self.db_manager.log_api_call("ERROR", 0, error_msg)
            return False

# Inicjalizacja komponentów
db_manager = DatabaseManager(DATABASE_PATH)
data_fetcher = WeatherDataFetcher(db_manager)

# Harmonogram automatycznego pobierania danych
def schedule_data_fetching():
    """Funkcja do harmonogramowania pobierania danych"""
    def run_fetch():
        asyncio.run(data_fetcher.fetch_data_from_imgw())
    
    # Pobieranie danych co godzinę
    schedule.every().hour.do(run_fetch)
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Sprawdzaj co minutę

# Uruchom harmonogram w osobnym wątku
threading.Thread(target=schedule_data_fetching, daemon=True).start()

# API Endpoints

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Strona główna - zwraca frontend aplikacji"""
    try:
        with open("frontend/index.html", "r", encoding="utf-8") as file:
            return HTMLResponse(content=file.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Frontend nie został znaleziony</h1>")

@app.get("/api/weather/current", response_model=WeatherResponse)
async def get_current_weather():
    """Pobiera aktualne dane pogodowe"""
    try:
        data = db_manager.get_latest_data()
        
        if not data:
            # Jeśli brak danych w bazie, spróbuj pobrać z API
            await data_fetcher.fetch_data_from_imgw()
            data = db_manager.get_latest_data()
        
        stations = [WeatherStation(**record) for record in data]
        
        return WeatherResponse(
            stations=stations,
            total_count=len(stations),
            last_update=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Błąd podczas pobierania aktualnych danych: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/weather/historical")
async def get_historical_weather(days: int = 7):
    """Pobiera dane historyczne"""
    try:
        if days > 30:
            raise HTTPException(status_code=400, detail="Maksymalny okres to 30 dni")
        
        data = db_manager.get_historical_data(days)
        stations = [WeatherStation(**record) for record in data]
        
        return WeatherResponse(
            stations=stations,
            total_count=len(stations),
            last_update=datetime.now().isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas pobierania danych historycznych: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/weather/refresh")
async def refresh_weather_data(background_tasks: BackgroundTasks):
    """Wymusić odświeżenie danych z API IMGW"""
    try:
        background_tasks.add_task(data_fetcher.fetch_data_from_imgw)
        return {"message": "Odświeżanie danych zostało rozpoczęte w tle"}
    except Exception as e:
        logger.error(f"Błąd podczas odświeżania danych: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Sprawdzenie stanu aplikacji"""
    try:
        # Sprawdź połączenie z bazą danych
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM weather_data")
            record_count = cursor.fetchone()[0]
        
        return {
            "status": "healthy",
            "database_records": record_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/stats")
async def get_statistics():
    """Pobiera statystyki aplikacji"""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            # Liczba rekordów
            cursor.execute("SELECT COUNT(*) FROM weather_data")
            total_records = cursor.fetchone()[0]
            
            # Liczba stacji
            cursor.execute("SELECT COUNT(DISTINCT id_stacji) FROM weather_data")
            stations_count = cursor.fetchone()[0]
            
            # Najnowsza aktualizacja
            cursor.execute("SELECT MAX(data_pomiaru || ' ' || godzina_pomiaru) FROM weather_data")
            last_update = cursor.fetchone()[0]
            
            # Ostatnie logi API
            cursor.execute("""
                SELECT status, COUNT(*) as count 
                FROM api_logs 
                WHERE timestamp > datetime('now', '-24 hours')
                GROUP BY status
            """)
            api_logs = dict(cursor.fetchall())
            
        return {
            "total_records": total_records,
            "stations_count": stations_count,
            "last_update": last_update,
            "api_calls_24h": api_logs,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Błąd podczas pobierania statystyk: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Serwowanie plików statycznych (frontend)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

if __name__ == "__main__":
    import uvicorn
    
    # Pobierz dane przy starcie aplikacji
    asyncio.run(data_fetcher.fetch_data_from_imgw())
    
    # Uruchom serwer
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=1
    )