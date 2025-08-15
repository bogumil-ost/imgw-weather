# Konfiguracja aplikacji IMGW Weather
# config.py

import os
from typing import Dict, Any

class Config:
    """Klasa konfiguracji aplikacji"""
    
    # Konfiguracja bazy danych
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "weather_data.db")
    DATABASE_BACKUP_INTERVAL: int = int(os.getenv("DATABASE_BACKUP_INTERVAL", "24"))  # godziny
    
    # Konfiguracja API IMGW
    IMGW_API_URL: str = "https://danepubliczne.imgw.pl/api/data/synop"
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))  # sekundy
    DATA_FETCH_INTERVAL: int = int(os.getenv("DATA_FETCH_INTERVAL", "60"))  # minuty
    
    # Konfiguracja serwera
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Konfiguracja logowania
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "weather_app.log")
    LOG_MAX_SIZE: int = int(os.getenv("LOG_MAX_SIZE", "10485760"))  # 10MB
    LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    
    # Konfiguracja historii danych
    DATA_RETENTION_DAYS: int = int(os.getenv("DATA_RETENTION_DAYS", "365"))
    MAX_RECORDS_PER_REQUEST: int = int(os.getenv("MAX_RECORDS_PER_REQUEST", "1000"))
    
    # Konfiguracja bezpieczeństwa
    ALLOWED_HOSTS: list = os.getenv("ALLOWED_HOSTS", "*").split(",")
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Współrzędne geograficzne głównych stacji (do mapy)
    STATION_COORDINATES: Dict[str, Dict[str, float]] = {
        "12295": {"lat": 53.1325, "lon": 23.1688, "name": "Białystok"},
        "12600": {"lat": 49.8224, "lon": 19.0444, "name": "Bielsko Biała"},
        "12235": {"lat": 53.6983, "lon": 17.5583, "name": "Chojnice"},
        "12550": {"lat": 50.8118, "lon": 19.1203, "name": "Częstochowa"},
        "12160": {"lat": 54.1522, "lon": 19.4044, "name": "Elbląg"},
        "12375": {"lat": 52.2297, "lon": 21.0122, "name": "Warszawa"},
        "12566": {"lat": 50.0647, "lon": 19.9450, "name": "Kraków"},
        "12115": {"lat": 54.3520, "lon": 18.6466, "name": "Gdańsk"},
        "12250": {"lat": 52.4064, "lon": 16.9252, "name": "Poznań"},
        "12424": {"lat": 51.7520, "lon": 19.4660, "name": "Łódź"},
        "12560": {"lat": 50.2649, "lon": 19.0238, "name": "Katowice"},
        "12465": {"lat": 51.2465, "lon": 22.5684, "name": "Lublin"},
        "12400": {"lat": 51.1079, "lon": 17.0385, "name": "Wrocław"},
        "12185": {"lat": 54.7158, "lon": 20.5060, "name": "Olsztyn"},
        "12595": {"lat": 49.9747, "lon": 20.4568, "name": "Nowy Sącz"},
        "12210": {"lat": 53.7784, "lon": 15.7201, "name": "Szczecin"},
        "12495": {"lat": 50.8551, "lon": 20.6289, "name": "Kielce"},
        "12125": {"lat": 54.4773, "lon": 17.0322, "name": "Słupsk"}
    }
    
    # Mapowanie kierunków wiatru
    WIND_DIRECTIONS: Dict[str, str] = {
        "0": "N", "360": "N", "10": "N", "20": "NNE", "30": "NNE", "40": "NE",
        "50": "NE", "60": "ENE", "70": "ENE", "80": "E", "90": "E",
        "100": "E", "110": "ESE", "120": "ESE", "130": "SE", "140": "SE",
        "150": "SSE", "160": "SSE", "170": "S", "180": "S", "190": "S",
        "200": "SSW", "210": "SSW", "220": "SW", "230": "SW", "240": "WSW",
        "250": "WSW", "260": "W", "270": "W", "280": "W", "290": "WNW",
        "300": "WNW", "310": "NW", "320": "NW", "330": "NNW", "340": "NNW",
        "350": "N"
    }
    
    # Zakresy kolorów dla temperatury (do wizualizacji)
    TEMPERATURE_COLORS: Dict[str, Any] = {
        "extreme_cold": {"min": -30, "max": -20, "color": "#0D47A1"},
        "very_cold": {"min": -20, "max": -10, "color": "#1976D2"},
        "cold": {"min": -10, "max": 0, "color": "#42A5F5"},
        "cool": {"min": 0, "max": 10, "color": "#81C784"},
        "mild": {"min": 10, "max": 20, "color": "#FFD54F"},
        "warm": {"min": 20, "max": 30, "color": "#FF8A65"},
        "hot": {"min": 30, "max": 40, "color": "#F44336"},
        "extreme_hot": {"min": 40, "max": 50, "color": "#B71C1C"}
    }
    
    @classmethod
    def get_temperature_color(cls, temperature: float) -> str:
        """Zwraca kolor dla danej temperatury"""
        for _, config in cls.TEMPERATURE_COLORS.items():
            if config["min"] <= temperature < config["max"]:
                return config["color"]
        return "#757575"  # Domyślny kolor szary
    
    @classmethod
    def get_wind_direction_name(cls, degrees: str) -> str:
        """Zwraca nazwę kierunku wiatru na podstawie stopni"""
        try:
            deg = int(float(degrees))
            # Znajdź najbliższy kierunek
            closest = min(cls.WIND_DIRECTIONS.keys(), 
                         key=lambda x: abs(int(x) - deg))
            return cls.WIND_DIRECTIONS[closest]
        except (ValueError, KeyError):
            return "N/A"
    
    @classmethod
    def get_station_coordinates(cls, station_id: str) -> Dict[str, float]:
        """Zwraca współrzędne stacji meteorologicznej"""
        return cls.STATION_COORDINATES.get(station_id, {"lat": 52.0, "lon": 20.0})

# Dodatkowe stałe
class Constants:
    """Stałe używane w aplikacji"""
    
    # Formaty daty
    DATE_FORMAT = "%Y-%m-%d"
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    # Nazwy parametrów w języku polskim
    PARAMETER_NAMES = {
        "temperatura": "Temperatura (°C)",
        "predkosc_wiatru": "Prędkość wiatru (m/s)",
        "kierunek_wiatru": "Kierunek wiatru (°)",
        "wilgotnosc_wzgledna": "Wilgotność względna (%)",
        "suma_opadu": "Suma opadów (mm)",
        "cisnienie": "Ciśnienie (hPa)"
    }
    
    # Jednostki parametrów
    PARAMETER_UNITS = {
        "temperatura": "°C",
        "predkosc_wiatru": "m/s",
        "kierunek_wiatru": "°",
        "wilgotnosc_wzgledna": "%",
        "suma_opadu": "mm",
        "cisnienie": "hPa"
    }
    
    # Limity wartości (do walidacji)
    PARAMETER_LIMITS = {
        "temperatura": {"min": -50, "max": 50},
        "predkosc_wiatru": {"min": 0, "max": 100},
        "kierunek_wiatru": {"min": 0, "max": 360},
        "wilgotnosc_wzgledna": {"min": 0, "max": 100},
        "suma_opadu": {"min": 0, "max": 200},
        "cisnienie": {"min": 900, "max": 1100}
    }

# Eksport konfiguracji
config = Config()
constants = Constants()