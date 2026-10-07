import os
import webbrowser

def build_2d_rotate_map_with_layers(output_filename="index.html"):
    html_content = '''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>Bản đồ 2D - Self-Adaptive Responsive Layout</title>
    
    <!-- Leaflet 2D Core -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

    <!-- Leaflet Rotate Plugin -->
    <script src="https://unpkg.com/leaflet-rotate@0.2.8/dist/leaflet-rotate-src.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet-rotate@0.2.8/dist/leaflet-rotate.css" />

    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

    <style>
        :root {
            --bg-glass: linear-gradient(135deg, rgba(30, 30, 47, 0.90) 0%, rgba(42, 42, 64, 0.90) 100%);
            --border-glass: 1px solid rgba(255, 255, 255, 0.18);
            --shadow-glass: 0 8px 25px rgba(0, 0, 0, 0.45);
            --accent-color: #00d2ff;
        }

        body, html {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            -webkit-tap-highlight-color: transparent;
            touch-action: manipulation;
        }

        #map {
            width: 100%;
            height: 100%;
            background-color: #1a1a2e;
        }

        /* 1. TỐI ƯU CÁC NÚT ĐIỀU KHIỂN BẢN ĐỒ LEAFLET */
        .leaflet-top.leaflet-left {
            top: 75px;
            left: 14px;
        }

        .leaflet-bar, .leaflet-control-zoom, .leaflet-control-layers {
            border: none !important;
            box-shadow: var(--shadow-glass) !important;
            border-radius: 14px !important;
            overflow: hidden;
        }

        .leaflet-bar a {
            background: var(--bg-glass) !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            border: var(--border-glass) !important;
            color: var(--accent-color) !important;
            font-weight: bold !important;
            width: 40px !important;
            height: 40px !important;
            line-height: 40px !important;
        }

        .leaflet-control-layers {
            background: var(--bg-glass) !important;
            backdrop-filter: blur(14px) !important;
            -webkit-backdrop-filter: blur(14px) !important;
            border: var(--border-glass) !important;
            color: #ffffff !important;
            padding: 10px 14px !important;
            font-size: 13px !important;
        }

        .leaflet-control-layers-base label {
            margin-bottom: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* 2. KHUNG TÌM KIẾM ĐỊA ĐIỂM GLOBAL */
        #search-bar-container {
            position: absolute;
            top: 16px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1000;
            width: 450px;
            max-width: calc(100vw - 110px);
            display: flex;
            align-items: center;
            background: var(--bg-glass);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: var(--border-glass);
            border-radius: 30px;
            padding: 4px 16px;
            box-shadow: var(--shadow-glass);
        }

        .search-icon { color: var(--accent-color); font-size: 16px; margin-right: 10px; }

        #global-search-input {
            width: 100%;
            background: transparent;
            border: none;
            outline: none;
            color: #ffffff;
            font-size: 14px;
            padding: 10px 0;
        }

        #clear-search-btn { background: transparent; border: none; color: #a0a0b5; cursor: pointer; padding: 6px; }

        .global-autocomplete-box {
            position: absolute;
            top: calc(100% + 8px); left: 0; right: 0;
            background: rgba(30, 30, 47, 0.95);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: var(--border-glass);
            border-radius: 16px;
            max-height: 250px;
            overflow-y: auto;
            z-index: 1050;
            display: none;
            box-shadow: var(--shadow-glass);
        }

        /* 3. NÚT LA BÀN RESET HƯỚNG BẮC */
        #reset-bearing-btn {
            position: absolute;
            top: 16px;
            right: 16px;
            z-index: 1000;
            width: 44px;
            height: 44px;
            border-radius: 50%;
            background: var(--bg-glass);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: var(--border-glass);
            color: var(--accent-color);
            font-size: 18px;
            cursor: pointer;
            box-shadow: var(--shadow-glass);
            display: flex;
            align-items: center;
            justify-content: center;
        }

        #compass-icon { transition: transform 0.1s linear; }

        /* 4. PANEL DẪN ĐƯỜNG (PC DEFAULT) */
        #routing-panel {
            position: absolute;
            bottom: 25px;
            left: 20px;
            z-index: 1000;
            background: var(--bg-glass);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            padding: 16px;
            border-radius: 20px;
            box-shadow: var(--shadow-glass);
            width: 310px;
            color: #ffffff;
            border: var(--border-glass);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .panel-header { display: flex; align-items: center; gap: 10px; cursor: pointer; }
        .panel-header i {
            font-size: 18px;
            background: linear-gradient(45deg, #00d2ff, #3a7bd5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .panel-header h3 { margin: 0; font-size: 15px; font-weight: 700; flex: 1; }
        .toggle-icon { display: none; color: #a0a0b5; font-size: 14px; }
        .panel-body { margin-top: 14px; }

        .input-group { position: relative; margin-bottom: 10px; display: flex; align-items: center; }
        .input-group i { position: absolute; left: 12px; font-size: 14px; z-index: 2; }
        .icon-start { color: #00e676; }
        .icon-end { color: #ff5252; }

        .input-group input {
            width: 100%;
            padding: 11px 12px 11px 36px;
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 12px;
            color: #ffffff;
            font-size: 13px;
            outline: none;
            box-sizing: border-box;
        }

        .autocomplete-box {
            position: absolute;
            bottom: calc(100% + 6px); left: 0; right: 0;
            background: rgba(37, 37, 56, 0.95);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: var(--border-glass);
            border-radius: 12px;
            max-height: 160px;
            overflow-y: auto;
            z-index: 1050;
            display: none;
        }

        .autocomplete-item {
            padding: 12px;
            font-size: 12px;
            color: #e0e0e0;
            cursor: pointer;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .button-group { display: flex; gap: 10px; margin-top: 14px; }
        .button-group button {
            flex: 1; padding: 11px; border: none; border-radius: 12px;
            font-size: 13px; font-weight: 600; cursor: pointer;
            display: flex; align-items: center; justify-content: center; gap: 6px;
            transition: opacity 0.2s;
        }
        .button-group button:active { opacity: 0.8; }
        #route-btn { background: linear-gradient(135deg, #11998e, #38ef7d); color: #fff; }
        #clear-btn { background: linear-gradient(135deg, #ff416c, #ff4b2b); color: #fff; }

        .info-card {
            margin-top: 12px; padding: 10px;
            background: rgba(0, 210, 255, 0.15);
            border: 1px solid rgba(0, 210, 255, 0.3);
            border-radius: 10px; font-size: 12px; text-align: center; color: #ffffff;
        }

        /* 5. ĐỒNG HỒ GLASS DESIGN (PC DEFAULT) */
        #glass-clock-container {
            position: absolute;
            bottom: 25px;
            left: 360px;
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 18px;
            background: var(--bg-glass);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: var(--border-glass);
            border-radius: 18px;
            box-shadow: var(--shadow-glass);
            color: #ffffff;
            height: 48px;
            box-sizing: border-box;
            transition: all 0.3s ease;
        }
        .clock-icon {
            font-size: 20px;
            background: linear-gradient(45deg, #00d2ff, #3a7bd5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        #clock-time { font-size: 16px; font-weight: 700; }
        #clock-date { font-size: 11px; color: #a0a0b5; margin-top: 1px; }

        /* RESPONSIVE MEDIA QUERIES */
        @media (max-width: 1024px) and (min-width: 769px) {
            #glass-clock-container {
                left: auto;
                right: 20px;
            }
        }

        @media (max-width: 768px) {
            #search-bar-container {
                top: 12px;
                left: 12px;
                transform: none;
                width: calc(100vw - 80px);
                max-width: none;
            }

            #reset-bearing-btn {
                top: 12px;
                right: 12px;
            }

            .leaflet-top.leaflet-left {
                top: 68px;
                left: 12px;
            }

            #glass-clock-container {
                display: none;
            }

            #routing-panel {
                bottom: 12px;
                left: 12px;
                right: 12px;
                width: auto;
                max-width: none;
                border-radius: 18px;
            }

            .toggle-icon { display: block; }

            #routing-panel.panel-collapsed .panel-body {
                display: none;
            }

            #routing-panel.panel-collapsed {
                padding: 12px 16px;
            }
        }
    </style>
</head>
<body>

    <div id="map"></div>

    <!-- KHUNG TÌM KIẾM ĐỊA ĐIỂM -->
    <div id="search-bar-container">
        <i class="fa-solid fa-magnifying-glass search-icon"></i>
        <input type="text" id="global-search-input" placeholder="Tìm kiếm địa điểm..." autocomplete="off" oninput="debounceGlobalSearch()" />
        <button id="clear-search-btn" onclick="clearGlobalSearch()" style="display: none;">
            <i class="fa-solid fa-xmark"></i>
        </button>
        <div id="global-search-results" class="global-autocomplete-box"></div>
    </div>

    <!-- NÚT RESET HƯỚNG BẮC -->
    <button id="reset-bearing-btn" title="Đặt lại hướng Bắc (0°)" onclick="resetMapBearing()">
        <i class="fa-solid fa-compass" id="compass-icon"></i>
    </button>

    <!-- PANEL DẪN ĐƯỜNG -->
    <div id="routing-panel" class="panel-collapsed">
        <div class="panel-header" onclick="toggleRoutingPanel()">
            <i class="fa-solid fa-route"></i>
            <h3>Dẫn Đường 2D</h3>
            <i class="fa-solid fa-chevron-up toggle-icon" id="panel-toggle-btn"></i>
        </div>
        
        <div class="panel-body">
            <div class="input-group">
                <i class="fa-solid fa-circle-dot icon-start"></i>
                <input type="text" id="start-input" placeholder="Nhập điểm đón (A)..." autocomplete="off" oninput="debounceSearch('start')" />
                <div id="start-results" class="autocomplete-box"></div>
            </div>

            <div class="input-group">
                <i class="fa-solid fa-location-dot icon-end"></i>
                <input type="text" id="end-input" placeholder="Nhập điểm đến (B)..." autocomplete="off" oninput="debounceSearch('end')" />
                <div id="end-results" class="autocomplete-box"></div>
            </div>

            <div class="button-group">
                <button id="route-btn" onclick="calculateRoute()">
                    <i class="fa-solid fa-paper-plane"></i> Tìm Đường
                </button>
                <button id="clear-btn" onclick="clearRoute()">
                    <i class="fa-solid fa-rotate-left"></i> Xóa
                </button>
            </div>

            <div id="route-info" class="info-card" style="display: none;"></div>
        </div>
    </div>

    <!-- ĐỒNG HỒ GLASS DESIGN -->
    <div id="glass-clock-container">
        <div class="clock-icon"><i class="fa-regular fa-clock"></i></div>
        <div class="clock-content">
            <div id="clock-time">00:00:00</div>
            <div id="clock-date">Thứ ..., --/--/----</div>
        </div>
    </div>

    <script>
        // 1. ĐỊNH NGHĨA CÁC LỚP BẢN ĐỒ (ĐÃ LỌC BỎ OPENSTREETMAP VÀ DARK MODE)
        var googleRoadmap = L.tileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
            maxZoom: 20, attribution: 'Google Maps'
        });

        var googleSatellite = L.tileLayer('https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
            maxZoom: 20, attribution: 'Google Vệ Tinh'
        });

        var googleHybrid = L.tileLayer('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', {
            maxZoom: 20, attribution: 'Google Hybrid'
        });

        var esriSat = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            maxZoom: 19, attribution: 'Esri Satellite'
        });

        // 2. KHỞI TẠO BẢN ĐỒ LEAFLET 2D VỚI XOAY 360 DEGREES
        var map = L.map('map', {
            center: [16.047079, 108.206230],
            zoom: 6,
            layers: [googleRoadmap],
            rotate: true,
            touchRotate: true,
            rotateControl: false
        });

        // 3. THÊM BỘ CHỌN LỚP BẢN ĐỒ
        var baseMaps = {
            "🗺️ Google Đường Bộ": googleRoadmap,
            "🛰️ Google Vệ Tinh": googleSatellite,
            "🌐 Google Hybrid": googleHybrid,
            "📡 Esri Satellite": esriSat
        };

        L.control.layers(baseMaps, null, { position: 'topleft' }).addTo(map);

        // 4. XỬ LÝ XOAY BẢN ĐỒ (PC + MOBILE)
        map.setBearing(0);

        map.on('rotate', function() {
            var bearing = map.getBearing();
            var compass = document.getElementById('compass-icon');
            if (compass) {
                compass.style.transform = `rotate(${-bearing}deg)`;
            }
        });

        var isRotating = false;
        var startX = 0;
        var startBearing = 0;
        var container = map.getContainer();

        container.addEventListener('mousedown', function(e) {
            if (e.ctrlKey || e.button === 2) {
                isRotating = true;
                startX = e.clientX;
                startBearing = map.getBearing() || 0;
                container.style.cursor = 'grabbing';
                e.preventDefault();
            }
        });

        window.addEventListener('mousemove', function(e) {
            if (isRotating) {
                var deltaX = e.clientX - startX;
                var newBearing = startBearing + (deltaX * 0.6);
                map.setBearing(newBearing);
            }
        });

        window.addEventListener('mouseup', function() {
            if (isRotating) {
                isRotating = false;
                container.style.cursor = '';
            }
        });

        container.addEventListener('contextmenu', e => e.preventDefault());

        function resetMapBearing() {
            map.setBearing(0);
        }

        /* ĐỒNG HỒ THỜI GIAN THỰC */
        function updateClock() {
            var now = new Date();
            var hours = String(now.getHours()).padStart(2, '0');
            var minutes = String(now.getMinutes()).padStart(2, '0');
            var seconds = String(now.getSeconds()).padStart(2, '0');
            document.getElementById('clock-time').innerText = `${hours}:${minutes}:${seconds}`;

            var days = ['Chủ Nhật', 'Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy'];
            var dayName = days[now.getDay()];
            var date = String(now.getDate()).padStart(2, '0');
            var month = String(now.getMonth() + 1).padStart(2, '0');
            var year = now.getFullYear();
            document.getElementById('clock-date').innerText = `${dayName}, ${date}/${month}/${year}`;
        }
        setInterval(updateClock, 1000);
        updateClock();

        /* TOGGLE PANEL MOBILE */
        function toggleRoutingPanel() {
            if (window.innerWidth <= 768) {
                var panel = document.getElementById('routing-panel');
                var icon = document.getElementById('panel-toggle-btn');
                if (panel.classList.contains('panel-collapsed')) {
                    panel.classList.remove('panel-collapsed');
                    icon.className = "fa-solid fa-chevron-down toggle-icon";
                } else {
                    panel.classList.add('panel-collapsed');
                    icon.className = "fa-solid fa-chevron-up toggle-icon";
                }
            }
        }

        /* DẪN ĐƯỜNG VÀ TÌM KIẾM ĐỊA ĐIỂM */
        var startMarker = null, endMarker = null, searchMarker = null, routePolyline = null;
        var globalSearchTimer = null, searchTimer = null;

        function debounceGlobalSearch() {
            clearTimeout(globalSearchTimer);
            var query = document.getElementById('global-search-input').value;
            var clearBtn = document.getElementById('clear-search-btn');

            if (query.length > 0) {
                clearBtn.style.display = 'block';
            } else {
                clearBtn.style.display = 'none';
                document.getElementById('global-search-results').style.display = 'none';
                return;
            }

            globalSearchTimer = setTimeout(() => {
                if (query.length < 2) return;
                fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&countrycodes=vn&limit=5`)
                    .then(res => res.json())
                    .then(data => {
                        var box = document.getElementById('global-search-results');
                        box.innerHTML = '';
                        if (data.length > 0) {
                            box.style.display = 'block';
                            data.forEach(item => {
                                var div = document.createElement('div');
                                div.className = 'autocomplete-item';
                                div.innerText = item.display_name;
                                div.onclick = function() {
                                    goToLocation(parseFloat(item.lat), parseFloat(item.lon), item.display_name);
                                    box.style.display = 'none';
                                };
                                box.appendChild(div);
                            });
                        } else { box.style.display = 'none'; }
                    });
            }, 300);
        }

        function goToLocation(lat, lng, label) {
            if (searchMarker) map.removeLayer(searchMarker);
            searchMarker = L.marker([lat, lng]).addTo(map)
                .bindPopup("<b>" + label + "</b>").openPopup();
            map.setView([lat, lng], 15);
        }

        function clearGlobalSearch() {
            document.getElementById('global-search-input').value = '';
            document.getElementById('clear-search-btn').style.display = 'none';
            document.getElementById('global-search-results').style.display = 'none';
            if (searchMarker) map.removeLayer(searchMarker);
        }

        function debounceSearch(type) {
            clearTimeout(searchTimer);
            searchTimer = setTimeout(() => {
                var query = document.getElementById(type + '-input').value;
                if (query.length < 2) {
                    document.getElementById(type + '-results').style.display = 'none';
                    return;
                }
                fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&countrycodes=vn&limit=5`)
                    .then(res => res.json())
                    .then(data => {
                        var box = document.getElementById(type + '-results');
                        box.innerHTML = '';
                        if (data.length > 0) {
                            box.style.display = 'block';
                            data.forEach(item => {
                                var div = document.createElement('div');
                                div.className = 'autocomplete-item';
                                div.innerText = item.display_name;
                                div.onclick = function() {
                                    if (type === 'start') {
                                        setStartPoint(parseFloat(item.lat), parseFloat(item.lon), item.display_name);
                                    } else {
                                        setEndPoint(parseFloat(item.lat), parseFloat(item.lon), item.display_name);
                                    }
                                    box.style.display = 'none';
                                };
                                box.appendChild(div);
                            });
                        } else { box.style.display = 'none'; }
                    });
            }, 300);
        }

        function setStartPoint(lat, lng, label) {
            if (startMarker) map.removeLayer(startMarker);
            startMarker = L.marker([lat, lng]).addTo(map).bindPopup("<b>Điểm đón (A)</b><br>" + label).openPopup();
            document.getElementById('start-input').value = label;
        }

        function setEndPoint(lat, lng, label) {
            if (endMarker) map.removeLayer(endMarker);
            endMarker = L.marker([lat, lng]).addTo(map).bindPopup("<b>Điểm đến (B)</b><br>" + label).openPopup();
            document.getElementById('end-input').value = label;
        }

        function calculateRoute() {
            var infoCard = document.getElementById('route-info');
            if (!startMarker || !endMarker) {
                infoCard.style.display = 'block';
                infoCard.innerHTML = "<span style='color: #ff5252;'>Vui lòng chọn đủ Điểm đón & Điểm đến!</span>";
                return;
            }

            var latLngA = startMarker.getLatLng();
            var latLngB = endMarker.getLatLng();
            var osrmUrl = `https://router.project-osrm.org/route/v1/driving/${latLngA.lng},${latLngA.lat};${latLngB.lng},${latLngB.lat}?overview=full&geometries=geojson`;

            infoCard.style.display = 'block';
            infoCard.innerHTML = "<i class='fa-solid fa-spinner fa-spin'></i> Đang tính toán đường đi...";

            fetch(osrmUrl)
                .then(res => res.json())
                .then(data => {
                    if (data.routes && data.routes.length > 0) {
                        var route = data.routes[0];
                        var coords = route.geometry.coordinates.map(c => [c[1], c[0]]);

                        if (routePolyline) map.removeLayer(routePolyline);
                        routePolyline = L.polyline(coords, {color: '#00d2ff', weight: 6, opacity: 0.9}).addTo(map);
                        map.fitBounds(routePolyline.getBounds(), {padding: [40, 40]});

                        var distKm = (route.distance / 1000).toFixed(2);
                        infoCard.innerHTML = `<i class="fa-solid fa-road"></i> Khoảng cách: <b>${distKm} km</b>`;
                    } else {
                        infoCard.innerHTML = "<span style='color: #ff5252;'>Không tìm thấy đường đi thích hợp!</span>";
                    }
                });
        }

        function clearRoute() {
            if (startMarker) map.removeLayer(startMarker);
            if (endMarker) map.removeLayer(endMarker);
            if (routePolyline) map.removeLayer(routePolyline);
            startMarker = null; endMarker = null; routePolyline = null;
            document.getElementById('start-input').value = '';
            document.getElementById('end-input').value = '';
            document.getElementById('route-info').style.display = 'none';
        }

        map.on('click', function(e) {
            if (!startMarker) {
                setStartPoint(e.latlng.lat, e.latlng.lng, "Điểm chọn trên bản đồ");
            } else if (!endMarker) {
                setEndPoint(e.latlng.lat, e.latlng.lng, "Điểm chọn trên bản đồ");
                calculateRoute();
            }
        });
    </script>
</body>
</html>
'''
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[OK] Đã cập nhật thành công bản đồ (Đã bỏ OpenStreetMap và Dark Map): {output_filename}")
    webbrowser.open('file://' + os.path.realpath(output_filename))

if __name__ == "__main__":
    build_2d_rotate_map_with_layers()