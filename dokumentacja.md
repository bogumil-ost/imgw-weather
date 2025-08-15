# System Monitorowania Danych Meteorologicznych IMGW

## Opis Projektu

Aplikacja internetowa służąca do automatycznego pobierania, przechowywania i wizualizacji danych meteorologicznych z API Instytutu Meteorologii i Gospodarki Wodnej (IMGW). System pobiera dane co godzinę i prezentuje je w formie interaktywnych wykresów i map.

## Funkcjonalności

### Frontend (Aplikacja Internetowa)
- **Dashboard** - Mapa Polski z oznaczonymi stacjami meteorologicznymi
- **Wykresy interaktywne** - Temperatura, ciśnienie, opady, wilgotność
- **Tabela danych** - Przeglądanie i eksport danych do CSV
- **Responsywny design** - Działanie na wszystkich urządzeniach
- **Auto-odświeżanie** - Automatyczna aktualizacja danych co godzinę

### Backend (API)
- **FastAPI** - Szybkie i wydajne API REST
- **SQLite** - Lekka baza danych, idealna dla VPS o małych zasobach
- **Automatyczne pobieranie** - Harmonogram pobierania danych co godzinę
- **Logowanie** - Monitoring działania aplikacji
- **Health checks** - Monitorowanie stanu systemu

## Wymagania Systemowe

### Minimalne wymagania VPS:
- **RAM**: 1GB (zalecane 2GB)
- **Dysk**: 15GB (zalecane 20GB)
- **System**: Ubuntu 20.04+ / Debian 10+
- **Python**: 3.8+

## Struktura Projektu

```
imgw-weather-app/
├── main.py                 # Backend FastAPI
├── requirements.txt        # Zależności Python
├── install.sh             # Skrypt instalacyjny
├── frontend/              # Pliki frontend
│   ├── index.html         # Strona główna
│   ├── style.css          # Stylowanie
│   └── app.js            # Logika JavaScript
├── systemd/              # Konfiguracja systemd
│   └── imgw-weather.service
├── nginx/                # Konfiguracja Nginx
│   └── imgw-weather.conf
└── docs/                 # Dokumentacja
    └── README.md
```

## Instalacja na VPS

### 1. Przygotowanie środowiska

```bash
# Aktualizacja systemu
sudo apt update && sudo apt upgrade -y

# Instalacja wymaganych pakietów
sudo apt install -y python3 python3-pip python3-venv nginx sqlite3 git curl
```

### 2. Utworzenie katalogu projektu

```bash
# Utworzenie katalogu
sudo mkdir -p /opt/imgw-weather
sudo chown $USER:$USER /opt/imgw-weather
cd /opt/imgw-weather
```

### 3. Pobranie kodu aplikacji

```bash
# Skopiuj wszystkie pliki projektu do katalogu /opt/imgw-weather/
# Możesz użyć git clone, scp lub innej metody transferu plików
```

### 4. Konfiguracja Python

```bash
# Utworzenie środowiska wirtualnego
python3 -m venv venv
source venv/bin/activate

# Instalacja zależności
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Konfiguracja Nginx

```bash
# Utworzenie konfiguracji Nginx
sudo tee /etc/nginx/sites-available/imgw-weather > /dev/null << 'EOF'
server {
    listen 80;
    server_name your_domain.com;  # Zmień na swoją domenę

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /opt/imgw-weather/frontend;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Aktywacja konfiguracji
sudo ln -sf /etc/nginx/sites-available/imgw-weather /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### 6. Konfiguracja systemd

```bash
# Utworzenie serwisu systemd
sudo tee /etc/systemd/system/imgw-weather.service > /dev/null << 'EOF'
[Unit]
Description=IMGW Weather Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/imgw-weather
Environment=PATH=/opt/imgw-weather/venv/bin
ExecStart=/opt/imgw-weather/venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

### 7. Uruchomienie aplikacji

```bash
# Ustawienie uprawnień
sudo chown -R www-data:www-data /opt/imgw-weather

# Uruchomienie serwisów
sudo systemctl daemon-reload
sudo systemctl enable imgw-weather
sudo systemctl start imgw-weather
sudo systemctl enable nginx

# Sprawdzenie statusu
sudo systemctl status imgw-weather
```

### 8. Konfiguracja firewall (opcjonalnie)

```bash
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22
# sudo ufw enable  # Odkomentuj, aby włączyć firewall
```

## API Endpoints

### Główne endpointy:

- `GET /` - Strona główna aplikacji
- `GET /api/weather/current` - Aktualne dane pogodowe
- `GET /api/weather/historical?days=7` - Dane historyczne
- `POST /api/weather/refresh` - Wymuszenie aktualizacji danych
- `GET /api/health` - Status aplikacji
- `GET /api/stats` - Statystyki systemu

### Przykład odpowiedzi API:

```json
{
  "stations": [
    {
      "id_stacji": "12295",
      "stacja": "Białystok",
      "data_pomiaru": "2025-08-13",
      "godzina_pomiaru": "18",
      "temperatura": "20.3",
      "predkosc_wiatru": "1",
      "kierunek_wiatru": "360",
      "wilgotnosc_wzgledna": "62.3",
      "suma_opadu": "0",
      "cisnienie": "1021.8"
    }
  ],
  "total_count": 1,
  "last_update": "2025-08-13T20:30:00"
}
```

## Monitorowanie i Utrzymanie

### Komendy diagnostyczne:

```bash
# Status aplikacji
sudo systemctl status imgw-weather

# Logi aplikacji
sudo journalctl -u imgw-weather -f

# Restart aplikacji
sudo systemctl restart imgw-weather

# Status Nginx
sudo systemctl status nginx

# Sprawdzenie bazy danych
sqlite3 /opt/imgw-weather/weather_data.db "SELECT COUNT(*) FROM weather_data;"
```

### Backup bazy danych:

```bash
# Backup bazy danych
sqlite3 /opt/imgw-weather/weather_data.db ".backup /opt/imgw-weather/backup_$(date +%Y%m%d_%H%M%S).db"

# Automatyczny backup (dodaj do crontab)
0 2 * * * sqlite3 /opt/imgw-weather/weather_data.db ".backup /opt/imgw-weather/backup_$(date +\%Y\%m\%d).db"
```

## Rozwiązywanie Problemów

### Częste problemy:

1. **Aplikacja nie startuje**
   - Sprawdź logi: `sudo journalctl -u imgw-weather -n 50`
   - Sprawdź uprawnienia: `sudo chown -R www-data:www-data /opt/imgw-weather`

2. **Brak danych z API IMGW**
   - Sprawdź połączenie internetowe
   - Sprawdź status API: `curl https://danepubliczne.imgw.pl/api/data/synop`

3. **Nginx nie działa**
   - Sprawdź konfigurację: `sudo nginx -t`
   - Sprawdź logi: `sudo tail -f /var/log/nginx/error.log`

4. **Mało miejsca na dysku**
   - Wyczyść stare logi: `sudo journalctl --vacuum-time=30d`
   - Wyczyść stare backupy bazy danych

## Konfiguracja SSL/HTTPS

### Instalacja Let's Encrypt:

```bash
# Instalacja certbot
sudo apt install certbot python3-certbot-nginx

# Uzyskanie certyfikatu
sudo certbot --nginx -d your_domain.com

# Automatyczne odnawianie
sudo crontab -e
# Dodaj linię:
0 12 * * * /usr/bin/certbot renew --quiet
```

## Optymalizacja Wydajności

### Dla VPS z 1GB RAM:

1. **Konfiguracja Nginx**:
   - Zmniejsz `worker_processes` do 1
   - Ustaw `worker_connections` na 512

2. **Konfiguracja aplikacji**:
   - Użyj tylko 1 worker proces uvicorn
   - Ogranicz liczbę równoczesnych połączeń z bazą danych

3. **Monitoring zasobów**:
   ```bash
   # Monitorowanie RAM i CPU
   htop
   
   # Sprawdzenie użycia dysku
   df -h
   
   # Sprawdzenie procesów
   ps aux | grep python
   ```

## Licencja

Projekt działa zgodnie z licencją IMGW-PIB na wykorzystanie danych publicznych. Dane pochodzą z API dostępnego pod adresem https://danepubliczne.imgw.pl/

## Wsparcie

W przypadku problemów:
1. Sprawdź logi aplikacji
2. Upewnij się, że API IMGW jest dostępne
3. Sprawdź dokumentację FastAPI i Nginx
4. Skontaktuj się z administratorem systemu

## Changelog

### v1.0.0 (2025-08-13)
- Pierwsza wersja aplikacji
- Automatyczne pobieranie danych z IMGW API
- Interaktywne wykresy i mapa
- Responsywny frontend
- RESTful API backend
- Instrukcje wdrożenia na VPS