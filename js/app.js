class Application {
    constructor() {
        this.activeCycloneId = 'live_telemetry';
        this.activeTab = 'impact';
        this.selectedLocation = null;
        this.state = {
            cyclones: [],
            activeCyclone: null,
            riskData: null,
            infraData: null,
            exposedData: null,
            simData: null,
            liveWeather: null,
            liveStatus: null
        };
        this.chatMessages = [];
        this.mapController = null;
        this.contextPanelOpen = false;
        this.init();
    }

    async init() {
        console.log('Application initializing...');
        try {
            this.initTheme();
            this.triggerCycloneArrivalIntro();
            this.mapController = new MapController('command-map');
            this.mapController.onMapClickCallback = (lat, lon) => this.handleMapClickTelemetry(lat, lon);
            this.bindEvents();
            await this.loadInitialData();
            this.initLiveStream();
            console.log('Application initialized successfully');
        } catch (error) {
            console.error('Initialization error:', error);
            this.showError('Failed to initialize application. Please refresh the page.');
        }
    }

    triggerCycloneArrivalIntro() {
        const overlay = document.getElementById('cyclone-arrival-overlay');
        if (overlay) {
            setTimeout(() => {
                overlay.classList.add('fade-out');
                setTimeout(() => {
                    overlay.remove();
                }, 850);
            }, 1800);
        }
    }

    initLiveStream() {
        console.log('Initializing SSE live stream...');
        ApiClient.subscribeLiveStream(
            (message) => this.handleLiveStateUpdate(message),
            (error) => console.error('SSE Error:', error)
        );
    }

    handleLiveStateUpdate(liveData) {
        console.log('Live state update received:', liveData);
        
        const badge = document.getElementById('live-mode-badge');
        const stormName = document.getElementById('left-storm-name');
        const stormStatus = document.getElementById('left-storm-status');

        if (badge) {
            if (this.activeCycloneId === 'live_telemetry') {
                if (liveData.cyclone && liveData.cyclone.has_active) {
                    badge.innerHTML = `
                        <span class="live-green-signal">
                            <span class="signal-ring"></span>
                            <span class="signal-core"></span>
                        </span>
                        <span class="monitoring-label">LIVE · ${liveData.cyclone.name || 'ACTIVE STORM'}</span>
                    `;
                    if (stormName) stormName.textContent = `Cyclone ${liveData.cyclone.name || 'Unknown'}`;
                    if (stormStatus) {
                        stormStatus.textContent = 'ACTIVE';
                        stormStatus.style.color = 'var(--risk-high)';
                    }
                } else {
                    badge.innerHTML = `
                        <span class="live-green-signal">
                            <span class="signal-ring"></span>
                            <span class="signal-core"></span>
                        </span>
                        <span class="monitoring-label">MONITORING</span>
                    `;
                    if (stormName) stormName.textContent = 'No active cyclone';
                    if (stormStatus) {
                        stormStatus.textContent = 'Monitoring';
                        stormStatus.style.color = 'var(--risk-mod)';
                    }
                }
            } else {
                badge.innerHTML = `
                    <span class="live-green-signal historical">
                        <span class="signal-core" style="background:#f59e0b; box-shadow:0 0 8px #f59e0b;"></span>
                    </span>
                    <span class="monitoring-label" style="color:#f59e0b;">HISTORICAL SCENARIO</span>
                `;
            }
        }

        if (liveData.weather) {
            this.state.liveWeather = liveData.weather;
            this.updateWeatherDisplay(liveData.weather);
        }

        if (liveData.risk) {
            this.state.riskData = liveData.risk;
            this.updateDashboardMetrics(liveData.risk);
            this.updateRiskAnalysisSection(liveData.risk);
        }

        if (liveData.infrastructure) {
            this.state.infraData = liveData.infrastructure;
            this.updateInfrastructureCounts(liveData.infrastructure);
        }

        const timestampInd = document.getElementById('last-updated-time');
        if (timestampInd) {
            const now = new Date();
            timestampInd.textContent = `${now.toLocaleTimeString()} IST`;
        }
    }

    bindEvents() {
        // Tab navigation for right dock panel (supports both .dock-tab and .nav-tab)
        document.querySelectorAll('.dock-tab, .nav-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                const tabId = e.currentTarget.getAttribute('data-tab');
                if (tabId) this.switchTab(tabId);
            });
        });

        // Toggle Left Situation HUD
        const btnToggleLeft = document.getElementById('btn-toggle-left-hud');
        if (btnToggleLeft) {
            btnToggleLeft.addEventListener('click', () => {
                const leftPanel = document.getElementById('left-panel');
                if (leftPanel) {
                    leftPanel.classList.toggle('collapsed');
                    btnToggleLeft.classList.toggle('active');
                    setTimeout(() => {
                        if (this.mapController && this.mapController.map) {
                            this.mapController.map.invalidateSize();
                        }
                    }, 350);
                }
            });
        }

        // Toggle Right AI Intelligence Dock
        const btnToggleRight = document.getElementById('btn-toggle-ai-dock');
        if (btnToggleRight) {
            btnToggleRight.addEventListener('click', () => {
                const rightDock = document.getElementById('right-intelligence-dock');
                if (rightDock) {
                    rightDock.classList.toggle('collapsed');
                    btnToggleRight.classList.toggle('active');
                    setTimeout(() => {
                        if (this.mapController && this.mapController.map) {
                            this.mapController.map.invalidateSize();
                        }
                    }, 350);
                }
            });
        }

        // Toggle Theme (Light / Dark mode)
        const btnToggleTheme = document.getElementById('btn-toggle-theme');
        if (btnToggleTheme) {
            btnToggleTheme.addEventListener('click', () => this.toggleTheme());
        }

        // Quick Prompt Chips in AI Dock
        document.querySelectorAll('.prompt-chip').forEach(chip => {
            chip.addEventListener('click', (e) => {
                const promptText = e.currentTarget.getAttribute('data-prompt');
                const chatInput = document.getElementById('chat-input');
                if (chatInput && promptText) {
                    chatInput.value = promptText;
                    this.handleAIChat();
                }
            });
        });

        // Cyclone selector
        const selector = document.getElementById('cyclone-selector');
        if (selector) {
            selector.addEventListener('change', (e) => {
                this.loadCycloneDetails(e.target.value);
            });
        }

        // Basemap switcher
        const baseMapSel = document.getElementById('basemap-selector');
        if (baseMapSel) {
            baseMapSel.addEventListener('change', (e) => {
                if (this.mapController) {
                    this.mapController.switchBaseLayer(e.target.value);
                }
            });
        }

        // Multi-language switcher
        const langSel = document.getElementById('lang-selector');
        if (langSel) {
            if (window.i18n) {
                langSel.value = window.i18n.currentLang;
                window.i18n.applyTranslations();
            }
            langSel.addEventListener('change', (e) => {
                if (window.i18n) {
                    window.i18n.setLanguage(e.target.value);
                }
            });
        }

        // Region selector (All India, East Coast, West Coast, Global)
        const regionSel = document.getElementById('region-selector');
        if (regionSel) {
            regionSel.addEventListener('change', async (e) => {
                if (this.mapController) {
                    const target = this.mapController.focusRegion(e.target.value);
                    const stormLoc = document.getElementById('left-storm-loc');
                    if (stormLoc && target) stormLoc.textContent = target.label;
                    
                    // Fetch live weather for selected region center
                    if (target && target.center) {
                        try {
                            const weather = await ApiClient.getLiveWeather(target.center[0], target.center[1]);
                            this.state.liveWeather = weather;
                            this.updateWeatherDisplay(weather);
                        } catch(err) {
                            console.warn("Region weather update note:", err);
                        }
                    }
                }
            });
        }

        // Clear location button
        const clearBtn = document.getElementById('btn-clear-location');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearSelectedLocation());
        }

        // Location search form (e.g. Mumbai, Chennai, Kolkata, Delhi, Jaipur)
        const searchForm = document.getElementById('location-search-form');
        if (searchForm) {
            searchForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const searchInput = document.getElementById('location-search-input');
                if (searchInput && searchInput.value.trim() && this.mapController) {
                    this.showLoading(true);
                    try {
                        const loc = await this.mapController.searchLocation(searchInput.value.trim());
                        if (loc) {
                            await this.handleMapClickTelemetry(loc.lat, loc.lon);
                        }
                    } catch(err) {
                        console.warn("Location search note:", err);
                    } finally {
                        this.showLoading(false);
                    }
                }
            });
        }

        // Layer toggles
        const toggles = [
            { id: 'toggle-hospitals', key: 'hospitals' },
            { id: 'toggle-shelters', key: 'shelters' },
            { id: 'toggle-power', key: 'power' },
            { id: 'toggle-roads', key: 'roads' }
        ];
        toggles.forEach(t => {
            const el = document.getElementById(t.id);
            if (el) {
                el.addEventListener('change', (e) => {
                    this.mapController.toggleLayerGroup(t.key, e.target.checked);
                });
            }
        });

        // Simulation sliders
        const sliders = ['wind', 'rain', 'shift'];
        sliders.forEach(s => {
            const slider = document.getElementById(`slider-${s}`);
            const valDisplay = document.getElementById(`val-${s}`);
            if (slider && valDisplay) {
                slider.addEventListener('input', (e) => {
                    valDisplay.textContent = (e.target.value > 0 ? '+' : '') + e.target.value + (s === 'shift' ? ' km' : s === 'rain' ? '%' : ' kts');
                });
            }
        });

        // Simulation button
        const simBtn = document.getElementById('btn-run-sim');
        if (simBtn) {
            simBtn.addEventListener('click', () => this.runSimulation());
        }

        // AI chat form
        const chatForm = document.getElementById('ai-chat-form');
        if (chatForm) {
            chatForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleAIChat();
            });
        }

        // Download advisory
        const downloadBtn = document.getElementById('btn-download-advisory');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => this.downloadAdvisoryMarkdown());
        }

        // Context panel close
        const closeBtn = document.getElementById('context-panel-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.closeContextPanel());
        }
        
        // Window resize
        window.addEventListener('resize', () => {
            if (this.mapController && this.mapController.map) {
                this.mapController.map.invalidateSize();
            }
        });
    }

    switchTab(tabId) {
        this.activeTab = tabId;

        // Auto-uncollapse right intelligence dock when switching tabs
        const rightDock = document.getElementById('right-intelligence-dock');
        const btnToggleRight = document.getElementById('btn-toggle-ai-dock');
        if (rightDock) {
            rightDock.classList.remove('collapsed');
            rightDock.classList.add('open');
            if (btnToggleRight) btnToggleRight.classList.add('active');
            setTimeout(() => {
                if (this.mapController && this.mapController.map) {
                    this.mapController.map.invalidateSize();
                }
            }, 300);
        }
        
        // Update dock-tab & nav-tab active states
        document.querySelectorAll('.dock-tab, .nav-tab').forEach(tab => {
            if (tab.getAttribute('data-tab') === tabId) {
                tab.classList.add('active');
            } else {
                tab.classList.remove('active');
            }
        });

        // Show/hide tab-views
        document.querySelectorAll('.tab-view').forEach(panel => {
            if (panel.id === `tab-${tabId}`) {
                panel.classList.add('active');
            } else {
                panel.classList.remove('active');
            }
        });

        if (tabId === 'advisory') {
            this.loadEmergencyAdvisory();
        } else if (tabId === 'impact' || tabId === 'risk') {
            if (this.state.riskData) {
                this.updateRiskAnalysisSection(this.state.riskData);
            }
        }
    }

    toggleTheme() {
        const isLight = document.body.classList.toggle('light-theme');
        const themeIcon = document.getElementById('theme-icon');
        const themeText = document.getElementById('theme-text');
        const currentTheme = isLight ? 'light' : 'dark';

        if (themeIcon) themeIcon.textContent = isLight ? '🌙' : '☀️';
        if (themeText) themeText.textContent = isLight ? 'Dark Mode' : 'Light Mode';

        localStorage.setItem('cycloneshield_theme', currentTheme);
    }

    initTheme() {
        const savedTheme = localStorage.getItem('cycloneshield_theme');
        if (savedTheme === 'light') {
            document.body.classList.add('light-theme');
            const themeIcon = document.getElementById('theme-icon');
            const themeText = document.getElementById('theme-text');
            if (themeIcon) themeIcon.textContent = '🌙';
            if (themeText) themeText.textContent = 'Dark Mode';
        }
    }

    async loadInitialData() {
        this.showLoading(true);
        try {
            this.state.cyclones = await ApiClient.getCyclones();
            this.populateCycloneSelector();
            
            const infra = await ApiClient.getInfrastructure();
            this.mapController.renderInfrastructure(infra);
            this.updateInfrastructureCounts(infra);

            await this.loadCycloneDetails(this.activeCycloneId);
        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.showError('Could not load initial dashboard data.');
        } finally {
            this.showLoading(false);
        }
    }

    populateCycloneSelector() {
        const selector = document.getElementById('cyclone-selector');
        if (!selector) return;

        selector.innerHTML = '';
        
        const liveGroup = document.createElement('optgroup');
        liveGroup.label = 'LIVE TELEMETRY';
        const liveOpt = document.createElement('option');
        liveOpt.value = 'live_telemetry';
        liveOpt.textContent = '● Live Monitoring';
        liveGroup.appendChild(liveOpt);
        selector.appendChild(liveGroup);

        const histGroup = document.createElement('optgroup');
        histGroup.label = 'HISTORICAL SCENARIOS';
        this.state.cyclones.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c.cyclone_id;
            opt.textContent = `${c.name} (${c.year})`;
            histGroup.appendChild(opt);
        });
        selector.appendChild(histGroup);

        selector.value = this.activeCycloneId;
    }

    async loadCycloneDetails(cycloneId) {
        this.showLoading(true);
        this.activeCycloneId = cycloneId;
        const stormName = document.getElementById('left-storm-name');
        const stormStatus = document.getElementById('left-storm-status');
        const stormLoc = document.getElementById('left-storm-loc');
        
        try {
            if (cycloneId === 'live_telemetry') {
                await ApiClient.setLiveMode('LIVE');
                const status = await ApiClient.getLiveStatus();
                this.state.liveStatus = status;

                if (status.cyclone && status.cyclone.has_active && status.cyclone.geojson_track) {
                    this.state.activeCyclone = status.cyclone;
                    this.mapController.renderCycloneTrack(status.cyclone.geojson_track);
                    if(stormName) stormName.textContent = `Cyclone ${status.cyclone.name}`;
                    if(stormStatus) {
                        stormStatus.textContent = 'ACTIVE';
                        stormStatus.style.color = 'var(--risk-high)';
                    }
                } else {
                    this.state.activeCyclone = null;
                    this.mapController.renderMonitoringMode();
                    if(stormName) stormName.textContent = `No active cyclone`;
                    if(stormStatus) {
                        stormStatus.textContent = 'Monitoring';
                        stormStatus.style.color = 'var(--risk-mod)';
                    }
                }

                const liveRisk = await ApiClient.getLiveRisk();
                this.state.riskData = liveRisk;
                
                const liveInfra = await ApiClient.getLiveInfrastructure();
                if (liveInfra) {
                    this.state.exposedData = liveInfra;
                }
                
                const lat = status.cyclone && status.cyclone.has_active ? status.cyclone.lat : 15;
                const lon = status.cyclone && status.cyclone.has_active ? status.cyclone.lon : 85;
                
                try {
                    const weather = await ApiClient.getLiveWeather(lat, lon);
                    this.state.liveWeather = weather;
                    this.updateWeatherDisplay(weather);
                } catch(e) {
                    console.error("Live weather failed", e);
                }

            } else {
                await ApiClient.setLiveMode('DEMO');
                const cyclone = await ApiClient.getCycloneById(cycloneId);
                this.state.activeCyclone = cyclone;
                
                if(stormName) stormName.textContent = `Cyclone ${cyclone.name}`;
                if(stormStatus) {
                    stormStatus.textContent = 'HISTORICAL';
                    stormStatus.style.color = 'var(--text-muted)';
                }
                if(stormLoc) stormLoc.textContent = `${cyclone.basin} (${cyclone.year})`;

                if (cyclone.geojson_track) {
                    this.mapController.renderCycloneTrack(cyclone.geojson_track);
                }
                
                const risk = await ApiClient.calculateForecast({ cyclone_id: cycloneId, buffer_km: 100 });
                this.state.riskData = risk;
                
                const exposed = await ApiClient.getExposedInfrastructure(cycloneId, 100);
                this.state.exposedData = exposed;
                
                this.updateWeatherDisplay(null);
            }

            if (this.state.riskData) {
                this.updateDashboardMetrics(this.state.riskData);
                this.updateRiskAnalysisSection(this.state.riskData);
            }
            if (this.state.exposedData) {
                // this.renderExposedInfrastructureTable(this.state.exposedData);
            }
            
        } catch (error) {
            console.error('Failed to load cyclone details:', error);
            this.showError('Could not load scenario details.');
        } finally {
            this.showLoading(false);
            if (this.mapController && this.mapController.map) {
                this.mapController.map.invalidateSize();
            }
        }
    }

    async handleMapClickTelemetry(lat, lon) {
        this.showLoading(true);
        try {
            // Set target marker pin
            if (this.mapController) {
                this.mapController.setTargetLocation(lat, lon);
            }

            // Call Location Analysis API
            const analysis = await ApiClient.analyzeLocation(lat, lon);
            this.selectedLocation = analysis;

            const loc = analysis.location;
            const weather = analysis.weather;
            const risk = analysis.risk;
            const infra = analysis.infrastructure;

            // 1. Update Left HUD Header
            const modeLabel = document.getElementById('left-hud-mode-label');
            const stormName = document.getElementById('left-storm-name');
            const stormLoc = document.getElementById('left-storm-loc');
            const stormStatus = document.getElementById('left-storm-status');
            const clearBtn = document.getElementById('btn-clear-location');

            if (modeLabel) modeLabel.textContent = 'SELECTED LOCATION';
            if (stormName) stormName.textContent = `${loc.name}, ${loc.state}`;
            if (stormLoc) stormLoc.textContent = `Lat: ${loc.latitude.toFixed(2)}°, Lon: ${loc.longitude.toFixed(2)}°`;
            if (stormStatus) {
                stormStatus.textContent = 'SELECTED';
                stormStatus.style.color = 'var(--accent-blue)';
            }
            if (clearBtn) clearBtn.style.display = 'inline-block';

            // 2. Update Risk Gauge
            const scoreEl = document.getElementById('kpi-score');
            const badgeEl = document.getElementById('kpi-badge');
            if (scoreEl) scoreEl.textContent = risk.score;
            if (badgeEl) {
                badgeEl.textContent = risk.level;
                badgeEl.className = 'risk-category-badge ' + (
                    risk.level === 'EXTREME' ? 'ext' :
                    risk.level === 'HIGH' ? 'high' :
                    risk.level === 'MODERATE' ? 'mod' : 'low'
                );
            }

            // 3. Update Weather Telemetry Tiles
            this.updateWeatherDisplay({
                temperature_c: weather.temperature,
                wind_speed_kmh: weather.wind_speed,
                wind_speed_knots: weather.wind_speed_knots,
                surface_pressure_hpa: weather.pressure,
                projected_rainfall_mm: weather.rainfall
            });

            // 4. Update Infrastructure Exposure Counts
            const eTotal = document.getElementById('kpi-infra');
            const eH = document.getElementById('exp-count-hospitals');
            const eS = document.getElementById('exp-count-shelters');
            const eP = document.getElementById('exp-count-power');
            const eR = document.getElementById('exp-count-roads');

            if (eTotal) eTotal.textContent = infra.total_exposed;
            if (eH) eH.textContent = infra.hospitals;
            if (eS) eS.textContent = infra.shelters;
            if (eP) eP.textContent = infra.power;
            if (eR) eR.textContent = infra.transport;

            // Also update Right Intelligence Drawer Infra Tab
            const tiH = document.getElementById('tab-infra-hospitals');
            const tiS = document.getElementById('tab-infra-shelters');
            const tiP = document.getElementById('tab-infra-power');
            const tiT = document.getElementById('tab-infra-transport');

            if (tiH) tiH.textContent = infra.hospitals;
            if (tiS) tiS.textContent = infra.shelters;
            if (tiP) tiP.textContent = infra.power;
            if (tiT) tiT.textContent = infra.transport;

        } catch (error) {
            console.error("Failed to execute location analysis:", error);
        } finally {
            this.showLoading(false);
        }
    }

    clearSelectedLocation() {
        this.selectedLocation = null;

        if (this.mapController) {
            this.mapController.clearTargetLocation();
        }

        const modeLabel = document.getElementById('left-hud-mode-label');
        const stormName = document.getElementById('left-storm-name');
        const stormLoc = document.getElementById('left-storm-loc');
        const stormStatus = document.getElementById('left-storm-status');
        const clearBtn = document.getElementById('btn-clear-location');

        if (modeLabel) modeLabel.textContent = 'CYCLONE STATUS';
        if (stormName) stormName.textContent = 'No active cyclone';
        if (stormLoc) stormLoc.textContent = 'India-Wide Monitoring Mode';
        if (stormStatus) {
            stormStatus.textContent = 'Monitoring';
            stormStatus.style.color = 'var(--risk-mod)';
        }
        if (clearBtn) clearBtn.style.display = 'none';

        // Reset to initial baseline telemetry
        if (this.state.riskData) {
            this.updateDashboardMetrics(this.state.riskData);
        }
        if (this.state.liveWeather) {
            this.updateWeatherDisplay(this.state.liveWeather);
        }
        if (this.state.infraData) {
            this.updateInfrastructureCounts(this.state.infraData);
        }
    }

    updateWeatherDisplay(weatherData) {
        const els = {
            temp: document.getElementById('weather-temp'),
            wind: document.getElementById('weather-wind'),
            pressure: document.getElementById('weather-pressure'),
            rain: document.getElementById('weather-rain')
        };
        
        if (weatherData) {
            const w = weatherData.weather || weatherData;
            
            const tempVal = w.temperature_c ?? w.temperature;
            const windVal = w.wind_speed_knots ?? w.wind_speed;
            const pressureVal = w.surface_pressure_hpa ?? w.pressure;
            const rainVal = w.projected_rainfall_mm ?? w.rainfall;

            if (els.temp) els.temp.textContent = (tempVal !== undefined && tempVal !== null) ? `${tempVal}°C` : '--';
            if (els.wind) els.wind.textContent = (windVal !== undefined && windVal !== null) ? `${windVal} kts` : '--';
            if (els.pressure) els.pressure.textContent = (pressureVal !== undefined && pressureVal !== null) ? `${pressureVal} hPa` : '--';
            if (els.rain) els.rain.textContent = (rainVal !== undefined && rainVal !== null) ? `${rainVal} mm` : '--';
        } else {
            Object.values(els).forEach(el => {
                if (el) el.textContent = '--';
            });
        }
    }

    updateDashboardMetrics(risk) {
        const scoreEl = document.getElementById('kpi-score');
        const badgeEl = document.getElementById('kpi-badge');
        const infraEl = document.getElementById('kpi-infra');

        if (scoreEl) scoreEl.textContent = risk.vulnerability_score || 0;
        
        if (badgeEl) {
            badgeEl.textContent = risk.risk_category || 'UNKNOWN';
            badgeEl.className = 'text-low';
            if (risk.risk_category === 'EXTREME') badgeEl.className = 'text-ext';
            else if (risk.risk_category === 'HIGH') badgeEl.className = 'text-high';
            else if (risk.risk_category === 'MODERATE') badgeEl.className = 'text-mod';
        }

        if (infraEl && risk.infrastructure_summary) {
            infraEl.textContent = risk.infrastructure_summary.total_exposed || 0;
        }
    }

    updateInfrastructureCounts(infra) {
        if (!infra || !infra.features) return;
        
        const counts = { hospital: 0, shelter: 0, power: 0, road: 0 };
        infra.features.forEach(f => {
            const cat = (f.properties.category || '').toLowerCase();
            if (counts[cat] !== undefined) counts[cat]++;
            else if (cat.includes('hospital')) counts['hospital']++;
        });

        const eH = document.getElementById('exp-count-hospitals');
        const eS = document.getElementById('exp-count-shelters');
        const eP = document.getElementById('exp-count-power');
        const eR = document.getElementById('exp-count-roads');

        if(eH) eH.textContent = counts.hospital;
        if(eS) eS.textContent = counts.shelter;
        if(eP) eP.textContent = counts.power;
        if(eR) eR.textContent = counts.road;

        const tiH = document.getElementById('tab-infra-hospitals');
        const tiS = document.getElementById('tab-infra-shelters');
        const tiP = document.getElementById('tab-infra-power');
        const tiT = document.getElementById('tab-infra-transport');

        if(tiH) tiH.textContent = counts.hospital;
        if(tiS) tiS.textContent = counts.shelter;
        if(tiP) tiP.textContent = counts.power;
        if(tiT) tiT.textContent = counts.road;
    }

    updateRiskAnalysisSection(risk) {
        if (risk && risk.hazard_breakdown) {
            ChartController.initRadarChart('hazard-radar-chart', risk.hazard_breakdown);
        }
    }

    async runSimulation() {
        const windSlider = document.getElementById('slider-wind');
        const rainSlider = document.getElementById('slider-rain');
        const shiftSlider = document.getElementById('slider-shift');

        const deltaWind = windSlider ? parseFloat(windSlider.value) : 0;
        const deltaRain = rainSlider ? parseFloat(rainSlider.value) : 0;
        const shiftDist = shiftSlider ? parseFloat(shiftSlider.value) : 0;

        const cycloneId = (this.activeCycloneId && this.activeCycloneId !== 'live_telemetry') ? this.activeCycloneId : 'amphan_2020';

        const params = {
            cyclone_id: cycloneId,
            delta_wind_knots: deltaWind,
            delta_rainfall_percent: deltaRain,
            shift_direction: 'EAST',
            shift_distance_km: shiftDist
        };

        this.showLoading(true);
        try {
            const result = await ApiClient.runSimulation(params);
            this.state.simData = result;
            this.renderSimulationResults(result);
        } catch (error) {
            console.error('Simulation API call note:', error);
            const baseScore = (this.selectedLocation && this.selectedLocation.risk) ? this.selectedLocation.risk.score : 45;
            const simScore = Math.min(100, Math.max(0, Math.round(baseScore + (deltaWind * 0.4) + (deltaRain * 0.3) + (shiftDist * 0.2))));
            const deltaScore = Math.round(simScore - baseScore);
            const simLevel = simScore >= 75 ? 'EXTREME' : simScore >= 50 ? 'HIGH' : simScore >= 25 ? 'MODERATE' : 'LOW';

            this.renderSimulationResults({
                simulated: { vulnerability_score: simScore, risk_category: simLevel },
                delta: { score_delta: deltaScore },
                gemini_explanation: `**What-If Scenario Simulation Projections**:\n- **Wind Speed Adjustment**: ${deltaWind > 0 ? '+' : ''}${deltaWind} kts\n- **Rainfall Severity**: ${deltaRain > 0 ? '+' : ''}${deltaRain}%\n- **Track Shift**: ${shiftDist} km\n- **Simulated Risk Score**: ${simScore} / 100 (${simLevel})\n- **Score Delta**: ${deltaScore > 0 ? '+' : ''}${deltaScore} points.`
            });
        } finally {
            this.showLoading(false);
        }
    }

    renderSimulationResults(sim) {
        if (!sim) return;

        // Status badge
        const simBadge = document.getElementById('sim-sim-badge');
        if(simBadge) simBadge.textContent = 'Simulated Result';

        // Simulated Score
        const simScore = document.getElementById('sim-sim-score');
        const deltaBadge = document.getElementById('sim-delta-badge');

        if (simScore) simScore.textContent = sim.simulated.vulnerability_score;

        if (deltaBadge && sim.delta) {
            const delta = sim.delta.score_delta;
            deltaBadge.textContent = `${delta > 0 ? '+' : ''}${delta}`;
            deltaBadge.style.color = delta > 0 ? 'var(--risk-high)' : 'var(--risk-low)';
        }

        // AI Explanation box
        const aiBox = document.getElementById('sim-ai-explanation-box');
        if (aiBox) {
            aiBox.innerHTML = `<p>${(sim.gemini_explanation || 'Scenario calculated.').replace(/\n/g, '<br/>')}</p>`;
        }
    }

    formatMarkdown(text) {
        if (!text) return '';
        
        let html = text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

        // Risk / Alert Tag Highlights
        html = html.replace(/\[(EXTREME RISK|EXTREME|SUPER CYCLONE)\]/gi, '<span class="ai-tag tag-ext">$1</span>');
        html = html.replace(/\[(HIGH RISK|HIGH|MANDATORY EVACUATION)\]/gi, '<span class="ai-tag tag-high">$1</span>');
        html = html.replace(/\[(MODERATE RISK|MODERATE|MONITORING)\]/gi, '<span class="ai-tag tag-mod">$1</span>');
        html = html.replace(/\[(LOW RISK|SAFE|NORMAL)\]/gi, '<span class="ai-tag tag-low">$1</span>');

        // Headers: ### Header, ## Header, # Header
        html = html.replace(/^### (.*$)/gim, '<h4 class="ai-h3">$1</h4>');
        html = html.replace(/^## (.*$)/gim, '<h3 class="ai-h2">$1</h3>');
        html = html.replace(/^# (.*$)/gim, '<h2 class="ai-h1">$1</h2>');

        // Bold & Italic
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

        // Numbered lists
        html = html.replace(/^\d+\.\s+(.*$)/gim, '<li class="ai-num-item">$1</li>');

        // Bullet lists
        html = html.replace(/^[\-*]\s+(.*$)/gim, '<li class="ai-bullet-item">$1</li>');

        // Wrap list items
        html = html.replace(/(<li class="ai-bullet-item">.*?<\/li>)+/g, '<ul class="ai-list">$&</ul>');
        html = html.replace(/(<li class="ai-num-item">.*?<\/li>)+/g, '<ol class="ai-list-num">$&</ol>');

        // Paragraphs & Line breaks
        const lines = html.split(/\n\n+/);
        html = lines.map(line => {
            if (line.startsWith('<h') || line.startsWith('<ul') || line.startsWith('<ol')) {
                return line;
            }
            return `<p>${line.replace(/\n/g, '<br>')}</p>`;
        }).join('');

        return html;
    }

    async handleAIChat() {
        const inputEl = document.getElementById('chat-input');
        const historyEl = document.getElementById('chat-history');
        if (!inputEl || !historyEl) return;

        const query = inputEl.value.trim();
        if (!query) return;

        inputEl.value = '';
        
        const now = new Date();
        const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        // Add user message card
        const userMsgHtml = `
            <div class="ai-msg-card user">
                <div class="msg-header">
                    <span class="sender-name">You</span>
                    <span class="msg-time">${timeStr}</span>
                    <div class="avatar-badge user">👤</div>
                </div>
                <div class="msg-body">
                    <p>${this.escapeHtml(query)}</p>
                </div>
            </div>
        `;
        historyEl.innerHTML += userMsgHtml;
        this.chatMessages.push({ role: 'user', content: query });
        
        const loaderId = 'chat-loader-' + Date.now();
        const thinkingHtml = `
            <div id="${loaderId}" class="ai-msg-card system thinking">
                <div class="msg-header">
                    <div class="avatar-badge pulsing">✨</div>
                    <span class="sender-name">CycloneShield AI</span>
                    <span class="msg-time">Analyzing Telemetry...</span>
                </div>
                <div class="msg-body">
                    <div class="typing-indicator">
                        <span></span><span></span><span></span>
                    </div>
                </div>
            </div>
        `;
        historyEl.innerHTML += thinkingHtml;
        historyEl.scrollTop = historyEl.scrollHeight;

        const selectedLang = window.i18n ? window.i18n.getLangName() : 'English';
        const context = {
            selectedLocation: this.selectedLocation ? {
                name: this.selectedLocation.location.name,
                state: this.selectedLocation.location.state,
                latitude: this.selectedLocation.location.latitude,
                longitude: this.selectedLocation.location.longitude,
                weather: this.selectedLocation.weather,
                risk: this.selectedLocation.risk,
                infrastructure: this.selectedLocation.infrastructure,
                cyclone: this.selectedLocation.cyclone
            } : null,
            mode: this.selectedLocation ? "SELECTED_LOCATION" : "INDIA_WIDE_MONITORING",
            cycloneId: this.activeCycloneId,
            riskData: this.state.riskData,
            weather: this.state.liveWeather,
            languageInstruction: `IMPORTANT: Please answer the user's question clearly in ${selectedLang} language.`
        };

        try {
            const resp = await ApiClient.chatAssistant({
                query: query,
                context: context,
                history: this.chatMessages
            });

            const loaderEl = document.getElementById(loaderId);
            if (loaderEl) loaderEl.remove();

            const rawAnswer = resp.answer || 'I am unable to analyze the data right now.';
            const formattedHtml = this.formatMarkdown(rawAnswer);
            const aiMsgId = 'ai-msg-' + Date.now();

            const aiMsgHtml = `
                <div id="${aiMsgId}" class="ai-msg-card system">
                    <div class="msg-header">
                        <div class="avatar-badge">✨</div>
                        <span class="sender-name">CycloneShield AI</span>
                        <span class="msg-time">${timeStr}</span>
                    </div>
                    <div class="msg-body">
                        ${formattedHtml}
                    </div>
                </div>
            `;
            historyEl.innerHTML += aiMsgHtml;
            this.chatMessages.push({ role: 'assistant', content: rawAnswer });

        } catch (error) {
            console.error('Chat error:', error);
            const loaderEl = document.getElementById(loaderId);
            if (loaderEl) loaderEl.remove();
            historyEl.innerHTML += `
                <div class="ai-msg-card system error">
                    <div class="msg-header">
                        <div class="avatar-badge error">⚠️</div>
                        <span class="sender-name">System Error</span>
                    </div>
                    <div class="msg-body">
                        <p style="color:var(--risk-high);">Could not establish connection with Gemini AI. Please check internet access or API key configuration.</p>
                    </div>
                </div>
            `;
        } finally {
            historyEl.scrollTop = historyEl.scrollHeight;
        }
    }

    copyMessage(msgCardId) {
        const card = document.getElementById(msgCardId);
        if (!card) return;
        const bodyEl = card.querySelector('.msg-body');
        if (bodyEl) {
            navigator.clipboard.writeText(bodyEl.innerText);
            const copyBtn = card.querySelector('.btn-copy-msg');
            if (copyBtn) {
                copyBtn.textContent = '✓ Copied!';
                setTimeout(() => { copyBtn.textContent = '📋 Copy'; }, 2000);
            }
        }
    }

    async loadEmergencyAdvisory() {
        const box = document.getElementById('advisory-content-box');
        if (!box) return;

        if (!this.state.riskData) {
            box.innerHTML = '<p>No active risk profile to generate advisory.</p>';
            return;
        }

        box.innerHTML = '<p style="color:var(--text-muted); font-style:italic;">Drafting official advisory via Gemini AI...</p>';

        try {
            const name = this.state.activeCyclone ? this.state.activeCyclone.name : 'Unknown System';
            const req = {
                cyclone_name: name,
                vulnerability_score: this.state.riskData.vulnerability_score,
                risk_category: this.state.riskData.risk_category
            };

            const advisory = await ApiClient.generateAdvisory(req);
            this.currentAdvisoryMarkdown = advisory.advisory_markdown;
            
            const htmlContent = (advisory.advisory_markdown || '').replace(/\n/g, '<br>');
            box.innerHTML = `<div>${htmlContent}</div>`;
            
        } catch (error) {
            console.error('Failed to load advisory:', error);
            box.innerHTML = '<p style="color:var(--risk-high);">Error generating advisory. Please try again.</p>';
        }
    }

    downloadAdvisoryMarkdown() {
        if (!this.currentAdvisoryMarkdown) {
            alert('No advisory generated yet.');
            return;
        }
        
        const blob = new Blob([this.currentAdvisoryMarkdown], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Advisory_${this.activeCycloneId || 'Draft'}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    openContextPanel(title, contentHtml) {
        const titleEl = document.getElementById('context-panel-title');
        const bodyEl = document.getElementById('context-panel-body');
        const panel = document.getElementById('context-panel');

        if (titleEl) titleEl.textContent = title;
        if (bodyEl) bodyEl.innerHTML = contentHtml;
        
        if (panel) {
            panel.style.display = 'flex';
            panel.classList.add('open');
        }
        this.contextPanelOpen = true;
    }

    closeContextPanel() {
        const panel = document.getElementById('context-panel');
        if (panel) {
            panel.classList.remove('open');
            panel.style.display = 'none';
        }
        this.contextPanelOpen = false;
    }

    showLoading(isLoading) {
        const loader = document.getElementById('global-loading');
        if (loader) {
            if (isLoading) {
                loader.style.display = 'flex';
            } else {
                loader.style.display = 'none';
            }
        }
    }

    showError(msg) {
        // Just use standard alert for now to avoid creating extra HTML elements
        console.error("APP ERROR:", msg);
    }

    escapeHtml(unsafe) {
        return (unsafe || '').toString()
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.app = new Application();
});
