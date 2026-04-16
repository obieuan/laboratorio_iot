"""
=============================================================
Actividad 1 — Agregar una segunda gráfica al dashboard
EIUM — Universidad Modelo

El dashboard ya muestra temperatura en tiempo real.
Tu tarea: agregar una gráfica de consumo eléctrico (power_w).

Hay 2 TODOs marcados en el JavaScript del HTML.
El código de la gráfica de temperatura ya existe — úsalo como referencia.
=============================================================
"""

from flask import Flask, render_template_string
from flask_socketio import SocketIO
import random
import math
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'iot-eium-2026'
socketio = SocketIO(app, cors_allowed_origins="*")

servers = {
    "SRV-01": {"base_temp": 22.0, "base_power": 180},
    "SRV-02": {"base_temp": 23.5, "base_power": 220},
    "SRV-03": {"base_temp": 21.0, "base_power": 160},
}

reading_count = 0

def generate_reading(srv_id, params):
    global reading_count
    reading_count += 1
    now = datetime.now()
    hour = now.hour + now.minute / 60.0
    work_factor = 0.3 * math.exp(-0.5 * ((hour - 14) / 4) ** 2)
    temp = params["base_temp"] + work_factor * 5 + random.gauss(0, 0.3)
    if srv_id == "SRV-01" and reading_count % 50 == 0:
        temp += random.uniform(10, 15)
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
    }

def sensor_simulator():
    while True:
        for srv_id, params in servers.items():
            socketio.emit('sensor_update', generate_reading(srv_id, params))
        socketio.sleep(2)

@socketio.on('connect')
def handle_connect():
    socketio.emit('server_message', {
        'text': 'Conectado al servidor IoT',
        'timestamp': datetime.now().strftime("%H:%M:%S")
    })

@socketio.on('disconnect')
def handle_disconnect():
    pass


DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>IoT Dashboard — Actividad 1</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.4/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #0a0e1a; color: #e2e8f0; }
        .header {
            background: #111827; border-bottom: 2px solid #0891b2;
            padding: 12px 24px; display: flex; justify-content: space-between; align-items: center;
        }
        .header h1 { font-size: 18px; color: #06b6d4; }
        .status-badge { display: flex; align-items: center; gap: 8px; font-size: 13px; }
        .status-dot { width: 10px; height: 10px; border-radius: 50%; background: #ef4444; }
        .status-dot.connected { background: #10b981; animation: pulse 2s infinite; }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }
        .dashboard { padding: 20px; max-width: 1400px; margin: 0 auto; }
        .charts-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;  /* dos columnas iguales */
            gap: 16px;
            margin-bottom: 20px;
        }
        .chart-card {
            background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155;
        }
        .chart-card h3 { font-size: 14px; color: #94a3b8; margin-bottom: 12px; }
        .chart-card .todo-hint {
            color: #f59e0b; font-size: 12px; font-family: monospace;
            background: rgba(245,158,11,0.1); padding: 8px 12px; border-radius: 6px;
            margin-bottom: 12px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>IoT Server Room — Actividad 1</h1>
        <div class="status-badge">
            <span id="connectionStatus">Desconectado</span>
            <div class="status-dot" id="statusDot"></div>
        </div>
    </div>

    <div class="dashboard">
        <div class="charts-grid">

            <!-- Gráfica 1: Temperatura (ya implementada) -->
            <div class="chart-card">
                <h3>Temperatura en tiempo real</h3>
                <canvas id="tempChart"></canvas>
            </div>

            <!-- Gráfica 2: Consumo eléctrico (tu tarea) -->
            <div class="chart-card">
                <h3>Consumo eléctrico (W)</h3>
                <div class="todo-hint">TODO 2 — esta gráfica no actualiza todavía</div>
                <canvas id="powerChart"></canvas>
            </div>

        </div>
    </div>

    <script>
        const socket = io();

        socket.on('connect', () => {
            document.getElementById('connectionStatus').textContent = 'En vivo';
            document.getElementById('statusDot').classList.add('connected');
        });
        socket.on('disconnect', () => {
            document.getElementById('connectionStatus').textContent = 'Desconectado';
            document.getElementById('statusDot').classList.remove('connected');
        });

        // ============================================================
        // GRÁFICA DE TEMPERATURA (referencia — ya funciona)
        // ============================================================
        const MAX_POINTS = 60;

        const tempData = {
            'SRV-01': { labels: [], data: [], color: '#06b6d4' },
            'SRV-02': { labels: [], data: [], color: '#10b981' },
            'SRV-03': { labels: [], data: [], color: '#f59e0b' },
        };

        const tempChart = new Chart(document.getElementById('tempChart').getContext('2d'), {
            type: 'line',
            data: {
                labels: [],
                datasets: Object.entries(tempData).map(([id, d]) => ({
                    label: id, data: d.data, borderColor: d.color,
                    backgroundColor: 'transparent', borderWidth: 2,
                    pointRadius: 0, tension: 0.3,
                }))
            },
            options: {
                responsive: true,
                scales: {
                    x: { ticks: { color: '#64748b', maxTicksLimit: 8 }, grid: { color: '#1e293b' } },
                    y: { min: 15, max: 45, ticks: { color: '#64748b' }, grid: { color: '#1e293b' } }
                },
                plugins: { legend: { labels: { color: '#94a3b8', usePointStyle: true } } }
            }
        });

        function updateTempChart(data) {
            const d = tempData[data.device_id];
            if (!d) return;
            d.labels.push(data.timestamp);
            d.data.push(data.temperature_c);
            if (d.data.length > MAX_POINTS) { d.labels.shift(); d.data.shift(); }
            tempChart.data.labels = tempData['SRV-01'].labels;
            tempChart.update('none');
        }

        // ============================================================
        // TODO 1 — Crear la gráfica de consumo (powerChart)
        //
        // Crea una estructura powerData igual a tempData pero para power_w.
        // Inicializa powerChart con new Chart(...) igual que tempChart,
        // ajustando el eje Y al rango de watts (ej. min:100, max:400).
        // ============================================================


        // ============================================================
        // TODO 2 — Actualizar powerChart cuando llegan datos
        //
        // Crea una función updatePowerChart(data) igual a updateTempChart,
        // pero usando powerData y data.power_w en lugar de data.temperature_c.
        // Luego llámala dentro de socket.on('sensor_update', ...) abajo.
        // ============================================================


        // ============================================================
        // RECIBIR DATOS DEL SERVIDOR
        // ============================================================
        socket.on('sensor_update', (data) => {
            updateTempChart(data);
            // TODO: llamar updatePowerChart(data) aquí
        });

    </script>
</body>
</html>
"""


@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)


if __name__ == '__main__':
    print("Actividad 1 — http://localhost:5000")
    socketio.start_background_task(sensor_simulator)
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
