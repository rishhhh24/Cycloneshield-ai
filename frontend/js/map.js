/**
 * CycloneShield AI - Leaflet GIS Map Controller
 * Features India-wide monitoring, Leaflet MarkerCluster support, and dynamic target location analysis.
 */

class MapController {
    constructor(containerId) {
        this.containerId = containerId;
        this.map = null;
        this.currentBaseLayerKey = 'google_street';
        this.baseLayers = {};
        this.onMapClickCallback = null;
        this.targetMarker = null;
        this.markerClusterGroup = null;
        this.layerGroups = {
            track: null,
            buffers: null,
            target: null,
            hospitals: null,
            shelters: null,
            power: null,
            roads: null,
            railways: null
        };
        this.initMap();
    }

    initMap() {
        // Center default view around All India (22.59° N, 78.96° E)
        this.map = L.map(this.containerId, {
            center: [22.5937, 78.9629],
            zoom: 5,
            zoomControl: false
        });

        // Custom Zoom Control top-right
        L.control.zoom({ position: 'topright' }).addTo(this.map);

        // Define Google Maps standard tile provider
        this.baseLayers = {
            google_street: L.tileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
                attribution: '&copy; Google Maps',
                maxZoom: 20
            })
        };

        // Add Google Maps standard by default
        this.baseLayers[this.currentBaseLayerKey].addTo(this.map);

        // Initialize Layer Groups
        Object.keys(this.layerGroups).forEach(key => {
            this.layerGroups[key] = L.layerGroup().addTo(this.map);
        });

        // Initialize Wind Particle Stream Animation Overlay
        this.windOverlay = new WindAnimationOverlay(this.map);

        // Initialize Marker Cluster Group if available
        if (typeof L.markerClusterGroup === 'function') {
            this.markerClusterGroup = L.markerClusterGroup({
                chunkedLoading: true,
                spiderfyOnMaxZoom: true,
                showCoverageOnHover: false,
                zoomToBoundsOnClick: true,
                maxClusterRadius: 50
            });
            this.map.addLayer(this.markerClusterGroup);
        }

        // Listen for Map Clicks to Update Location Analysis Anywhere in India
        this.map.on('click', (e) => {
            const { lat, lng } = e.latlng;
            this.setTargetLocation(lat, lng);
            if (this.onMapClickCallback) {
                this.onMapClickCallback(lat, lng);
            }
        });
    }

    setTargetLocation(lat, lon, label = 'Selected Target Location') {
        if (!this.layerGroups.target) return;
        this.layerGroups.target.clearLayers();

        const pulseHtml = `
            <div class="map-target-pulse">
                <div class="ring"></div>
                <div class="dot"></div>
            </div>
        `;
        const customIcon = L.divIcon({
            html: pulseHtml,
            className: 'custom-target-icon',
            iconSize: [40, 40],
            iconAnchor: [20, 20]
        });

        this.targetMarker = L.marker([lat, lon], { icon: customIcon }).addTo(this.layerGroups.target);
        this.targetMarker.bindPopup(`
            <div style="padding:6px; font-weight:bold; font-size:11px; text-align:center;">
                🎯 ${label}<br>
                <span style="font-size:10px; color:#38bdf8;">Lat: ${lat.toFixed(4)}°, Lon: ${lon.toFixed(4)}°</span>
            </div>
        `);
    }

    clearTargetLocation() {
        if (this.layerGroups.target) {
            this.layerGroups.target.clearLayers();
        }
        this.targetMarker = null;
    }

    switchBaseLayer(layerKey) {
        if (!this.baseLayers[layerKey]) return;
        
        if (this.baseLayers[this.currentBaseLayerKey]) {
            this.map.removeLayer(this.baseLayers[this.currentBaseLayerKey]);
        }
        
        this.baseLayers[layerKey].addTo(this.map);
        this.currentBaseLayerKey = layerKey;
    }

    async searchLocation(query) {
        if (!query) return null;
        try {
            const resp = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}`);
            const data = await resp.json();
            if (data && data.length > 0) {
                const lat = parseFloat(data[0].lat);
                const lon = parseFloat(data[0].lon);
                this.map.flyTo([lat, lon], 10, { duration: 1.5 });
                this.setTargetLocation(lat, lon, data[0].display_name.split(',')[0]);
                return { lat, lon, display_name: data[0].display_name };
            }
        } catch(e) {
            console.warn("Geocoding failed:", e);
        }
        return null;
    }

    // Render Cyclone Track GeoJSON
    renderCycloneTrack(geojsonTrack) {
        this.layerGroups.track.clearLayers();
        this.layerGroups.buffers.clearLayers();

        if (!geojsonTrack || !geojsonTrack.features) return;

        const features = geojsonTrack.features;
        const coordinates = features.map(f => [f.geometry.coordinates[1], f.geometry.coordinates[0]]);

        // 1. Draw Storm Path Polyline
        const trackLine = L.polyline(coordinates, {
            color: '#0284c7',
            weight: 5,
            dashArray: '8, 6',
            opacity: 0.95
        }).addTo(this.layerGroups.track);

        // Fit map bounds to track
        this.map.fitBounds(trackLine.getBounds(), { padding: [60, 60] });

        // 2. Plot Track Points
        features.forEach(f => {
            const lat = f.geometry.coordinates[1];
            const lon = f.geometry.coordinates[0];
            const props = f.properties;

            const isLandfall = props.is_landfall_point;
            const wind = props.wind_speed_knots;

            // Marker color based on storm category
            let color = '#2563eb';
            if (wind >= 120) color = '#b91c1c'; // Super Cyclone
            else if (wind >= 90) color = '#dc2626'; // Very Severe
            else if (wind >= 60) color = '#d97706'; // Severe

            const marker = L.circleMarker([lat, lon], {
                radius: isLandfall ? 11 : 7,
                fillColor: color,
                color: '#ffffff',
                weight: isLandfall ? 3 : 2,
                fillOpacity: 0.95
            }).addTo(this.layerGroups.track);

            const popupContent = `
                <div style="padding:4px; min-width:200px;">
                    <div style="font-weight:bold; color:#0284c7; font-size:13px; border-bottom:1px solid rgba(0,0,0,0.1); padding-bottom:4px; margin-bottom:6px;">${props.storm_category || 'Track Point'}</div>
                    <div style="font-size:11px; line-height:1.5;">
                        <div><strong>Timestamp:</strong> ${props.timestamp_utc ? props.timestamp_utc.substring(0,16) : 'N/A'}</div>
                        <div><strong>Wind Speed:</strong> <span style="color:#d97706; font-weight:bold;">${wind} knots (${Math.round(wind*1.852)} km/h)</span></div>
                        <div><strong>Pressure:</strong> ${props.central_pressure_hpa || 'N/A'} hPa</div>
                        ${isLandfall ? `<div style="margin-top:6px; background:#b91c1c; color:white; padding:4px 8px; border-radius:4px; text-align:center; font-weight:bold;">🎯 LANDFALL POINT</div>` : ''}
                    </div>
                </div>
            `;
            marker.bindPopup(popupContent);

            if (isLandfall) {
                // 100km Outer Ring
                L.circle([lat, lon], {
                    radius: 100000,
                    color: '#d97706',
                    weight: 2,
                    dashArray: '5, 5',
                    fillColor: '#d97706',
                    fillOpacity: 0.08
                }).addTo(this.layerGroups.buffers);

                // 50km Gale Radius
                L.circle([lat, lon], {
                    radius: 50000,
                    color: '#dc2626',
                    weight: 2,
                    fillColor: '#dc2626',
                    fillOpacity: 0.15
                }).addTo(this.layerGroups.buffers);

                // 25km Eye Core Radius
                L.circle([lat, lon], {
                    radius: 25000,
                    color: '#b91c1c',
                    weight: 2.5,
                    fillColor: '#b91c1c',
                    fillOpacity: 0.3
                }).addTo(this.layerGroups.buffers);
            }
        });
    }

    // Render India-Wide Monitoring Mode when no active cyclone exists
    renderMonitoringMode() {
        this.layerGroups.track.clearLayers();
        this.layerGroups.buffers.clearLayers();

        // Fit Map to All-India View (No static fake cyclone circles)
        this.map.flyTo([22.5937, 78.9629], 5, { duration: 1.2 });
    }

    // Render Infrastructure GeoJSON Layer with Cluster Support
    renderInfrastructure(infraGeoJSON) {
        // Clear existing infra layers
        ['hospitals', 'shelters', 'power', 'roads', 'railways'].forEach(k => {
            this.layerGroups[k].clearLayers();
        });
        if (this.markerClusterGroup) {
            this.markerClusterGroup.clearLayers();
        }

        if (!infraGeoJSON || !infraGeoJSON.features) return;

        infraGeoJSON.features.forEach(f => {
            const props = f.properties;
            const geom = f.geometry;
            const cat = props.category;

            if (geom.type === 'Point') {
                const lat = geom.coordinates[1];
                const lon = geom.coordinates[0];

                let iconSvg = '';
                let targetGroup = this.layerGroups.hospitals;

                if (cat === 'hospital') {
                    targetGroup = this.layerGroups.hospitals;
                    iconSvg = `
                        <div class="custom-map-pin hospital-pin">
                            <svg width="34" height="42" viewBox="0 0 36 42" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M18 0C8.059 0 0 8.059 0 18C0 28.5 18 42 18 42C18 42 36 28.5 36 18C36 8.059 27.941 0 18 0Z" fill="#b91c1c"/>
                                <path d="M18 2C9.163 2 2 9.163 2 18C2 27.2 18 39.5 18 39.5C18 39.5 34 27.2 34 18C34 9.163 26.837 2 18 2Z" fill="#ef4444"/>
                                <rect x="15" y="9" width="6" height="18" rx="1.5" fill="white"/>
                                <rect x="9" y="15" width="18" height="6" rx="1.5" fill="white"/>
                            </svg>
                        </div>`;
                } else if (cat === 'shelter') {
                    targetGroup = this.layerGroups.shelters;
                    iconSvg = `
                        <div class="custom-map-pin shelter-pin">
                            <svg width="34" height="42" viewBox="0 0 36 42" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M18 0C8.059 0 0 8.059 0 18C0 28.5 18 42 18 42C18 42 36 28.5 36 18C36 8.059 27.941 0 18 0Z" fill="#047857"/>
                                <path d="M18 2C9.163 2 2 9.163 2 18C2 27.2 18 39.5 18 39.5C18 39.5 34 27.2 34 18C34 9.163 26.837 2 18 2Z" fill="#10b981"/>
                                <path d="M18 9L11 12.5V17.5C11 21.8 14 25.8 18 27C22 25.8 25 21.8 25 17.5V12.5L18 9Z" fill="white"/>
                            </svg>
                        </div>`;
                } else if (cat === 'power') {
                    targetGroup = this.layerGroups.power;
                    iconSvg = `
                        <div class="custom-map-pin power-pin">
                            <svg width="34" height="42" viewBox="0 0 36 42" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M18 0C8.059 0 0 8.059 0 18C0 28.5 18 42 18 42C18 42 36 28.5 36 18C36 8.059 27.941 0 18 0Z" fill="#b45309"/>
                                <path d="M18 2C9.163 2 2 9.163 2 18C2 27.2 18 39.5 18 39.5C18 39.5 34 27.2 34 18C34 9.163 26.837 2 18 2Z" fill="#f59e0b"/>
                                <path d="M17 9L11 19H17L15 27L24 16H18L20 9H17Z" fill="white"/>
                            </svg>
                        </div>`;
                }

                const customIcon = L.divIcon({
                    html: iconSvg,
                    className: 'custom-leaflet-icon-wrapper',
                    iconSize: [34, 42],
                    iconAnchor: [17, 42]
                });

                const marker = L.marker([lat, lon], { icon: customIcon });

                const popupContent = `
                    <div style="padding:4px; min-width:210px;">
                        <div style="font-weight:bold; color:#0284c7; font-size:13px; border-bottom:1px solid rgba(0,0,0,0.1); padding-bottom:4px; margin-bottom:6px;">${props.name}</div>
                        <div style="font-size:11px; line-height:1.5;">
                            <div><strong>Category:</strong> <span style="text-transform:capitalize;">${props.category}</span></div>
                            <div><strong>District:</strong> ${props.district}, ${props.state}</div>
                            ${props.capacity_val ? `<div><strong>Capacity:</strong> ${props.capacity_val} ${cat === 'hospital' ? 'Beds' : 'Persons'}</div>` : ''}
                            ${props.elevation_meters ? `<div><strong>Elevation:</strong> ${props.elevation_meters}m ASL</div>` : ''}
                        </div>
                    </div>
                `;
                marker.bindPopup(popupContent);

                if (this.markerClusterGroup) {
                    this.markerClusterGroup.addLayer(marker);
                } else {
                    marker.addTo(targetGroup);
                }

            } else if (geom.type === 'LineString') {
                const coords = geom.coordinates.map(c => [c[1], c[0]]);

                if (cat === 'road') {
                    L.polyline(coords, {
                        color: '#d97706',
                        weight: 4,
                        opacity: 0.85
                    }).bindPopup(`<div style="padding:4px; font-weight:bold; color:#d97706; font-size:11px;">${props.name}</div>`).addTo(this.layerGroups.roads);
                } else if (cat === 'railway') {
                    L.polyline(coords, {
                        color: '#0284c7',
                        weight: 3,
                        dashArray: '6, 6',
                        opacity: 0.85
                    }).bindPopup(`<div style="padding:4px; font-weight:bold; color:#0284c7; font-size:11px;">${props.name}</div>`).addTo(this.layerGroups.railways);
                }
            }
        });
    }

    // Layer Visibility Toggle Helper
    toggleLayerGroup(categoryKey, isVisible) {
        if (this.layerGroups[categoryKey]) {
            if (isVisible) {
                this.map.addLayer(this.layerGroups[categoryKey]);
            } else {
                this.map.removeLayer(this.layerGroups[categoryKey]);
            }
        }
    }
}

/**
 * Real-Time Canvas Particle Wind Flow Animation Layer for Leaflet Map
 */
class WindAnimationOverlay {
    constructor(map) {
        this.map = map;
        this.canvas = document.createElement('canvas');
        this.canvas.className = 'leaflet-wind-canvas-layer';
        this.canvas.style.position = 'absolute';
        this.canvas.style.pointerEvents = 'none';
        this.ctx = this.canvas.getContext('2d');

        const pane = map.getPanes().overlayPane;
        if (pane) pane.appendChild(this.canvas);

        this.particles = [];
        this.numParticles = 200; // High particle density for maximum visibility
        this.animating = false;

        this.reposition();
        this.initParticles();
        this.bindEvents();
        this.start();
    }

    reposition() {
        if (!this.map || !this.canvas) return;
        const size = this.map.getSize();
        if (this.canvas.width !== size.x || this.canvas.height !== size.y) {
            this.canvas.width = size.x;
            this.canvas.height = size.y;
        }
        const topLeft = this.map.containerPointToLayerPoint([0, 0]);
        L.DomUtil.setPosition(this.canvas, topLeft);
    }

    initParticles() {
        this.particles = [];
        const w = this.canvas.width || window.innerWidth;
        const h = this.canvas.height || window.innerHeight;

        const colors = [
            { r: 56, g: 189, b: 248 },  // Electric Cyan
            { r: 6, g: 182, b: 212 },   // Vibrant Teal
            { r: 96, g: 165, b: 250 },  // Light Sky Blue
            { r: 255, g: 255, b: 255 }  // Bright White Streak
        ];

        for (let i = 0; i < this.numParticles; i++) {
            const color = colors[Math.floor(Math.random() * colors.length)];
            this.particles.push({
                x: Math.random() * w,
                y: Math.random() * h,
                length: Math.random() * 40 + 15,
                speed: Math.random() * 3.5 + 1.5,
                angle: (Math.PI / 180) * (280 + Math.random() * 55),
                alpha: Math.random() * 0.35 + 0.65, // 0.65 to 1.0 ultra visible opacity
                width: Math.random() * 2.0 + 2.0,  // 2.0px to 4.0px thick lines
                color: color,
                life: Math.random() * 100
            });
        }
    }

    bindEvents() {
        this.map.on('move moveend zoomend resize', () => {
            this.reposition();
            this.initParticles();
        });
    }

    start() {
        if (this.animating) return;
        this.animating = true;
        const animate = () => {
            if (!this.animating) return;
            this.draw();
            requestAnimationFrame(animate);
        };
        requestAnimationFrame(animate);
    }

    draw() {
        if (!this.ctx || !this.canvas) return;
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        this.ctx.lineCap = 'round';

        for (let p of this.particles) {
            p.life += 1;
            if (p.life > 120 || p.x > this.canvas.width || p.y < 0 || p.x < 0 || p.y > this.canvas.height) {
                p.x = Math.random() * this.canvas.width;
                p.y = Math.random() * this.canvas.height;
                p.life = 0;
            }

            p.x += Math.cos(p.angle) * p.speed;
            p.y += Math.sin(p.angle) * p.speed;

            const tailX = p.x - Math.cos(p.angle) * p.length;
            const tailY = p.y - Math.sin(p.angle) * p.length;

            const grad = this.ctx.createLinearGradient(tailX, tailY, p.x, p.y);
            const { r, g, b } = p.color;
            grad.addColorStop(0, `rgba(${r}, ${g}, ${b}, 0)`);
            grad.addColorStop(1, `rgba(${r}, ${g}, ${b}, ${p.alpha})`);

            this.ctx.lineWidth = p.width;
            this.ctx.strokeStyle = grad;
            this.ctx.beginPath();
            this.ctx.moveTo(tailX, tailY);
            this.ctx.lineTo(p.x, p.y);
            this.ctx.stroke();

            // Glowing dot head for maximum visibility
            this.ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${p.alpha * 0.9})`;
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.width * 0.7, 0, Math.PI * 2);
            this.ctx.fill();
        }
    }
}
