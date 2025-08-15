// Weather IMGW Application - JavaScript (Completely Fixed)
class WeatherApp {
    constructor() {
        this.weatherData = [
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
                "cisnienie": "1021.8",
                "lat": 53.1325,
                "lon": 23.1688
            },
            {
                "id_stacji": "12600",
                "stacja": "Bielsko Biała",
                "data_pomiaru": "2025-08-13",
                "godzina_pomiaru": "18",
                "temperatura": "22.6",
                "predkosc_wiatru": "2",
                "kierunek_wiatru": "80",
                "wilgotnosc_wzgledna": "60.3",
                "suma_opadu": "0",
                "cisnienie": "1018.4",
                "lat": 49.8224,
                "lon": 19.0444
            },
            {
                "id_stacji": "12235",
                "stacja": "Chojnice",
                "data_pomiaru": "2025-08-13",
                "godzina_pomiaru": "18",
                "temperatura": "23.4",
                "predkosc_wiatru": "1",
                "kierunek_wiatru": "120",
                "wilgotnosc_wzgledna": "48.3",
                "suma_opadu": "0",
                "cisnienie": "1020.1",
                "lat": 53.6983,
                "lon": 17.5583
            },
            {
                "id_stacji": "12550",
                "stacja": "Częstochowa",
                "data_pomiaru": "2025-08-13",
                "godzina_pomiaru": "18",
                "temperatura": "26.2",
                "predkosc_wiatru": "1",
                "kierunek_wiatru": "80",
                "wilgotnosc_wzgledna": "39.0",
                "suma_opadu": "0",
                "cisnienie": "1018.2",
                "lat": 50.8118,
                "lon": 19.1203
            },
            {
                "id_stacji": "12160",
                "stacja": "Elbląg",
                "data_pomiaru": "2025-08-13",
                "godzina_pomiaru": "18",
                "temperatura": "21.4",
                "predkosc_wiatru": "2",
                "kierunek_wiatru": "50",
                "wilgotnosc_wzgledna": "67.2",
                "suma_opadu": "0",
                "cisnienie": "1021.3",
                "lat": 54.1522,
                "lon": 19.4044
            },
            {
                "id_stacji": "12375",
                "stacja": "Warszawa",
                "data_pomiaru": "2025-08-13",
                "godzina_pomiaru": "18",
                "temperatura": "24.8",
                "predkosc_wiatru": "3",
                "kierunek_wiatru": "90",
                "wilgotnosc_wzgledna": "55.2",
                "suma_opadu": "0",
                "cisnienie": "1019.5",
                "lat": 52.2297,
                "lon": 21.0122
            },
            {
                "id_stacji": "12566",
                "stacja": "Kraków",
                "data_pomiaru": "2025-08-13",
                "godzina_pomiaru": "18",
                "temperatura": "25.1",
                "predkosc_wiatru": "2",
                "kierunek_wiatru": "70",
                "wilgotnosc_wzgledna": "52.8",
                "suma_opadu": "0",
                "cisnienie": "1017.9",
                "lat": 50.0647,
                "lon": 19.9450
            },
            {
                "id_stacji": "12115",
                "stacja": "Gdańsk",
                "data_pomiaru": "2025-08-13",
                "godzina_pomiaru": "18",
                "temperatura": "19.5",
                "predkosc_wiatru": "4",
                "kierunek_wiatru": "280",
                "wilgotnosc_wzgledna": "72.1",
                "suma_opadu": "0",
                "cisnienie": "1022.1",
                "lat": 54.3520,
                "lon": 18.6466
            }
        ];
        
        this.map = null;
        this.charts = {};
        this.currentTab = 'dashboard';
        this.filteredData = [...this.weatherData];
        this.sortField = null;
        this.sortDirection = 'asc';
        
        // Wait for DOM to be fully loaded before initializing
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    init() {
        console.log('Initializing Weather App...');
        this.setupEventListeners();
        this.updateDashboardStats();
        
        // Initialize map and charts after a short delay to ensure DOM is ready
        setTimeout(() => {
            this.initializeMap();
            this.initializeCharts();
            this.populateTable();
            this.populateStationSelector();
            this.updateLastRefresh();
            this.startAutoRefresh();
        }, 100);
    }

    setupEventListeners() {
        console.log('Setting up event listeners...');
        
        // Tab navigation
        const navTabs = document.querySelectorAll('.nav-tab');
        navTabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const tabName = tab.getAttribute('data-tab');
                console.log('Tab clicked:', tabName);
                this.switchTab(tabName);
            });
        });

        // Refresh button
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.refreshData();
            });
        }

        // Time range selector
        const timeRange = document.getElementById('timeRange');
        if (timeRange) {
            timeRange.addEventListener('change', (e) => {
                this.handleTimeRangeChange(e.target.value);
            });
        }

        // Search functionality
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterTable(e.target.value);
            });
        }

        // Export functionality
        const exportBtn = document.getElementById('exportBtn');
        if (exportBtn) {
            exportBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.exportToCSV();
            });
        }

        // Table sorting
        const sortHeaders = document.querySelectorAll('.data-table th[data-sort]');
        sortHeaders.forEach(th => {
            th.addEventListener('click', (e) => {
                e.preventDefault();
                const field = th.getAttribute('data-sort');
                this.sortTable(field);
            });
        });

        // Station selector
        const stationSelect = document.getElementById('stationSelect');
        if (stationSelect) {
            stationSelect.addEventListener('change', () => {
                this.updateCharts();
            });
        }
    }

    switchTab(tabName) {
        console.log('Switching to tab:', tabName);
        
        // Remove active class from all tabs
        const allTabs = document.querySelectorAll('.nav-tab');
        allTabs.forEach(tab => tab.classList.remove('active'));
        
        // Add active class to clicked tab
        const activeTab = document.querySelector(`[data-tab="${tabName}"]`);
        if (activeTab) {
            activeTab.classList.add('active');
        }

        // Hide all tab content
        const allContent = document.querySelectorAll('.tab-content');
        allContent.forEach(content => content.classList.remove('active'));
        
        // Show selected tab content
        const activeContent = document.getElementById(tabName);
        if (activeContent) {
            activeContent.classList.add('active');
        }

        this.currentTab = tabName;

        // Handle specific tab requirements
        if (tabName === 'dashboard' && this.map) {
            setTimeout(() => {
                this.map.invalidateSize();
            }, 100);
        } else if (tabName === 'charts') {
            setTimeout(() => {
                this.updateCharts();
            }, 100);
        }
    }

    showLoading() {
        const modal = document.getElementById('loadingModal');
        if (modal) {
            modal.classList.remove('hidden');
        }
    }

    hideLoading() {
        const modal = document.getElementById('loadingModal');
        if (modal) {
            modal.classList.add('hidden');
        }
    }

    async refreshData() {
        this.showLoading();
        
        try {
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // Simulate data changes
            this.weatherData.forEach(station => {
                station.temperatura = (parseFloat(station.temperatura) + (Math.random() - 0.5) * 2).toFixed(1);
                station.wilgotnosc_wzgledna = (parseFloat(station.wilgotnosc_wzgledna) + (Math.random() - 0.5) * 5).toFixed(1);
                station.cisnienie = (parseFloat(station.cisnienie) + (Math.random() - 0.5) * 3).toFixed(1);
            });

            this.filteredData = [...this.weatherData];
            this.updateDashboardStats();
            this.updateMapMarkers();
            this.populateTable();
            this.updateCharts();
            this.updateLastRefresh();
            
        } catch (error) {
            console.error('Error refreshing data:', error);
        } finally {
            this.hideLoading();
        }
    }

    updateLastRefresh() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('pl-PL', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        const lastUpdateEl = document.getElementById('lastUpdate');
        if (lastUpdateEl) {
            lastUpdateEl.textContent = timeString;
        }
    }

    startAutoRefresh() {
        setInterval(() => {
            this.refreshData();
        }, 3600000);
    }

    initializeMap() {
        try {
            const mapElement = document.getElementById('map');
            if (!mapElement) {
                console.error('Map element not found');
                return;
            }

            this.map = L.map('map').setView([52.0, 19.0], 6);

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(this.map);

            this.updateMapMarkers();
            console.log('Map initialized successfully');
        } catch (error) {
            console.error('Error initializing map:', error);
        }
    }

    updateMapMarkers() {
        if (!this.map) return;

        // Clear existing markers
        this.map.eachLayer(layer => {
            if (layer instanceof L.Marker) {
                this.map.removeLayer(layer);
            }
        });

        // Add markers for each station
        this.weatherData.forEach(station => {
            const temp = parseFloat(station.temperatura);
            let markerColor = '#1E40AF';
            
            if (temp >= 30) markerColor = '#EF4444';
            else if (temp >= 25) markerColor = '#F59E0B';
            else if (temp >= 20) markerColor = '#10B981';
            else if (temp >= 15) markerColor = '#0EA5E9';

            const customIcon = L.divIcon({
                className: 'custom-marker',
                html: `<div style="background-color: ${markerColor}; width: 20px; height: 20px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>`,
                iconSize: [20, 20],
                iconAnchor: [10, 10]
            });

            const marker = L.marker([station.lat, station.lon], { icon: customIcon });
            
            const popupContent = `
                <div>
                    <h4>${station.stacja}</h4>
                    <div class="popup-data">
                        <div class="popup-item">
                            <span class="popup-label">Temperatura:</span>
                            <span class="popup-value">${station.temperatura}°C</span>
                        </div>
                        <div class="popup-item">
                            <span class="popup-label">Wilgotność:</span>
                            <span class="popup-value">${station.wilgotnosc_wzgledna}%</span>
                        </div>
                        <div class="popup-item">
                            <span class="popup-label">Ciśnienie:</span>
                            <span class="popup-value">${station.cisnienie} hPa</span>
                        </div>
                        <div class="popup-item">
                            <span class="popup-label">Wiatr:</span>
                            <span class="popup-value">${station.predkosc_wiatru} m/s</span>
                        </div>
                        <div class="popup-item">
                            <span class="popup-label">Opady:</span>
                            <span class="popup-value">${station.suma_opadu} mm</span>
                        </div>
                        <div class="popup-item">
                            <span class="popup-label">Pomiar:</span>
                            <span class="popup-value">${station.godzina_pomiaru}:00</span>
                        </div>
                    </div>
                </div>
            `;

            marker.bindPopup(popupContent);
            marker.addTo(this.map);
        });
    }

    updateDashboardStats() {
        try {
            const temps = this.weatherData.map(s => parseFloat(s.temperatura));
            const humidity = this.weatherData.map(s => parseFloat(s.wilgotnosc_wzgledna));
            const pressure = this.weatherData.map(s => parseFloat(s.cisnienie));

            const avgTemp = (temps.reduce((a, b) => a + b, 0) / temps.length).toFixed(1);
            const avgHumidity = (humidity.reduce((a, b) => a + b, 0) / humidity.length).toFixed(1);
            const avgPressure = (pressure.reduce((a, b) => a + b, 0) / pressure.length).toFixed(1);

            const elements = {
                'avgTemp': `${avgTemp}°C`,
                'avgHumidity': `${avgHumidity}%`,
                'avgPressure': `${avgPressure} hPa`,
                'stationCount': this.weatherData.length
            };

            Object.entries(elements).forEach(([id, value]) => {
                const element = document.getElementById(id);
                if (element) {
                    element.textContent = value;
                }
            });
        } catch (error) {
            console.error('Error updating dashboard stats:', error);
        }
    }

    initializeCharts() {
        try {
            const chartColors = ['#1FB8CD', '#FFC185', '#B4413C', '#ECEBD5', '#5D878F', '#DB4545', '#D2BA4C', '#964325'];
            
            // Temperature Chart
            const tempCtx = document.getElementById('tempChart');
            if (tempCtx) {
                this.charts.temperature = new Chart(tempCtx.getContext('2d'), {
                    type: 'line',
                    data: {
                        labels: this.weatherData.map(s => s.stacja),
                        datasets: [{
                            label: 'Temperatura (°C)',
                            data: this.weatherData.map(s => parseFloat(s.temperatura)),
                            borderColor: chartColors[0],
                            backgroundColor: chartColors[0] + '20',
                            tension: 0.3
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: false,
                                title: {
                                    display: true,
                                    text: 'Temperatura (°C)'
                                }
                            }
                        }
                    }
                });
            }

            // Precipitation Chart
            const precipCtx = document.getElementById('precipChart');
            if (precipCtx) {
                this.charts.precipitation = new Chart(precipCtx.getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: this.weatherData.map(s => s.stacja),
                        datasets: [{
                            label: 'Opady (mm)',
                            data: this.weatherData.map(s => parseFloat(s.suma_opadu)),
                            backgroundColor: chartColors[1]
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: 'Opady (mm)'
                                }
                            }
                        }
                    }
                });
            }

            // Pressure Chart
            const pressureCtx = document.getElementById('pressureChart');
            if (pressureCtx) {
                this.charts.pressure = new Chart(pressureCtx.getContext('2d'), {
                    type: 'line',
                    data: {
                        labels: this.weatherData.map(s => s.stacja),
                        datasets: [{
                            label: 'Ciśnienie (hPa)',
                            data: this.weatherData.map(s => parseFloat(s.cisnienie)),
                            borderColor: chartColors[2],
                            backgroundColor: chartColors[2] + '20',
                            tension: 0.3
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: false,
                                title: {
                                    display: true,
                                    text: 'Ciśnienie (hPa)'
                                }
                            }
                        }
                    }
                });
            }

            // Humidity Chart
            const humidityCtx = document.getElementById('humidityChart');
            if (humidityCtx) {
                this.charts.humidity = new Chart(humidityCtx.getContext('2d'), {
                    type: 'doughnut',
                    data: {
                        labels: this.weatherData.map(s => s.stacja),
                        datasets: [{
                            label: 'Wilgotność (%)',
                            data: this.weatherData.map(s => parseFloat(s.wilgotnosc_wzgledna)),
                            backgroundColor: chartColors
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'bottom'
                            }
                        }
                    }
                });
            }

            console.log('Charts initialized successfully');
        } catch (error) {
            console.error('Error initializing charts:', error);
        }
    }

    updateCharts() {
        try {
            const stationSelect = document.getElementById('stationSelect');
            if (!stationSelect) return;

            const selectedStations = Array.from(stationSelect.selectedOptions)
                .map(option => option.value);
            
            let dataToShow = this.weatherData;
            if (selectedStations.length > 0) {
                dataToShow = this.weatherData.filter(s => selectedStations.includes(s.stacja));
            }

            Object.keys(this.charts).forEach(chartKey => {
                const chart = this.charts[chartKey];
                if (!chart) return;

                chart.data.labels = dataToShow.map(s => s.stacja);
                
                switch(chartKey) {
                    case 'temperature':
                        chart.data.datasets[0].data = dataToShow.map(s => parseFloat(s.temperatura));
                        break;
                    case 'precipitation':
                        chart.data.datasets[0].data = dataToShow.map(s => parseFloat(s.suma_opadu));
                        break;
                    case 'pressure':
                        chart.data.datasets[0].data = dataToShow.map(s => parseFloat(s.cisnienie));
                        break;
                    case 'humidity':
                        chart.data.datasets[0].data = dataToShow.map(s => parseFloat(s.wilgotnosc_wzgledna));
                        break;
                }
                
                chart.update();
            });
        } catch (error) {
            console.error('Error updating charts:', error);
        }
    }

    populateStationSelector() {
        try {
            const select = document.getElementById('stationSelect');
            if (!select) return;

            select.innerHTML = '';
            
            this.weatherData.forEach(station => {
                const option = document.createElement('option');
                option.value = station.stacja;
                option.textContent = station.stacja;
                select.appendChild(option);
            });
        } catch (error) {
            console.error('Error populating station selector:', error);
        }
    }

    populateTable() {
        try {
            const tbody = document.getElementById('tableBody');
            if (!tbody) return;

            tbody.innerHTML = '';

            this.filteredData.forEach(station => {
                const row = document.createElement('tr');
                
                row.innerHTML = `
                    <td>${station.stacja}</td>
                    <td class="${this.getTemperatureClass(station.temperatura)}">${station.temperatura}°C</td>
                    <td>${station.wilgotnosc_wzgledna}%</td>
                    <td>${station.cisnienie} hPa</td>
                    <td>${station.predkosc_wiatru} m/s</td>
                    <td>${station.suma_opadu} mm</td>
                    <td>${station.data_pomiaru} ${station.godzina_pomiaru}:00</td>
                `;
                
                tbody.appendChild(row);
            });
        } catch (error) {
            console.error('Error populating table:', error);
        }
    }

    getTemperatureClass(temp) {
        const temperature = parseFloat(temp);
        if (temperature >= 30) return 'temp-hot';
        if (temperature >= 25) return 'temp-warm';
        if (temperature >= 20) return 'temp-mild';
        if (temperature >= 15) return 'temp-cool';
        return 'temp-cold';
    }

    filterTable(searchTerm) {
        this.filteredData = this.weatherData.filter(station => 
            station.stacja.toLowerCase().includes(searchTerm.toLowerCase())
        );
        this.populateTable();
    }

    sortTable(field) {
        if (this.sortField === field) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortField = field;
            this.sortDirection = 'asc';
        }

        // Update sort indicators
        document.querySelectorAll('.data-table th').forEach(th => {
            th.classList.remove('sorted');
        });
        const sortedHeader = document.querySelector(`th[data-sort="${field}"]`);
        if (sortedHeader) {
            sortedHeader.classList.add('sorted');
        }

        // Sort data
        this.filteredData.sort((a, b) => {
            let aVal = a[field];
            let bVal = b[field];

            if (!isNaN(parseFloat(aVal))) {
                aVal = parseFloat(aVal);
                bVal = parseFloat(bVal);
            }

            if (this.sortDirection === 'asc') {
                return aVal > bVal ? 1 : -1;
            } else {
                return aVal < bVal ? 1 : -1;
            }
        });

        this.populateTable();
    }

    exportToCSV() {
        try {
            const headers = ['Stacja', 'Temperatura', 'Wilgotność', 'Ciśnienie', 'Wiatr', 'Opady', 'Data pomiaru'];
            const csvContent = [
                headers.join(','),
                ...this.filteredData.map(station => [
                    `"${station.stacja}"`,
                    station.temperatura,
                    station.wilgotnosc_wzgledna,
                    station.cisnienie,
                    station.predkosc_wiatru,
                    station.suma_opadu,
                    `"${station.data_pomiaru} ${station.godzina_pomiaru}:00"`
                ].join(','))
            ].join('\n');

            const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', `dane_pogodowe_${new Date().toISOString().split('T')[0]}.csv`);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Error exporting CSV:', error);
        }
    }

    handleTimeRangeChange(range) {
        console.log('Time range changed to:', range);
        this.updateDashboardStats();
        this.updateCharts();
        this.populateTable();
    }
}

// Initialize the application
new WeatherApp();