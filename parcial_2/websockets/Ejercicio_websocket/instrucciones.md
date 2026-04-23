# Ejercicio: Dashboard IoT en Tiempo Real

## Objetivo
Construir un dashboard web que reciba datos de sensores via HTTP POST y los muestre en tiempo real usando WebSockets.

**Entregable:** Screenshot del dashboard funcionando con datos en vivo.

---

## Setup (5 min)

### 1. Instalar dependencias
```bash
pip install flask flask-socketio
```

### 2. Descargar el simulador
El profesor les dará el archivo `sensor_simulator.py`. **No lo modifiquen.** Este archivo simula un sensor que manda datos por HTTP POST a `http://localhost:5000/api/sensor` cada 2 segundos.

El simulador manda JSONs con esta estructura:
```json
{
    "device_id": "SRV-01",
    "timestamp": "14:30:25",
    "temperature_c": 23.4,
    "power_w": 210.5,
    "cpu_percent": 35.2,
    "fan_rpm": 1180
}
```

---

## Ejercicio 1: Servidor básico (20 min)

Crea un archivo `server.py` que haga lo siguiente:

1. Crear una app Flask con SocketIO habilitado
2. Un endpoint `POST /api/sensor` que reciba el JSON del simulador — **el simulador ya manda POST a exactamente esa ruta**, tu trabajo es recibirlo y emitirlo por WebSocket
3. Cuando reciba datos, hacer `socketio.emit('sensor_update', data)` para empujarlos por WebSocket
4. Una ruta `GET /` que sirva un HTML básico

**Pistas:**
```python
from flask import Flask, request, jsonify
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Tu código aquí:
# - endpoint POST /api/sensor
# - dentro del endpoint: socketio.emit(...)
# - ruta GET / que regrese HTML
# - socketio.run(app, port=5000)
```

**Verificación:** Corre `server.py`, luego en otra terminal corre `sensor_simulator.py`. Debes ver prints en la terminal del servidor mostrando los datos que llegan.

---

## Ejercicio 2: Dashboard HTML (25 min)

Modifica tu `server.py` para que la ruta `GET /` sirva un HTML que:

1. Se conecte al servidor via WebSocket: `const socket = io();`
2. Escuche el evento `sensor_update`
3. Muestre los datos en la página (al menos temperatura y device_id)

**HTML mínimo para empezar:**
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.4/socket.io.min.js"></script>
<h1>Dashboard IoT</h1>
<div id="data">Esperando datos...</div>

<script>
    const socket = io();
    
    socket.on('sensor_update', (data) => {
        // Actualizar el div con los datos que llegan
        document.getElementById('data').innerHTML = 
            `<b>${data.device_id}</b>: ${data.temperature_c}°C`;
    });
</script>
```

**Verificación:** Con el servidor y simulador corriendo, abre `localhost:5000` en el navegador. Debes ver los datos actualizándose cada 2 segundos sin recargar la página.

---

## Ejercicio 3: Mejorar el dashboard (20 min)

Agrega al menos **3** de las siguientes mejoras:

- [ ] Mostrar las 4 variables: temperatura, consumo, CPU, fan RPM
- [ ] Indicador de conexión (conectado/desconectado)
- [ ] Contador de mensajes recibidos
- [ ] Cambiar el color de la temperatura si pasa de 30°C (alerta)
- [ ] Mostrar la hora del último dato recibido
- [ ] Log de las últimas 10 lecturas
- [ ] Separar datos por servidor (SRV-01, SRV-02, SRV-03)
- [ ] Agregar CSS para que se vea presentable (fondo oscuro, tarjetas, etc.)

---

## Ejercicio 4 — Bonus (si te sobra tiempo)

Agrega una gráfica con Chart.js:

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<canvas id="myChart"></canvas>

<script>
    const ctx = document.getElementById('myChart').getContext('2d');
    const chart = new Chart(ctx, {
        type: 'line',
        data: { labels: [], datasets: [{ label: 'Temp', data: [], borderColor: '#06b6d4' }] },
        options: { animation: false }
    });
    
    // Dentro de socket.on('sensor_update'):
    // chart.data.labels.push(data.timestamp);
    // chart.data.datasets[0].data.push(data.temperature_c);
    // if (chart.data.labels.length > 30) { chart.data.labels.shift(); chart.data.datasets[0].data.shift(); }
    // chart.update();
</script>
```

---

## Resumen de archivos

```
Tu carpeta:
├── server.py              ← Lo que TÚ creas
└── sensor_simulator.py    ← Te lo da el profesor (no modificar)
```

## Cómo correrlo

```
Terminal 1:  python server.py
Terminal 2:  python sensor_simulator.py
Navegador:   http://localhost:5000
```
