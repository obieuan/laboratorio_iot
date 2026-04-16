"""
=============================================================
SERVIDOR — Dashboard IoT en Tiempo Real
=============================================================
Este servidor hace DOS cosas:
  1. Recibe datos de sensores via HTTP POST (endpoint /api/sensor)
  2. Empuja esos datos a los navegadores via WebSocket

Ejecutar:
    pip install flask flask-socketio
    python server.py

Dashboard: http://localhost:5000
API:       POST http://localhost:5000/api/sensor
=============================================================
"""

from flask import Flask, request, jsonify, render_template_string
from flask_socketio import SocketIO
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'iot-eium-2026'
socketio = SocketIO(app, cors_allowed_origins="*")


# ============================================================
# ENDPOINT HTTP — recibe datos del simulador (o del ESP32)
# ============================================================
@app.route('/api/sensor', methods=['POST'])
def receive_sensor_data():
    """Recibe un JSON con datos del sensor y lo empuja por WebSocket"""
    data = request.get_json()
    
    # Mostrar en terminal lo que llega
    status = "🔴 ALERTA" if data.get('temperature_c', 0) > 30 else "🟢 normal"
    print(f"[API] {data['device_id']}  temp={data['temperature_c']}°C  "
          f"power={data['power_w']}W  cpu={data['cpu_percent']}%  {status}")
    
    # ✨ AQUÍ ESTÁ EL PUENTE ✨
    # Dato entra por HTTP POST → sale por WebSocket a todos los dashboards
    socketio.emit('sensor_update', data)
    
    return jsonify({"status": "ok", "received": data['device_id']})


# ============================================================
# EVENTOS WEBSOCKET
# ============================================================
@socketio.on('connect')
def handle_connect():
    print(f"[WS] ✅ Dashboard conectado  (total: {len(socketio.server.eio.sockets)} clientes)")
    socketio.emit('server_message', {
        'text': 'Conectado al servidor IoT',
        'timestamp': datetime.now().strftime("%H:%M:%S")
    })

@socketio.on('disconnect')
def handle_disconnect():
    print(f"[WS] ❌ Dashboard desconectado")


# ============================================================
# DASHBOARD HTML
# ============================================================
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IoT Server Room Monitor</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.4/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: #0a0e1a;
            color: #e2e8f0;
            min-height: 100vh;
        }
        .header {
            background: #111827;
            border-bottom: 2px solid #0891b2;
            padding: 12px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 { font-size: 18px; color: #06b6d4; }
        .status-badge { display: flex; align-items: center; gap: 8px; font-size: 13px; }
        .status-dot {
            width: 10px; height: 10px; border-radius: 50%;
            background: #ef4444;
        }
        .status-dot.connected {
            background: #10b981;
            animation: pulse 2s infinite;
        }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }
        .dashboard { padding: 20px; max-width: 1400px; margin: 0 auto; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px; margin-bottom: 20px;
        }
        .stat-card {
            background: #1e293b; border-radius: 12px; padding: 20px;
            text-align: center; border: 1px solid #334155;
            transition: all 0.3s;
        }
        .stat-card.alert { border-color: #ef4444; background: #1a1020; }
        .stat-value { font-size: 32px; font-weight: 700; margin-bottom: 4px; }
        .stat-label { font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; }
        .stat-device { font-size: 11px; color: #475569; margin-top: 6px; }
        .charts-grid {
            display: grid; grid-template-columns: 2fr 1fr;
            gap: 16px; margin-bottom: 20px;
        }
        .chart-card {
            background: #1e293b; border-radius: 12px; padding: 20px;
            border: 1px solid #334155;
        }
        .chart-card h3 { font-size: 14px; color: #94a3b8; margin-bottom: 12px; }
        .alerts-log { max-height: 280px; overflow-y: auto; }
        .alert-item {
            padding: 8px 12px; margin-bottom: 6px; border-radius: 6px;
            font-size: 12px; font-family: 'Consolas', monospace;
            display: flex; justify-content: space-between;
        }
        .alert-item.warning { background: rgba(245,158,11,0.15); color: #f59e0b; border-left: 3px solid #f59e0b; }
        .alert-item.critical { background: rgba(239,68,68,0.15); color: #ef4444; border-left: 3px solid #ef4444; }
        .alert-item.info { background: rgba(8,145,178,0.15); color: #06b6d4; border-left: 3px solid #06b6d4; }
        .servers-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
        .server-card {
            background: #1e293b; border-radius: 12px; padding: 16px;
            border: 1px solid #334155;
        }
        .server-card h4 { font-size: 14px; color: #06b6d4; margin-bottom: 10px; }
        .server-metric {
            display: flex; justify-content: space-between;
            padding: 4px 0; font-size: 13px; border-bottom: 1px solid #1a1a2e;
        }
        .server-metric .label { color: #64748b; }
        .server-metric .value { color: #e2e8f0; font-weight: 600; }
        .server-metric .value.hot { color: #ef4444; }
        .footer { text-align: center; padding: 12px; color: #475569; font-size: 11px; }
        .msg-count { font-size: 11px; color: #475569; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🖥️ IoT Server Room Monitor</h1>
        <div style="display:flex;align-items:center;gap:20px">
            <span class="msg-count" id="msgCount">Mensajes: 0</span>
            <div class="status-badge">
                <span id="connectionStatus">Desconectado</span>
                <div class="status-dot" id="statusDot"></div>
            </div>
        </div>
    </div>
    
    <div class="dashboard">
        <div class="stats-grid">
            <div class="stat-card" id="card-temp">
                <div class="stat-value" id="val-temp" style="color:#06b6d4">--</div>
                <div class="stat-label">Temperatura</div>
                <div class="stat-device" id="dev-temp">---</div>
            </div>
            <div class="stat-card" id="card-power">
                <div class="stat-value" id="val-power" style="color:#10b981">--</div>
                <div class="stat-label">Consumo</div>
                <div class="stat-device" id="dev-power">---</div>
            </div>
            <div class="stat-card" id="card-cpu">
                <div class="stat-value" id="val-cpu" style="color:#f59e0b">--</div>
                <div class="stat-label">CPU</div>
                <div class="stat-device" id="dev-cpu">---</div>
            </div>
            <div class="stat-card" id="card-fan">
                <div class="stat-value" id="val-fan" style="color:#a78bfa">--</div>
                <div class="stat-label">Fan RPM</div>
                <div class="stat-device" id="dev-fan">---</div>
            </div>
        </div>
        
        <div class="charts-grid">
            <div class="chart-card">
                <h3>📈 Temperatura en Tiempo Real</h3>
                <canvas id="tempChart"></canvas>
            </div>
            <div class="chart-card">
                <h3>⚠️ Log de Alertas</h3>
                <div class="alerts-log" id="alertsLog">
                    <div class="alert-item info"><span>Esperando datos del simulador...</span></div>
                </div>
            </div>
        </div>
        
        <div class="servers-grid">
            <div class="server-card"><h4>SRV-01</h4>
                <div class="server-metric"><span class="label">Temp</span><span class="value" id="srv01-temp">--</span></div>
                <div class="server-metric"><span class="label">Power</span><span class="value" id="srv01-power">--</span></div>
                <div class="server-metric"><span class="label">CPU</span><span class="value" id="srv01-cpu">--</span></div>
                <div class="server-metric"><span class="label">Fan</span><span class="value" id="srv01-fan">--</span></div>
            </div>
            <div class="server-card"><h4>SRV-02</h4>
                <div class="server-metric"><span class="label">Temp</span><span class="value" id="srv02-temp">--</span></div>
                <div class="server-metric"><span class="label">Power</span><span class="value" id="srv02-power">--</span></div>
                <div class="server-metric"><span class="label">CPU</span><span class="value" id="srv02-cpu">--</span></div>
                <div class="server-metric"><span class="label">Fan</span><span class="value" id="srv02-fan">--</span></div>
            </div>
            <div class="server-card"><h4>SRV-03</h4>
                <div class="server-metric"><span class="label">Temp</span><span class="value" id="srv03-temp">--</span></div>
                <div class="server-metric"><span class="label">Power</span><span class="value" id="srv03-power">--</span></div>
                <div class="server-metric"><span class="label">CPU</span><span class="value" id="srv03-cpu">--</span></div>
                <div class="server-metric"><span class="label">Fan</span><span class="value" id="srv03-fan">--</span></div>
            </div>
        </div>
    </div>
    <div class="footer">IoT Avanzado — EIUM — WebSockets + Flask-SocketIO</div>

    <script>
        const socket = io();
        let messageCount = 0;
        
        socket.on('connect', () => {
            document.getElementById('connectionStatus').textContent = 'En vivo';
            document.getElementById('statusDot').classList.add('connected');
            console.log('[WS] Conectado');
        });
        socket.on('disconnect', () => {
            document.getElementById('connectionStatus').textContent = 'Desconectado';
            document.getElementById('statusDot').classList.remove('connected');
        });
        
        // Gráfica
        const MAX_POINTS = 60;
        const chartData = {
            'SRV-01': { labels: [], data: [], color: '#06b6d4' },
            'SRV-02': { labels: [], data: [], color: '#10b981' },
            'SRV-03': { labels: [], data: [], color: '#f59e0b' },
        };
        const ctx = document.getElementById('tempChart').getContext('2d');
        const tempChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: Object.entries(chartData).map(([id, d]) => ({
                    label: id, data: d.data, borderColor: d.color,
                    backgroundColor: 'transparent', borderWidth: 2,
                    pointRadius: 0, tension: 0.3,
                }))
            },
            options: {
                responsive: true,
                animation: { duration: 300 },
                scales: {
                    x: { ticks: { color: '#64748b', maxTicksLimit: 10 }, grid: { color: '#1e293b' } },
                    y: { min: 15, max: 45, ticks: { color: '#64748b' }, grid: { color: '#1e293b' } }
                },
                plugins: { legend: { labels: { color: '#94a3b8', usePointStyle: true } } }
            }
        });
        
        // ✨ RECIBIR DATOS VIA WEBSOCKET ✨
        socket.on('sensor_update', (data) => {
            messageCount++;
            document.getElementById('msgCount').textContent = 'Mensajes: ' + messageCount;
            
            updateStatCards(data);
            updateChart(data);
            updateServerPanel(data);
            checkAlerts(data);
        });
        
        socket.on('server_message', (data) => { addAlert('info', data.text, data.timestamp); });
        
        function updateStatCards(data) {
            document.getElementById('val-temp').textContent = data.temperature_c + '°C';
            document.getElementById('dev-temp').textContent = data.device_id + ' — ' + data.timestamp;
            document.getElementById('val-power').textContent = data.power_w + 'W';
            document.getElementById('dev-power').textContent = data.device_id;
            document.getElementById('val-cpu').textContent = data.cpu_percent + '%';
            document.getElementById('dev-cpu').textContent = data.device_id;
            document.getElementById('val-fan').textContent = data.fan_rpm;
            document.getElementById('dev-fan').textContent = data.device_id;
            const card = document.getElementById('card-temp');
            if (data.temperature_c > 30) {
                card.classList.add('alert');
                document.getElementById('val-temp').style.color = '#ef4444';
            } else {
                card.classList.remove('alert');
                document.getElementById('val-temp').style.color = '#06b6d4';
            }
        }
        function updateChart(data) {
            const sd = chartData[data.device_id];
            if (!sd) return;
            sd.labels.push(data.timestamp);
            sd.data.push(data.temperature_c);
            if (sd.data.length > MAX_POINTS) { sd.labels.shift(); sd.data.shift(); }
            tempChart.data.labels = chartData['SRV-01'].labels;
            tempChart.update('none');
        }
        function updateServerPanel(data) {
            const p = data.device_id.toLowerCase().replace('-','');
            const el = document.getElementById(p+'-temp');
            if (!el) return;
            el.textContent = data.temperature_c + '°C';
            el.className = 'value' + (data.temperature_c > 30 ? ' hot' : '');
            document.getElementById(p+'-power').textContent = data.power_w + 'W';
            document.getElementById(p+'-cpu').textContent = data.cpu_percent + '%';
            document.getElementById(p+'-fan').textContent = data.fan_rpm;
        }
        function checkAlerts(data) {
            if (data.temperature_c > 35) addAlert('critical', data.device_id+' — '+data.temperature_c+'°C — CRÍTICO', data.timestamp);
            else if (data.temperature_c > 30) addAlert('warning', data.device_id+' — '+data.temperature_c+'°C — Temp alta', data.timestamp);
        }
        function addAlert(type, text, time) {
            const log = document.getElementById('alertsLog');
            const item = document.createElement('div');
            item.className = 'alert-item ' + type;
            item.innerHTML = '<span>'+text+'</span><span>'+(time||'')+'</span>';
            log.insertBefore(item, log.firstChild);
            while (log.children.length > 20) log.removeChild(log.lastChild);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)


# ============================================================
# ARRANQUE
# ============================================================
if __name__ == '__main__':
    print("=" * 55)
    print("  🖥️  IoT Server Room Monitor — SERVIDOR")
    print("=" * 55)
    print()
    print("  Dashboard:  http://localhost:5000")
    print("  API:        POST http://localhost:5000/api/sensor")
    print()
    print("  Esperando datos del simulador...")
    print("  (en otra terminal: python simulator.py)")
    print()
    print("=" * 55)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)