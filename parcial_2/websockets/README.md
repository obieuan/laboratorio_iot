# Práctica: Dashboard IoT en Tiempo Real

## WebSockets + Flask-SocketIO + Chart.js

**Curso:** IoT Avanzado — EIUM  
**Tema:** Comunicación en tiempo real con WebSockets

---

## ¿Qué vamos a construir?

Un dashboard web que muestra datos de sensores de un cuarto de servidores actualizándose en tiempo real, sin recargar la página. Los datos llegan del servidor al navegador via WebSockets.

---

## Requisitos

```bash
pip install flask flask-socketio
```

No necesitas Mosquitto ni ESP32. El servidor incluye un simulador de datos.

---

## Ejecutar

```bash
python app.py
```

Abrir en navegador: `http://localhost:5000`

Verás un dashboard oscuro con:
- 4 tarjetas con valores en vivo (temperatura, consumo, CPU, fan)
- Gráfica de temperatura actualizándose cada 2 segundos
- Log de alertas cuando la temperatura pasa de 30°C
- Panel de estado por servidor (SRV-01, SRV-02, SRV-03)

---

## Cómo funciona — paso a paso

### 1. El servidor (Python)

```python
from flask_socketio import SocketIO

socketio = SocketIO(app)

# Empujar datos a TODOS los clientes conectados
socketio.emit('sensor_update', data)
```

`socketio.emit()` es la clave: envía un mensaje a todos los navegadores conectados **sin que ellos lo pidan**. Esto es WebSockets — el servidor decide cuándo enviar.

### 2. El cliente (JavaScript)

```javascript
const socket = io();  // Conectar al servidor

// Escuchar el evento 'sensor_update'
socket.on('sensor_update', (data) => {
    // data llega automáticamente cuando el servidor lo manda
    updateChart(data);
    updateCards(data);
});
```

`socket.on()` registra un listener. Cada vez que el servidor hace `emit('sensor_update', ...)`, el callback se ejecuta automáticamente. No hay `fetch()`, no hay `setInterval()`.

### 3. El simulador

Un hilo de Python genera datos cada 2 segundos simulando 3 servidores con patrones diurnos y anomalías periódicas. En un proyecto real, este hilo se reemplaza por un subscriber MQTT.

---

## Arquitectura

```
[Simulador Python]  ──genera datos──►  [Flask-SocketIO]  ──WebSocket──►  [Navegador + Chart.js]
       │                                      │
  (en proyecto real                    (emit a todos
   sería ESP32 + MQTT)                 los clientes)
```

---

## Puntos clave para entender

1. **`socketio.emit()`** — Servidor empuja datos al cliente. Es lo opuesto a HTTP donde el cliente siempre inicia.

2. **`socket.on()`** — El cliente escucha eventos. No pregunta, solo espera a que lleguen datos.

3. **`start_background_task()`** — Flask-SocketIO corre el simulador en un hilo separado sin bloquear el servidor web.

4. **`chart.update('none')`** — Chart.js se actualiza sin animación para que sea rápido con datos frecuentes.

5. **Bidireccional** — El cliente también puede enviar: `socket.emit('request_status')` manda un mensaje al servidor.

---

## Para explorar por tu cuenta

- Modifica el intervalo de `socketio.sleep(2)` a `socketio.sleep(0.5)` — ¿qué pasa?
- Agrega una gráfica de consumo eléctrico (power_w)
- Cambia el umbral de alerta de 30°C a 25°C
- Agrega un botón en el HTML que mande un evento al servidor
