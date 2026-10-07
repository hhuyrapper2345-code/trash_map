import os
import webbrowser
import folium
from folium.plugins import LocateControl, MiniMap

# --- CẤU HÌNH DỮ LIỆU ---
VIETNAM_CENTER = [16.047079, 108.206230]
INITIAL_ZOOM = 6

TILE_LAYERS = [
    {
        "url": "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
        "attr": "Google Maps",
        "name": "Google Maps (Đường xá)",
        "max_zoom": 20,
    },
    {
        "url": "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        "attr": "Google Maps Satellite",
        "name": "Google Hybrid (Vệ tinh + Tên đường)",
        "max_zoom": 20,
    },
    {
        "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "attr": "Tiles &copy; Esri",
        "name": "Vệ tinh Esri (Nhà cửa chi tiết)",
        "max_zoom": 18,
    },
]

LOCATIONS = [
    {"name": "Thủ đô Hà Nội", "loc": [21.028511, 105.804817], "color": "red"},
    {"name": "TP. Hồ Chí Minh", "loc": [10.823099, 106.629664], "color": "blue"},
    {"name": "TP. Đà Nẵng", "loc": [16.047079, 108.206230], "color": "green"},
    {"name": "Quần đảo Hoàng Sa (Việt Nam)", "loc": [16.5, 112.0], "color": "orange"},
    {"name": "Quần đảo Trường Sa (Việt Nam)", "loc": [8.65, 111.92], "color": "orange"},
]


def build_vietnam_routing_map(output_filename="vietnam_map.html"):
    # 1. Khởi tạo bản đồ
    m = folium.Map(
        location=VIETNAM_CENTER,
        zoom_start=INITIAL_ZOOM,
        tiles=None,
        prefer_canvas=True
    )

    # 2. Thêm các Lớp bản đồ
    for layer in TILE_LAYERS:
        folium.TileLayer(
            tiles=layer["url"],
            attr=layer["attr"],
            name=layer["name"],
            max_zoom=layer["max_zoom"]
        ).add_to(m)

    # 3. Marker các thành phố chính
    markers_group = folium.FeatureGroup(name="Thành phố chính").add_to(m)
    for item in LOCATIONS:
        folium.Marker(
            location=item["loc"],
            popup=folium.Popup(f"<b>{item['name']}</b>", max_width=300),
            tooltip=item["name"],
            icon=folium.Icon(color=item["color"], icon="info-sign")
        ).add_to(markers_group)

    # 4. Định vị GPS Thời gian thực
    LocateControl(
        auto_start=False,
        flyTo=True,
        keepCurrentZoomLevel=True,
        strings={"title": "Vị trí của tôi"}
    ).add_to(m)

    # 5. Bản đồ thu nhỏ MiniMap
    mini_map = MiniMap(
        tile_layer=folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
            attr='Esri'
        ),
        toggle_display=True,
        position='bottomright'
    )
    m.add_child(mini_map)

    # 6. Quản lý Lớp bản đồ
    folium.LayerControl(position='topright', collapsed=False).add_to(m)

    # --- 7. TÙY CHỈNH UI: BỔ SUNG Ô TÌM KIẾM Ở GIỮA PHÍA TRÊN & STYLES GRADIENT ---
    gradient_ui_html = '''
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

    <!-- KHUNG TÌM KIẾM ĐỊA ĐIỂM RIÊNG (CHÍNH GIỮA PHÍA TRÊN) -->
    <div id="search-bar-container">
        <i class="fa-solid fa-magnifying-glass search-icon"></i>
        <input type="text" id="global-search-input" placeholder="Tìm kiếm địa điểm, địa chỉ..." autocomplete="off" oninput="debounceGlobalSearch()" />
        <button id="clear-search-btn" onclick="clearGlobalSearch()" style="display: none;">
            <i class="fa-solid fa-xmark"></i>
        </button>
        <div id="global-search-results" class="global-autocomplete-box"></div>
    </div>

    <!-- PANEL DẪN ĐƯỜNG (GÓC DƯỚI BÊN TRÁI) -->
    <div id="routing-panel">
        <div class="panel-header">
            <i class="fa-solid fa-route"></i>
            <h3>Dẫn Đường Ngắn Nhất</h3>
        </div>
        
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

    <style>
        /* === KHUNG TÌM KIẾM ĐỊA ĐIỂM (CHÍNH GIỮA PHÍA TRÊN) === */
        #search-bar-container {
            position: absolute;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1000;
            width: 420px;
            max-width: 90vw;
            display: flex;
            align-items: center;
            background: linear-gradient(135deg, rgba(30, 30, 47, 0.85) 0%, rgba(42, 42, 64, 0.85) 100%);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.18);
            border-radius: 30px;
            padding: 6px 16px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
        }

        #search-bar-container:focus-within {
            box-shadow: 0 12px 30px rgba(0, 210, 255, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.3);
            border-color: #00d2ff;
        }

        .search-icon {
            color: #00d2ff;
            font-size: 16px;
            margin-right: 10px;
        }

        #global-search-input {
            width: 100%;
            background: transparent;
            border: none;
            outline: none;
            color: #ffffff;
            font-size: 14px;
            font-family: 'Segoe UI', Roboto, sans-serif;
            padding: 8px 0;
        }

        #global-search-input::placeholder {
            color: #a0a0b5;
        }

        #clear-search-btn {
            background: transparent;
            border: none;
            color: #a0a0b5;
            cursor: pointer;
            font-size: 14px;
            padding: 4px;
            transition: color 0.2s;
        }

        #clear-search-btn:hover {
            color: #ff5252;
        }

        /* Gợi ý địa điểm thả xuống từ khung tìm kiếm chính */
        .global-autocomplete-box {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: rgba(30, 30, 47, 0.95);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 16px;
            max-height: 250px;
            overflow-y: auto;
            z-index: 1050;
            margin-top: 10px;
            display: none;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        }

        /* === PANEL DẪN ĐƯỜNG GRADIENT (GÓC DƯỚI TRÁI) === */
        #routing-panel {
            position: absolute;
            bottom: 25px;
            left: 20px;
            z-index: 1000;
            background: linear-gradient(135deg, rgba(30, 30, 47, 0.85) 0%, rgba(42, 42, 64, 0.85) 100%);
            padding: 20px;
            border-radius: 18px;
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.15);
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            width: 310px;
            color: #ffffff;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.15);
        }

        .panel-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 16px;
        }

        .panel-header i {
            font-size: 20px;
            background: linear-gradient(45deg, #00d2ff, #3a7bd5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .panel-header h3 {
            margin: 0;
            font-size: 16px;
            font-weight: 700;
            letter-spacing: 0.5px;
            background: linear-gradient(45deg, #ffffff, #d0d0d0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .input-group {
            position: relative;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
        }

        .input-group i {
            position: absolute;
            left: 12px;
            font-size: 14px;
            z-index: 2;
        }

        .icon-start { color: #00e676; }
        .icon-end { color: #ff5252; }

        .input-group input {
            width: 100%;
            padding: 10px 12px 10px 36px;
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 10px;
            color: #ffffff;
            font-size: 13px;
            outline: none;
            transition: all 0.3s ease;
            box-sizing: border-box;
        }

        .input-group input:focus {
            background: rgba(255, 255, 255, 0.15);
            border-color: #00d2ff;
            box-shadow: 0 0 10px rgba(0, 210, 255, 0.3);
        }

        .input-group input::placeholder {
            color: #a0a0b5;
        }

        .autocomplete-box {
            position: absolute;
            bottom: 100%;
            left: 0;
            right: 0;
            background: rgba(37, 37, 56, 0.95);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 10px;
            max-height: 180px;
            overflow-y: auto;
            z-index: 1050;
            margin-bottom: 6px;
            display: none;
            box-shadow: 0 -8px 20px rgba(0,0,0,0.5);
        }

        .autocomplete-item {
            padding: 10px 14px;
            font-size: 12px;
            color: #e0e0e0;
            cursor: pointer;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            transition: background 0.2s;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .autocomplete-item:hover {
            background: linear-gradient(90deg, #3a7bd5, #00d2ff);
            color: #fff;
        }

        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 14px;
        }

        .button-group button {
            flex: 1;
            padding: 10px;
            border: none;
            border-radius: 10px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            transition: all 0.3s ease;
        }

        #route-btn {
            background: linear-gradient(135deg, #11998e, #38ef7d);
            color: #ffffff;
            box-shadow: 0 4px 15px rgba(56, 239, 125, 0.3);
        }

        #route-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(56, 239, 125, 0.5);
        }

        #clear-btn {
            background: linear-gradient(135deg, #ff416c, #ff4b2b);
            color: #ffffff;
            box-shadow: 0 4px 15px rgba(255, 65, 108, 0.3);
        }

        #clear-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 65, 108, 0.5);
        }

        .info-card {
            margin-top: 14px;
            padding: 12px;
            background: linear-gradient(135deg, rgba(0, 210, 255, 0.15), rgba(58, 123, 213, 0.15));
            border: 1px solid rgba(0, 210, 255, 0.3);
            border-radius: 10px;
            font-size: 13px;
            text-align: center;
            color: #ffffff;
            animation: fadeIn 0.4s ease;
        }

        .info-card b {
            color: #00d2ff;
            font-size: 15px;
        }

        /* === Ô LAYER CONTROL GRADIENT === */
        .leaflet-control-layers {
            background: linear-gradient(135deg, rgba(30, 30, 47, 0.85) 0%, rgba(42, 42, 64, 0.85) 100%) !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 14px !important;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.15) !important;
            padding: 10px 14px !important;
            color: #ffffff !important;
            font-family: 'Segoe UI', Roboto, sans-serif !important;
            font-size: 13px !important;
        }

        .leaflet-control-layers-separator {
            border-top: 1px solid rgba(255, 255, 255, 0.15) !important;
            margin: 8px 0 !important;
        }

        .leaflet-control-layers-base label,
        .leaflet-control-layers-overlays label {
            display: flex !important;
            align-items: center !important;
            gap: 8px !important;
            margin-bottom: 6px !important;
            cursor: pointer !important;
            color: #e0e0e0 !important;
        }

        .leaflet-control-layers-base label:hover,
        .leaflet-control-layers-overlays label:hover {
            color: #00d2ff !important;
        }

        .leaflet-control-layers input[type="radio"],
        .leaflet-control-layers input[type="checkbox"] {
            accent-color: #00d2ff !important;
            cursor: pointer !important;
        }

        /* === BẢN ĐỒ THU NHỎ (MINIMAP) GLASSMORPHISM === */
        .leaflet-control-minimap {
            background: linear-gradient(135deg, rgba(30, 30, 47, 0.65) 0%, rgba(42, 42, 64, 0.65) 100%) !important;
            backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 16px !important;
            padding: 5px !important;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4) !important;
            overflow: hidden !important;
        }

        .leaflet-control-minimap-mapcontainer {
            border-radius: 12px !important;
            overflow: hidden !important;
        }

        .leaflet-control-minimap-rect {
            border: 2px solid #00d2ff !important;
            background-color: rgba(0, 210, 255, 0.15) !important;
            border-radius: 4px !important;
            box-shadow: 0 0 8px rgba(0, 210, 255, 0.6) !important;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(5px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>

    <script>
        var mapObj = null;
        var startMarker = null;
        var endMarker = null;
        var searchMarker = null;
        var routePolyline = null;
        var searchTimer = null;
        var globalSearchTimer = null;

        document.addEventListener("DOMContentLoaded", function() {
            for (var key in window) {
                if (key.startsWith("map_") && window[key] instanceof L.Map) {
                    mapObj = window[key];
                    break;
                }
            }

            if (mapObj) {
                mapObj.on('click', function(e) {
                    if (!startMarker) {
                        setStartPoint(e.latLng.lat, e.latLng.lng, "Điểm chọn trên bản đồ");
                    } else if (!endMarker) {
                        setEndPoint(e.latLng.lat, e.latLng.lng, "Điểm chọn trên bản đồ");
                        calculateRoute();
                    }
                });
            }

            document.addEventListener('click', function(e) {
                if (!e.target.closest('.input-group')) {
                    document.getElementById('start-results').style.display = 'none';
                    document.getElementById('end-results').style.display = 'none';
                }
                if (!e.target.closest('#search-bar-container')) {
                    document.getElementById('global-search-results').style.display = 'none';
                }
            });
        });

        /* --- XỬ LÝ TÌM KIẾM ĐỊA ĐIỂM CHÍNH --- */
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
                        } else {
                            box.style.display = 'none';
                        }
                    });
            }, 300);
        }

        function goToLocation(lat, lng, label) {
            if (searchMarker) mapObj.removeLayer(searchMarker);
            searchMarker = L.marker([lat, lng]).addTo(mapObj)
                .bindPopup("<b>Địa điểm tìm kiếm:</b><br>" + label).openPopup();
            mapObj.setView([lat, lng], 15, { animate: true });
        }

        function clearGlobalSearch() {
            document.getElementById('global-search-input').value = '';
            document.getElementById('clear-search-btn').style.display = 'none';
            document.getElementById('global-search-results').style.display = 'none';
            if (searchMarker) mapObj.removeLayer(searchMarker);
            searchMarker = null;
        }

        /* --- XỬ LÝ DẪN ĐƯỜNG --- */
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
                        } else {
                            box.style.display = 'none';
                        }
                    });
            }, 300);
        }

        function setStartPoint(lat, lng, label) {
            if (startMarker) mapObj.removeLayer(startMarker);
            startMarker = L.marker([lat, lng], {title: "Điểm đón (A)"}).addTo(mapObj)
                .bindPopup("<b>Điểm đón (A)</b><br>" + label).openPopup();
            document.getElementById('start-input').value = label;
        }

        function setEndPoint(lat, lng, label) {
            if (endMarker) mapObj.removeLayer(endMarker);
            endMarker = L.marker([lat, lng], {title: "Điểm đến (B)"}).addTo(mapObj)
                .bindPopup("<b>Điểm đến (B)</b><br>" + label).openPopup();
            document.getElementById('end-input').value = label;
        }

        async function calculateRoute() {
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

                        if (routePolyline) mapObj.removeLayer(routePolyline);

                        routePolyline = L.polyline(coords, {color: '#00d2ff', weight: 6, opacity: 0.9}).addTo(mapObj);
                        mapObj.fitBounds(routePolyline.getBounds(), {padding: [60, 60]});

                        var distKm = (route.distance / 1000).toFixed(2);
                        infoCard.innerHTML = `<i class="fa-solid fa-road"></i> Khoảng cách: <b>${distKm} km</b>`;
                    } else {
                        infoCard.innerHTML = "<span style='color: #ff5252;'>Không tìm thấy đường đi thích hợp!</span>";
                    }
                })
                .catch(err => {
                    infoCard.innerHTML = "<span style='color: #ff5252;'>Lỗi kết nối máy chủ dẫn đường!</span>";
                });
        }

        function clearRoute() {
            if (startMarker) mapObj.removeLayer(startMarker);
            if (endMarker) mapObj.removeLayer(endMarker);
            if (routePolyline) mapObj.removeLayer(routePolyline);
            startMarker = null;
            endMarker = null;
            routePolyline = null;
            document.getElementById('start-input').value = "";
            document.getElementById('end-input').value = "";
            document.getElementById('start-results').style.display = 'none';
            document.getElementById('end-results').style.display = 'none';
            var infoCard = document.getElementById('route-info');
            infoCard.style.display = 'none';
            infoCard.innerHTML = "";
        }
    </script>
    '''

    m.get_root().html.add_child(folium.Element(gradient_ui_html))

    # Lưu và mở bản đồ
    m.save(output_filename)
    print(f"[OK] Đã thêm thanh tìm kiếm chính ở giữa phía trên: {output_filename}")
    webbrowser.open('file://' + os.path.realpath(output_filename))


if __name__ == "__main__":
    build_vietnam_routing_map()