"""
=============================================================
Dashboard IoT en Tiempo Real
Flask-SocketIO + Chart.js + Datos Simulados
EIUM — Universidad Modelo — Prof. Gabriel
=============================================================

Ejecutar:
    pip install flask flask-socketio
    python app.py

Abrir en navegador:
    http://localhost:5000
"""

from flask import Flask, render_template_string
from flask_socketio import SocketIO
import random
import math
import time
from datetime import datetime
from threading import Thread

# ============================================================
# CONFIGURACIÓN
# ============================================================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'iot-eium-2026'
socketio = SocketIO(app, cors_allowed_origins="*")

# ============================================================
# SIMULADOR DE SENSORES
# ============================================================
# Simula 3 servidores con datos realistas
servers = {
    "SRV-01": {"base_temp": 22.0, "base_power": 180},
    "SRV-02": {"base_temp": 23.5, "base_power": 220},
    "SRV-03": {"base_temp": 21.0, "base_power": 160},
}

reading_count = 0

def generate_reading(srv_id, params):
    """Genera una lectura simulada realista"""
    global reading_count
    reading_count += 1
    
    now = datetime.now()
    hour = now.hour + now.minute / 60.0
    
    # Patrón diurno: más carga durante el día
    work_factor = 0.3 * math.exp(-0.5 * ((hour - 14) / 4) ** 2)
    
    # Temperatura base + patrón + ruido
    temp = params["base_temp"] + work_factor * 5 + random.gauss(0, 0.3)
    
    # Cada ~50 lecturas, inyectar una anomalía en SRV-01
    if srv_id == "SRV-01" and reading_count % 50 == 0:
        temp += random.uniform(10, 15)  # Pico de temperatura
    
    power = params["base_power"] + work_factor * 80 + random.gauss(0, 3)
    cpu = max(5, min(100, 25 + work_factor * 60 + random.gauss(0, 5)))
    fan = max(800, 1000 + (temp - 22) * 200 + random.gauss(0, 20))
    
    return {
        "device_id": srv_id,
        "timestamp": now.strftime("%H:%M:%S"),
        "temperature_c": round(temp, 1),
        "power_w": round(power, 1),
        "cpu_percent": round(cpu, 1),
        "fan_rpm": round(fan, 0),
        "status": "alert" if temp > 30 else "normal"
    }


def sensor_simulator():
    """Hilo que genera datos cada 2 segundos y los empuja via WebSocket"""
    while True:
        for srv_id, params in servers.items():
            reading = generate_reading(srv_id, params)
            
            # ✨ ESTO ES LO IMPORTANTE ✨
            # socketio.emit() empuja el dato a TODOS los clientes conectados
            # Sin que ellos lo pidan — esto es WebSockets en acción
            socketio.emit('sensor_update', reading)
            
        socketio.sleep(2)  # Cada 2 segundos


# ============================================================
# EVENTOS DE WEBSOCKET
# ============================================================
@socketio.on('connect')
def handle_connect():
    """Se ejecuta cuando un cliente (navegador) se conecta"""
    print(f"[WS] Cliente conectado")
    # Mandar un mensaje de bienvenida
    socketio.emit('server_message', {
        'text': 'Conectado al servidor IoT',
        'timestamp': datetime.now().strftime("%H:%M:%S")
    })


@socketio.on('disconnect')
def handle_disconnect():
    print(f"[WS] Cliente desconectado")


@socketio.on('request_status')
def handle_status_request():
    """El cliente puede pedir datos — bidireccional"""
    socketio.emit('server_message', {
        'text': f'Servidores monitoreados: {len(servers)}',
        'timestamp': datetime.now().strftime("%H:%M:%S")
    })


# ============================================================
# TEMPLATE HTML (Dashboard)
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
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: #0a0e1a;
            color: #e2e8f0;
            min-height: 100vh;
        }
        
        /* Header */
        .header {
            background: #111827;
            border-bottom: 2px solid #0891b2;
            padding: 12px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 {
            font-size: 18px;
            font-weight: 600;
            color: #06b6d4;
        }
        .status-badge {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
        }
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #ef4444;
            animation: none;
        }
        .status-dot.connected {
            background: #10b981;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        /* Main grid */
        .dashboard {
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        /* Stat cards */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: #1e293b;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            border: 1px solid #334155;
            transition: border-color 0.3s;
        }
        .stat-card.alert {
            border-color: #ef4444;
            background: #1a1020;
        }
        .stat-value {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 4px;
        }
        .stat-label {
            font-size: 12px;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .stat-device {
            font-size: 11px;
            color: #475569;
            margin-top: 6px;
        }
        
        /* Charts */
        .charts-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 16px;
            margin-bottom: 20px;
        }
        .chart-card {
            background: #1e293b;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #334155;
        }
        .chart-card h3 {
            font-size: 14px;
            color: #94a3b8;
            margin-bottom: 12px;
        }
        
        /* Alerts log */
        .alerts-log {
            max-height: 280px;
            overflow-y: auto;
        }
        .alert-item {
            padding: 8px 12px;
            margin-bottom: 6px;
            border-radius: 6px;
            font-size: 12px;
            font-family: 'Consolas', monospace;
            display: flex;
            justify-content: space-between;
        }
        .alert-item.warning {
            background: rgba(245, 158, 11, 0.15);
            color: #f59e0b;
            border-left: 3px solid #f59e0b;
        }
        .alert-item.critical {
            background: rgba(239, 68, 68, 0.15);
            color: #ef4444;
            border-left: 3px solid #ef4444;
        }
        .alert-item.info {
            background: rgba(8, 145, 178, 0.15);
            color: #06b6d4;
            border-left: 3px solid #06b6d4;
        }
        
        /* Server status */
        .servers-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
        }
        .server-card {
            background: #1e293b;
            border-radius: 12px;
            padding: 16px;
            border: 1px solid #334155;
        }
        .server-card h4 {
            font-size: 14px;
            color: #06b6d4;
            margin-bottom: 10px;
        }
        .server-metric {
            display: flex;
            justify-content: space-between;
            padding: 4px 0;
            font-size: 13px;
            border-bottom: 1px solid #1a1a2e;
        }
        .server-metric .label { color: #64748b; }
        .server-metric .value { color: #e2e8f0; font-weight: 600; }
        .server-metric .value.hot { color: #ef4444; }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 12px;
            color: #475569;
            font-size: 11px;
        }
    </style>
</head>
<body>
    <!-- Header -->
    <div class="header">
        <h1>🖥️ IoT Server Room Monitor</h1>
        <div class="status-badge">
            <span id="connectionStatus">Desconectado</span>
            <div class="status-dot" id="statusDot"></div>
        </div>
    </div>
    
    <div class="dashboard">
        <!-- Stats principales -->
        <div class="stats-grid">
            <div class="stat-card" id="card-temp">
                <div class="stat-value" id="val-temp" style="color: #06b6d4">--</div>
                <div class="stat-label">Temperatura</div>
                <div class="stat-device" id="dev-temp">---</div>
            </div>
            <div class="stat-card" id="card-power">
                <div class="stat-value" id="val-power" style="color: #10b981">--</div>
                <div class="stat-label">Consumo</div>
                <div class="stat-device" id="dev-power">---</div>
            </div>
            <div class="stat-card" id="card-cpu">
                <div class="stat-value" id="val-cpu" style="color: #f59e0b">--</div>
                <div class="stat-label">CPU</div>
                <div class="stat-device" id="dev-cpu">---</div>
            </div>
            <div class="stat-card" id="card-fan">
                <div class="stat-value" id="val-fan" style="color: #a78bfa">--</div>
                <div class="stat-label">Fan RPM</div>
                <div class="stat-device" id="dev-fan">---</div>
            </div>
        </div>
        
        <!-- Gráfica + Alertas -->
        <div class="charts-grid">
            <div class="chart-card">
                <h3>📈 Temperatura en Tiempo Real</h3>
                <canvas id="tempChart"></canvas>
            </div>
            <div class="chart-card">
                <h3>⚠️ Log de Alertas</h3>
                <div class="alerts-log" id="alertsLog">
                    <div class="alert-item info">
                        <span>Esperando datos...</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Estado por servidor -->
        <div class="servers-grid">
            <div class="server-card" id="srv-01-card">
                <h4>SRV-01</h4>
                <div class="server-metric"><span class="label">Temp</span><span class="value" id="srv01-temp">--</span></div>
                <div class="server-metric"><span class="label">Power</span><span class="value" id="srv01-power">--</span></div>
                <div class="server-metric"><span class="label">CPU</span><span class="value" id="srv01-cpu">--</span></div>
                <div class="server-metric"><span class="label">Fan</span><span class="value" id="srv01-fan">--</span></div>
            </div>
            <div class="server-card" id="srv-02-card">
                <h4>SRV-02</h4>
                <div class="server-metric"><span class="label">Temp</span><span class="value" id="srv02-temp">--</span></div>
                <div class="server-metric"><span class="label">Power</span><span class="value" id="srv02-power">--</span></div>
                <div class="server-metric"><span class="label">CPU</span><span class="value" id="srv02-cpu">--</span></div>
                <div class="server-metric"><span class="label">Fan</span><span class="value" id="srv02-fan">--</span></div>
            </div>
            <div class="server-card" id="srv-03-card">
                <h4>SRV-03</h4>
                <div class="server-metric"><span class="label">Temp</span><span class="value" id="srv03-temp">--</span></div>
                <div class="server-metric"><span class="label">Power</span><span class="value" id="srv03-power">--</span></div>
                <div class="server-metric"><span class="label">CPU</span><span class="value" id="srv03-cpu">--</span></div>
                <div class="server-metric"><span class="label">Fan</span><span class="value" id="srv03-fan">--</span></div>
            </div>
        </div>
    </div>
    
    <div class="footer">
        IoT Avanzado — EIUM — Universidad Modelo — WebSockets + Flask-SocketIO
    </div>

    <script>
        // ============================================================
        // CONEXIÓN WEBSOCKET
        // ============================================================
        const socket = io();
        
        // Estado de conexión
        socket.on('connect', () => {
            document.getElementById('connectionStatus').textContent = 'En vivo';
            document.getElementById('statusDot').classList.add('connected');
            console.log('[WS] Conectado al servidor');
        });
        
        socket.on('disconnect', () => {
            document.getElementById('connectionStatus').textContent = 'Desconectado';
            document.getElementById('statusDot').classList.remove('connected');
            console.log('[WS] Desconectado');
        });
        
        // ============================================================
        // GRÁFICA CON CHART.JS
        // ============================================================
        const MAX_POINTS = 60; // Últimos 60 puntos (~2 minutos)
        
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
                    label: id,
                    data: d.data,
                    borderColor: d.color,
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.3,
                }))
            },
            options: {
                responsive: true,
                animation: { duration: 300 },
                scales: {
                    x: {
                        ticks: { color: '#64748b', maxTicksLimit: 10 },
                        grid: { color: '#1e293b' }
                    },
                    y: {
                        min: 15, max: 45,
                        ticks: { color: '#64748b' },
                        grid: { color: '#1e293b' }
                    }
                },
                plugins: {
                    legend: {
                        labels: { color: '#94a3b8', usePointStyle: true }
                    }
                }
            }
        });
        
        // ============================================================
        // RECIBIR DATOS DEL SERVIDOR (WebSocket)
        // ============================================================
        // ✨ ESTA ES LA MAGIA ✨
        // socket.on() escucha eventos que el servidor empuja
        // No hay fetch(), no hay polling — el dato llega solo
        
        socket.on('sensor_update', (data) => {
            // 1. Actualizar tarjetas principales (último dato recibido)
            updateStatCards(data);
            
            // 2. Actualizar gráfica
            updateChart(data);
            
            // 3. Actualizar panel del servidor
            updateServerPanel(data);
            
            // 4. Verificar alertas
            checkAlerts(data);
        });
        
        socket.on('server_message', (data) => {
            addAlert('info', data.text, data.timestamp);
        });
        
        // ============================================================
        // FUNCIONES DE ACTUALIZACIÓN
        // ============================================================
        function updateStatCards(data) {
            document.getElementById('val-temp').textContent = data.temperature_c + '°C';
            document.getElementById('dev-temp').textContent = data.device_id + ' — ' + data.timestamp;
            
            document.getElementById('val-power').textContent = data.power_w + 'W';
            document.getElementById('dev-power').textContent = data.device_id;
            
            document.getElementById('val-cpu').textContent = data.cpu_percent + '%';
            document.getElementById('dev-cpu').textContent = data.device_id;
            
            document.getElementById('val-fan').textContent = data.fan_rpm;
            document.getElementById('dev-fan').textContent = data.device_id;
            
            // Cambiar color si hay alerta
            const tempCard = document.getElementById('card-temp');
            if (data.temperature_c > 30) {
                tempCard.classList.add('alert');
                document.getElementById('val-temp').style.color = '#ef4444';
            } else {
                tempCard.classList.remove('alert');
                document.getElementById('val-temp').style.color = '#06b6d4';
            }
        }
        
        function updateChart(data) {
            const srvData = chartData[data.device_id];
            if (!srvData) return;
            
            srvData.labels.push(data.timestamp);
            srvData.data.push(data.temperature_c);
            
            // Mantener máximo de puntos
            if (srvData.data.length > MAX_POINTS) {
                srvData.labels.shift();
                srvData.data.shift();
            }
            
            // Usar labels del primer servidor para el eje X
            tempChart.data.labels = chartData['SRV-01'].labels;
            tempChart.update('none'); // 'none' = sin animación (más rápido)
        }
        
        function updateServerPanel(data) {
            const prefix = data.device_id.toLowerCase().replace('-', '');
            const tempEl = document.getElementById(prefix + '-temp');
            if (!tempEl) return;
            
            tempEl.textContent = data.temperature_c + '°C';
            tempEl.className = 'value' + (data.temperature_c > 30 ? ' hot' : '');
            
            document.getElementById(prefix + '-power').textContent = data.power_w + 'W';
            document.getElementById(prefix + '-cpu').textContent = data.cpu_percent + '%';
            document.getElementById(prefix + '-fan').textContent = data.fan_rpm;
        }
        
        function checkAlerts(data) {
            if (data.temperature_c > 35) {
                addAlert('critical', 
                    `${data.device_id} — ${data.temperature_c}°C — TEMPERATURA CRÍTICA`, 
                    data.timestamp);
            } else if (data.temperature_c > 30) {
                addAlert('warning', 
                    `${data.device_id} — ${data.temperature_c}°C — Temperatura alta`, 
                    data.timestamp);
            }
        }
        
        function addAlert(type, text, time) {
            const log = document.getElementById('alertsLog');
            const item = document.createElement('div');
            item.className = 'alert-item ' + type;
            item.innerHTML = `<span>${text}</span><span>${time || ''}</span>`;
            
            // Insertar arriba
            log.insertBefore(item, log.firstChild);
            
            // Máximo 20 alertas visibles
            while (log.children.length > 20) {
                log.removeChild(log.lastChild);
            }
        }
    </script>
</body>
</html>
"""


# ============================================================
# RUTA PRINCIPAL
# ============================================================
@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)


# ============================================================
# ARRANQUE
# ============================================================
if __name__ == '__main__':
    print("=" * 50)
    print("IoT Server Room Monitor")
    print("Dashboard: http://localhost:5000")
    print("=" * 50)
    print()
    print("Simulando 3 servidores (SRV-01, SRV-02, SRV-03)")
    print("Datos cada 2 segundos via WebSocket")
    print("Anomalías inyectadas cada ~50 lecturas en SRV-01")
    print()
    print("Presiona Ctrl+C para detener")
    print("=" * 50)
    
    # Iniciar simulador en hilo separado
    socketio.start_background_task(sensor_simulator)
    
    # Iniciar servidor
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
