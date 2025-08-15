# IMGW Weather Monitoring System

## Szybki Start

### 1. Wymagania
- VPS z Ubuntu 20.04+ / Debian 10+
- 1GB RAM (zalecane 2GB) 
- 15GB miejsca na dysku
- Python 3.8+

### 2. Instalacja

```bash
# Klonuj/skopiuj pliki projektu
cd /opt
sudo git clone <repository_url> imgw-weather
cd imgw-weather

# Uruchom skrypt instalacyjny
chmod +x install.sh
sudo ./install.sh
```

### 3. Sprawdzenie działania

```bash
# Status aplikacji
sudo systemctl status imgw-weather

# Logi aplikacji  
sudo journalctl -u imgw-weather -f

# Test API
curl http://localhost:8000/api/health
```

### 4. Dostęp do aplikacji
- **Frontend**: http://your_server_ip
- **API**: http://your_server_ip/api/weather/current
- **Dokumentacja API**: http://your_server_ip/docs

## Struktura Plików

```
/opt/imgw-weather/
├── main.py              # Backend FastAPI
├── config.py            # Konfiguracja
├── requirements.txt     # Zależności Python
├── install.sh          # Skrypt instalacyjny
├── manage_data.sh      # Zarządzanie danymi
├── weather_data.db     # Baza danych SQLite
├── frontend/           # Pliki frontend
├── logs/              # Pliki logów
└── backupy/           # Backupy bazy danych
```

## Zarządzanie

### Backup bazy danych
```bash
sudo /opt/imgw-weather/manage_data.sh backup
```

### Przywracanie z backupu
```bash
sudo /opt/imgw-weather/manage_data.sh restore backup_file.db.gz
```

### Sprawdzenie stanu
```bash
sudo /opt/imgw-weather/manage_data.sh check
```

## Monitoring

### Logi aplikacji
```bash
# Logi bieżące
sudo journalctl -u imgw-weather -f

# Logi z ostatnich 24h
sudo journalctl -u imgw-weather --since "24 hours ago"
```

### Zasoby systemu
```bash
# Użycie RAM i CPU
htop

# Miejsce na dysku
df -h

# Status serwisów
sudo systemctl status imgw-weather nginx
```

## Rozwiązywanie problemów

### Aplikacja nie startuje
1. Sprawdź logi: `sudo journalctl -u imgw-weather -n 50`
2. Sprawdź uprawnienia: `sudo chown -R www-data:www-data /opt/imgw-weather`
3. Sprawdź zależności: `cd /opt/imgw-weather && source venv/bin/activate && pip list`

### Brak danych
1. Sprawdź API IMGW: `curl https://danepubliczne.imgw.pl/api/data/synop`
2. Wymuszenie odświeżenia: `curl -X POST http://localhost:8000/api/weather/refresh`
3. Sprawdź logi pobierania danych

### Problemy z Nginx
1. Test konfiguracji: `sudo nginx -t`
2. Restart Nginx: `sudo systemctl restart nginx`
3. Sprawdź logi: `sudo tail -f /var/log/nginx/error.log`

## API Endpoints

| Endpoint | Metoda | Opis |
|----------|---------|------|
| `/` | GET | Frontend aplikacji |
| `/api/weather/current` | GET | Aktualne dane pogodowe |
| `/api/weather/historical` | GET | Dane historyczne |
| `/api/weather/refresh` | POST | Wymuszenie aktualizacji |
| `/api/health` | GET | Status aplikacji |
| `/api/stats` | GET | Statystyki systemu |

## Konfiguracja SSL

```bash
# Instalacja Certbot
sudo apt install certbot python3-certbot-nginx

# Uzyskanie certyfikatu
sudo certbot --nginx -d your_domain.com

# Auto-renewal
sudo crontab -e
# Dodaj: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Kontakt

W przypadku problemów sprawdź:
1. Dokumentację w pliku `dokumentacja.md`
2. Logi aplikacji
3. Status API IMGW
4. Zasoby systemowe VPS
