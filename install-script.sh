#!/bin/bash
# Skrypt instalacyjny dla aplikacji IMGW Weather na VPS Ubuntu/Debian
# install.sh

set -e

echo "=== INSTALACJA APLIKACJI IMGW WEATHER ===" 

# Aktualizacja systemu
echo "1. Aktualizacja systemu..."
sudo apt update && sudo apt upgrade -y

# Instalacja wymaganych pakietów systemowych
echo "2. Instalacja pakietów systemowych..."
sudo apt install -y python3 python3-pip python3-venv nginx sqlite3 git curl

# Utworzenie katalogu aplikacji
echo "3. Tworzenie katalogu aplikacji..."
sudo mkdir -p /opt/imgw-weather
sudo chown $USER:$USER /opt/imgw-weather
cd /opt/imgw-weather

# Klonowanie lub kopiowanie plików aplikacji
echo "4. Kopiowanie plików aplikacji..."
# Skopiuj wszystkie pliki projektu do /opt/imgw-weather/

# Utworzenie środowiska wirtualnego Python
echo "5. Tworzenie środowiska wirtualnego..."
python3 -m venv venv
source venv/bin/activate

# Instalacja zależności Python
echo "6. Instalacja zależności Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Utworzenie struktury katalogów
echo "7. Tworzenie struktury katalogów..."
mkdir -p frontend
mkdir -p logs
mkdir -p data

# Kopiowanie plików frontend
echo "8. Przygotowanie frontend..."
# Skopiuj pliki HTML, CSS, JS do katalogu frontend/

# Konfiguracja Nginx
echo "9. Konfiguracja Nginx..."
sudo tee /etc/nginx/sites-available/imgw-weather > /dev/null << EOF
server {
    listen 80;
    server_name your_domain.com;  # Zmień na swoją domenę lub IP

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias /opt/imgw-weather/frontend;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Aktywacja konfiguracji Nginx
sudo ln -sf /etc/nginx/sites-available/imgw-weather /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Konfiguracja systemd service
echo "10. Konfiguracja systemd service..."
sudo tee /etc/systemd/system/imgw-weather.service > /dev/null << EOF
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

# Ustawienie uprawnień
echo "11. Ustawienie uprawnień..."
sudo chown -R www-data:www-data /opt/imgw-weather
sudo chmod +x /opt/imgw-weather/main.py

# Uruchomienie i włączenie serwisów
echo "12. Uruchomienie serwisów..."
sudo systemctl daemon-reload
sudo systemctl enable imgw-weather
sudo systemctl start imgw-weather
sudo systemctl enable nginx

# Sprawdzenie statusu
echo "13. Sprawdzanie statusu..."
sudo systemctl status imgw-weather --no-pager
sudo systemctl status nginx --no-pager

# Konfiguracja firewall (opcjonalne)
echo "14. Konfiguracja firewall..."
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22
# sudo ufw enable  # Odkomentuj jeśli chcesz włączyć firewall

# Utworzenie cron job do automatycznego pobierania danych (backup)
echo "15. Konfiguracja cron job..."
(crontab -l 2>/dev/null; echo "0 * * * * curl -X POST http://localhost:8000/api/weather/refresh") | crontab -

echo ""
echo "=== INSTALACJA ZAKOŃCZONA ==="
echo ""
echo "Aplikacja została zainstalowana i uruchomiona!"
echo "Dostępna pod adresem: http://your_server_ip"
echo ""
echo "Przydatne komendy:"
echo "- Status aplikacji: sudo systemctl status imgw-weather"
echo "- Restart aplikacji: sudo systemctl restart imgw-weather"
echo "- Logi aplikacji: sudo journalctl -u imgw-weather -f"
echo "- Sprawdzenie Nginx: sudo systemctl status nginx"
echo ""
echo "UWAGA: Pamiętaj o:"
echo "1. Zmianie server_name w /etc/nginx/sites-available/imgw-weather"
echo "2. Konfiguracji SSL/HTTPS (np. Let's Encrypt)"
echo "3. Regularne backupy bazy danych SQLite"
echo ""