# PRÁCTICA DE LABORATORIO No. 5C
## ARQUITECTURA IoT CON GATEWAY: RASPBERRY PI ZERO W

---

## MODALIDAD DE TRABAJO

**Equipos:** 5 integrantes por equipo

**Recursos compartidos:**
- 1 laboratorio virtual por equipo (mismo de Prácticas 5A y 5B)
- 1 Raspberry Pi Zero W como gateway (proporcionada por laboratorio)

**Recursos individuales:**
- 1 ESP32 (Node32) por integrante

**PRERREQUISITOS:** 
- Haber completado Prácticas 5A (MQTT) y 5B (REST)
- Conservar configuración del broker MQTT de Práctica 5A

---

## 1. OBJETIVO GENERAL

Implementar y evaluar una arquitectura IoT con gateway intermediario utilizando Raspberry Pi Zero W, analizando las ventajas del procesamiento edge, agregación de datos, y comparando esta arquitectura con comunicación directa (MQTT y REST).

---

## 2. OBJETIVOS ESPECÍFICOS

1. Configurar una Raspberry Pi Zero W como gateway IoT que actúe como intermediario entre dispositivos ESP32 y el servidor central.

2. Implementar procesamiento edge en el gateway: agregación de datos, filtrado y cálculos preliminares.

3. Establecer comunicación ESP32 → Gateway (HTTP local) y Gateway → Servidor (MQTT remoto).

4. Evaluar la tolerancia a fallos de la arquitectura con gateway (buffering local).

5. Comparar experimentalmente las tres arquitecturas: MQTT directo, REST directo, y Gateway intermediario.

---

## 3. INTRODUCCIÓN TEÓRICA

### 3.1 ¿Qué es un Gateway IoT?

Un **gateway IoT** es un dispositivo intermediario que conecta dispositivos de borde (edge devices) con la nube o servidores centrales. Actúa como puente entre diferentes protocolos, agrega datos, y puede realizar procesamiento local antes de enviar información al servidor.

```
┌─────────────┐                    ┌─────────────┐                    ┌─────────────┐
│   Sensores  │  Protocolo local   │   Gateway   │   Protocolo cloud  │   Servidor  │
│   (ESP32)   │ ──────────────────>│   (RPi)     │ ──────────────────>│   Central   │
│             │   BLE/WiFi/LoRa    │             │   MQTT/HTTP/CoAP   │   (Cloud)   │
└─────────────┘                    └─────────────┘                    └─────────────┘
                                          │
                                          │ Edge Computing
                                          │ • Agregación
                                          │ • Filtrado
                                          │ • Buffer local
                                          │ • Cálculos
                                          └────────────────
```

### 3.2 Funciones de un Gateway IoT

**1. Traducción de protocolos:**
- Dispositivos de bajo consumo (BLE, Zigbee, LoRa) → Protocolo Internet (MQTT, HTTP)
- Permite heterogeneidad en la red de sensores

**2. Agregación de datos:**
- Combinar datos de múltiples sensores
- Reducir número de transmisiones a la nube
- Ejemplo: En lugar de enviar 100 lecturas individuales, enviar 1 mensaje con estadísticas

**3. Edge Computing (Procesamiento en el borde):**
- Cálculos locales: promedios, máximos, mínimos, detección de anomalías
- Filtrado de datos redundantes o ruidosos
- Toma de decisiones locales sin necesidad de comunicación con servidor

**4. Buffering (Almacenamiento temporal):**
- Si la conexión a Internet falla, el gateway puede almacenar datos localmente
- Reenviar cuando la conexión se restablezca
- Mejora la confiabilidad del sistema

**5. Seguridad:**
- Punto centralizado para implementar firewall, encriptación
- Autenticación de dispositivos antes de enviar datos a la nube

### 3.3 Ventajas de usar Gateway

| Ventaja | Descripción |
|---------|-------------|
| **Reducción de ancho de banda** | Menos datos enviados a la nube (agregación) |
| **Menor latencia local** | Decisiones locales sin round-trip a servidor |
| **Tolerancia a fallos** | Buffer local si Internet falla |
| **Menor consumo de energía** | Sensores usan protocolos de bajo consumo al gateway cercano |
| **Escalabilidad** | Gateway puede manejar muchos sensores, el servidor solo ve 1 gateway |
| **Heterogeneidad** | Dispositivos con diferentes protocolos pueden coexistir |
| **Seguridad mejorada** | Punto centralizado de control y encriptación |

### 3.4 Desventajas de usar Gateway

| Desventaja | Descripción |
|------------|-------------|
| **Punto único de fallo** | Si el gateway falla, todos los sensores quedan desconectados |
| **Mayor latencia end-to-end** | Salto adicional: Sensor → Gateway → Servidor |
| **Complejidad adicional** | Más componentes que configurar y mantener |
| **Costo inicial** | Hardware adicional requerido |
| **Gestión** | El gateway requiere mantenimiento, actualizaciones, monitoreo |

### 3.5 Raspberry Pi Zero W como Gateway

La Raspberry Pi Zero W es ideal para gateway IoT por:

**Especificaciones:**
- **CPU:** ARM11 de 1GHz (single-core)
- **RAM:** 512 MB
- **WiFi:** 802.11 b/g/n integrado
- **Bluetooth:** 4.1 BLE integrado
- **GPIO:** 40 pines para sensores/actuadores
- **Consumo:** ~100-150 mA (0.5W)
- **Tamaño:** 65mm × 30mm
- **Costo:** ~$10 USD

**Ventajas como gateway:**
- ✓ Sistema operativo Linux completo (Python, Node.js, etc.)
- ✓ Conectividad WiFi y Bluetooth integradas
- ✓ Bajo consumo energético
- ✓ Bajo costo
- ✓ Fácil de programar
- ✓ Gran comunidad y soporte

**Limitaciones:**
- ✗ CPU limitada (no para procesamiento intensivo)
- ✗ 512MB RAM (limita aplicaciones concurrentes)
- ✗ WiFi no es de alto rendimiento
- ✗ No tiene Ethernet (salvo con adaptador USB)

### 3.6 Comparación de arquitecturas

```
┌──────────────────────────────────────────────────────────────────┐
│                    ARQUITECTURA 1: MQTT DIRECTO                  │
│  ESP32 ─────WiFi─────→ Internet ─────→ Servidor MQTT            │
│                                                                  │
│  Ventajas:    • Menor latencia                                   │
│               • Tiempo real nativo                               │
│  Desventajas: • Cada ESP32 requiere conectividad directa        │
│               • Sin procesamiento edge                           │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                    ARQUITECTURA 2: REST DIRECTO                  │
│  ESP32 ─────WiFi─────→ Internet ─────→ API REST                 │
│                                                                  │
│  Ventajas:    • Simple de implementar                            │
│               • Familiar para desarrolladores web                │
│  Desventajas: • Polling requerido (no tiempo real)              │
│               • Mayor overhead HTTP                              │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                  ARQUITECTURA 3: GATEWAY (Esta práctica)         │
│  ESP32 ─→ WiFi local ─→ Raspberry Pi ─→ Internet ─→ Servidor    │
│           (HTTP)         (Gateway)        (MQTT)                 │
│                             ↓                                    │
│                      Edge Processing                             │
│                      • Agregación                                │
│                      • Buffer local                              │
│                      • Filtrado                                  │
│                                                                  │
│  Ventajas:    • Procesamiento edge                               │
│               • Tolerancia a fallas de Internet                  │
│               • Reduce tráfico a servidor                        │
│  Desventajas: • Mayor latencia (salto adicional)                 │
│               • Punto único de fallo (gateway)                   │
│               • Mayor complejidad                                │
└──────────────────────────────────────────────────────────────────┘
```

---

## 4. MATERIALES Y HERRAMIENTAS

### 4.1 Hardware
- **1 Raspberry Pi Zero W** (compartida por equipo)
- **1 tarjeta microSD** (16GB mínimo) con Raspbian OS Lite
- **1 fuente de alimentación** micro-USB 5V 2A
- **5 ESP32 (Node32)** (uno por integrante)
- **Cables USB** para ESP32 y Raspberry Pi

### 4.2 Software - Raspberry Pi
- **Raspbian OS Lite** (ya instalado)
- **Python 3** con pip
- **Bibliotecas Python:** `flask`, `paho-mqtt`, `requests`

### 4.3 Software - ESP32
- **Arduino IDE** configurado
- **Bibliotecas:** WiFi.h, HTTPClient.h, ArduinoJson.h

### 4.4 Acceso al laboratorio virtual
- **Mismo laboratorio** de Prácticas 5A y 5B
- **Broker MQTT** debe seguir corriendo en puerto 3000

---

## 5. ARQUITECTURA DEL SISTEMA

### 5.1 Flujo de datos

```
┌──────────┐                        ┌─────────────────────┐
│  ESP32_1 │─┐                      │  Raspberry Pi Zero  │
└──────────┘ │                      │     (Gateway)       │
┌──────────┐ │                      │                     │
│  ESP32_2 │─┤                      │  ┌───────────────┐  │
└──────────┘ │  HTTP POST           │  │  Flask Server │  │
┌──────────┐ │  192.168.X.X:5000    │  │  puerto 5000  │  │
│  ESP32_3 │─┼────────────────────► │  └───────┬───────┘  │
└──────────┘ │  {"temp": 23.5}      │          │          │
┌──────────┐ │                      │          ▼          │
│  ESP32_4 │─┤                      │  ┌───────────────┐  │
└──────────┘ │                      │  │ Agregador     │  │
┌──────────┐ │                      │  │ • Promedio    │  │
│  ESP32_5 │─┘                      │  │ • Min/Max     │  │
└──────────┘                        │  │ • Buffer      │  │
                                    │  └───────┬───────┘  │
                                    │          │          │
                                    │          ▼          │
                                    │  ┌───────────────┐  │
                                    │  │  MQTT Client  │  │
                                    │  │   Publisher   │  │
                                    │  └───────┬───────┘  │
                                    └──────────┼──────────┘
                                               │
                                               │ MQTT
                                               │ devlabs.eium.com.mx:3000
                                               ▼
                                    ┌──────────────────────┐
                                    │   devlabs Server     │
                                    │                      │
                                    │  ┌────────────────┐  │
                                    │  │ Mosquitto MQTT │  │
                                    │  │  Broker :3000  │  │
                                    │  └────────────────┘  │
                                    └──────────────────────┘
```

### 5.2 Protocolos utilizados

1. **ESP32 → Gateway:** HTTP POST (red local)
   - Protocolo simple y familiar
   - No requiere broker adicional
   - Red local de baja latencia

2. **Gateway → Servidor:** MQTT (Internet)
   - Eficiente para envío periódico
   - Bajo overhead
   - QoS para confiabilidad

---

## 6. DESARROLLO DE LA PRÁCTICA

### Organización del trabajo

| Rol | Responsable | Tareas |
|-----|-------------|--------|
| **Administrador Gateway** | Integrante 1 | Configurar Raspberry Pi, instalar software |
| **Desarrollador Gateway** | Integrante 2 | Programar lógica del gateway (Python) |
| **Desarrollador ESP32** | Integrante 3 | Adaptar código ESP32 para gateway |
| **Tester** | Integrante 4 | Pruebas de tolerancia a fallos |
| **Analista** | Integrante 5 | Comparación de arquitecturas |

---

## PARTE 1: CONFIGURACIÓN DE LA RASPBERRY PI

### 1.1 Conexión inicial (Integrante 1)

**Paso 1:** Conectar Raspberry Pi a monitor, teclado (o acceder por SSH)

**Paso 2:** Verificar conectividad WiFi:
```bash
# Ver redes disponibles
sudo iwlist wlan0 scan | grep ESSID

# Configurar WiFi (si no está configurado)
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```

Agregar:
```
network={
    ssid="NOMBRE_RED_LAB"
    psk="PASSWORD"
}
```

**Paso 3:** Reiniciar WiFi:
```bash
sudo systemctl restart dhcpcd
```

**Paso 4:** Obtener IP local:
```bash
hostname -I
```

**Anotar esta IP, será usada por los ESP32:** `192.168.X.X`

### 1.2 Instalación de dependencias

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python y pip
sudo apt install python3-pip -y

# Instalar bibliotecas Python
pip3 install flask flask-cors paho-mqtt requests

# Verificar instalación
python3 -c "import flask, paho.mqtt.client; print('OK')"
```

---

## PARTE 2: PROGRAMACIÓN DEL GATEWAY

### 2.1 Código completo del gateway (Integrante 2)

```bash
mkdir ~/gateway_iot
cd ~/gateway_iot
nano gateway.py
```

```python
#!/usr/bin/env python3
"""
Gateway IoT - Raspberry Pi Zero W
Práctica 5C

Funciones:
- Recibe datos de ESP32 vía HTTP local
- Agrega y procesa datos (Edge Computing)
- Reenvía al broker MQTT central
- Buffer local para tolerancia a fallos
"""

from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import json
import threading
import time
from datetime import datetime
from collections import defaultdict
import statistics

# ==================== CONFIGURACIÓN ====================
# Flask (HTTP local para recibir de ESP32)
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5000

# MQTT (para enviar al servidor central)
MQTT_BROKER = "devlabs.eium.com.mx"
MQTT_PORT = 3000
MQTT_BASE_TOPIC = "gateway/alpha"
MQTT_KEEPALIVE = 60

# Edge Computing
AGGREGATION_INTERVAL = 30  # Enviar agregación cada 30 segundos
MAX_BUFFER_SIZE = 1000     # Máximo de mensajes en buffer si MQTT falla

# ==================== VARIABLES GLOBALES ====================
app = Flask(__name__)

# Buffer de datos por dispositivo: {device_id: [lecturas]}
device_buffer = defaultdict(list)

# Buffer para datos no enviados (si MQTT offline)
offline_buffer = []

# Cliente MQTT
mqtt_client = mqtt.Client(client_id="gateway_rpi_zero")
mqtt_connected = False

# Estadísticas
stats = {
    'messages_received': 0,
    'messages_sent': 0,
    'messages_buffered': 0,
    'devices_registered': set(),
    'start_time': time.time()
}

# ==================== FUNCIONES MQTT ====================
def on_mqtt_connect(client, userdata, flags, rc):
    """Callback cuando se conecta al broker MQTT"""
    global mqtt_connected
    if rc == 0:
        print(f"✓ [MQTT] Conectado al broker {MQTT_BROKER}:{MQTT_PORT}")
        mqtt_connected = True
        
        # Enviar buffer offline si hay mensajes pendientes
        if offline_buffer:
            print(f"⟳ [MQTT] Enviando {len(offline_buffer)} mensajes del buffer offline")
            for msg in offline_buffer:
                client.publish(msg['topic'], msg['payload'], qos=1)
            offline_buffer.clear()
            stats['messages_buffered'] = 0
    else:
        print(f"✗ [MQTT] Error de conexión. Código: {rc}")
        mqtt_connected = False

def on_mqtt_disconnect(client, userdata, rc):
    """Callback cuando se desconecta del broker"""
    global mqtt_connected
    mqtt_connected = False
    if rc != 0:
        print(f"⚠ [MQTT] Desconexión inesperada. Código: {rc}")

def connect_mqtt():
    """Conectar al broker MQTT"""
    mqtt_client.on_connect = on_mqtt_connect
    mqtt_client.on_disconnect = on_mqtt_disconnect
    
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
        mqtt_client.loop_start()
        print(f"[MQTT] Intentando conexión a {MQTT_BROKER}:{MQTT_PORT}")
    except Exception as e:
        print(f"✗ [MQTT] Error al conectar: {e}")

def publish_to_mqtt(topic, payload, qos=1):
    """Publica mensaje al broker MQTT (con buffer si está offline)"""
    if mqtt_connected:
        try:
            result = mqtt_client.publish(topic, payload, qos=qos)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                stats['messages_sent'] += 1
                return True
            else:
                print(f"⚠ [MQTT] Error al publicar: {result.rc}")
                return False
        except Exception as e:
            print(f"✗ [MQTT] Excepción al publicar: {e}")
            return False
    else:
        # MQTT offline: guardar en buffer
        if len(offline_buffer) < MAX_BUFFER_SIZE:
            offline_buffer.append({'topic': topic, 'payload': payload})
            stats['messages_buffered'] = len(offline_buffer)
            print(f"⊙ [Buffer] Mensaje almacenado ({len(offline_buffer)}/{MAX_BUFFER_SIZE})")
        else:
            print(f"⚠ [Buffer] Buffer lleno! Descartando mensaje")
        return False

# ==================== EDGE COMPUTING ====================
def calculate_statistics(readings):
    """Calcula estadísticas de lecturas"""
    if not readings:
        return None
    
    temps = [r['temperatura'] for r in readings]
    
    return {
        'count': len(temps),
        'avg': round(statistics.mean(temps), 2),
        'min': round(min(temps), 2),
        'max': round(max(temps), 2),
        'std': round(statistics.stdev(temps), 2) if len(temps) > 1 else 0
    }

def periodic_aggregation():
    """Thread que envía agregación periódica"""
    while True:
        time.sleep(AGGREGATION_INTERVAL)
        
        if not device_buffer:
            continue
        
        # Crear mensaje de agregación
        aggregation = {
            'gateway_id': 'rpi_zero_alpha',
            'timestamp': time.time(),
            'timestamp_iso': datetime.now().isoformat(),
            'devices': []
        }
        
        for device_id, readings in device_buffer.items():
            if readings:
                stats_dev = calculate_statistics(readings)
                aggregation['devices'].append({
                    'device_id': device_id,
                    'statistics': stats_dev,
                    'last_reading': readings[-1]
                })
        
        # Publicar al broker
        topic = f"{MQTT_BASE_TOPIC}/aggregate"
        payload = json.dumps(aggregation)
        
        if publish_to_mqtt(topic, payload):
            print(f"📊 [Edge] Agregación enviada: {len(aggregation['devices'])} dispositivos")

# ==================== ENDPOINTS FLASK ====================
@app.route('/health', methods=['GET'])
def health():
    """Estado de salud del gateway"""
    uptime = time.time() - stats['start_time']
    
    return jsonify({
        'status': 'online',
        'gateway_id': 'rpi_zero_alpha',
        'uptime_seconds': round(uptime, 2),
        'mqtt_connected': mqtt_connected,
        'devices_registered': len(stats['devices_registered']),
        'messages_received': stats['messages_received'],
        'messages_sent': stats['messages_sent'],
        'messages_buffered': stats['messages_buffered'],
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/gateway/data', methods=['POST'])
def receive_data():
    """
    Recibe datos de ESP32
    
    Esperado:
    {
        "device_id": "esp32_1",
        "temperatura": 23.5,
        "timestamp": 1234567890
    }
    """
    stats['messages_received'] += 1
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON provided'}), 400
        
        device_id = data.get('device_id')
        if not device_id:
            return jsonify({'error': 'device_id required'}), 400
        
        # Registrar dispositivo
        stats['devices_registered'].add(device_id)
        
        # Agregar timestamp del gateway
        data['gateway_timestamp'] = time.time()
        data['gateway_received_at'] = datetime.now().isoformat()
        
        # Almacenar en buffer local (Edge)
        device_buffer[device_id].append(data)
        
        # Mantener solo últimas 100 lecturas
        if len(device_buffer[device_id]) > 100:
            device_buffer[device_id].pop(0)
        
        # Reenviar individualmente al broker MQTT
        topic = f"{MQTT_BASE_TOPIC}/devices/{device_id}/data"
        payload = json.dumps(data)
        success = publish_to_mqtt(topic, payload)
        
        # Log
        temp = data.get('temperatura', 'N/A')
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {device_id}: {temp}°C → {'✓ MQTT' if success else '⊙ Buffer'}")
        
        return jsonify({
            'status': 'success' if success else 'buffered',
            'device_id': device_id,
            'mqtt_connected': mqtt_connected,
            'messages_buffered': len(offline_buffer)
        }), 200 if success else 202
    
    except Exception as e:
        print(f"✗ [Error] {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/gateway/devices', methods=['GET'])
def list_devices():
    """Lista dispositivos registrados"""
    devices_info = []
    
    for device_id in stats['devices_registered']:
        readings = device_buffer.get(device_id, [])
        if readings:
            last = readings[-1]
            devices_info.append({
                'device_id': device_id,
                'last_temperature': last.get('temperatura'),
                'last_seen': last.get('gateway_received_at'),
                'reading_count': len(readings)
            })
    
    return jsonify({
        'device_count': len(devices_info),
        'devices': devices_info
    }), 200

@app.route('/gateway/aggregate', methods=['GET'])
def get_aggregate():
    """Retorna agregación actual (sin enviar a MQTT)"""
    aggregation = {}
    
    for device_id, readings in device_buffer.items():
        if readings:
            aggregation[device_id] = {
                'statistics': calculate_statistics(readings),
                'last_reading': readings[-1]
            }
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'aggregation': aggregation
    }), 200

# ==================== MAIN ====================
if __name__ == '__main__':
    print("=" * 70)
    print("  GATEWAY IoT - Raspberry Pi Zero W")
    print("  Práctica 5C")
    print("=" * 70)
    print(f"  Flask (HTTP local): {FLASK_HOST}:{FLASK_PORT}")
    print(f"  MQTT (servidor): {MQTT_BROKER}:{MQTT_PORT}")
    print(f"  Agregación cada: {AGGREGATION_INTERVAL} segundos")
    print("=" * 70)
    print()
    
    # Conectar a MQTT
    connect_mqtt()
    
    # Iniciar thread de agregación periódica
    agg_thread = threading.Thread(target=periodic_aggregation, daemon=True)
    agg_thread.start()
    
    # Iniciar servidor Flask
    print(f"[Flask] Iniciando servidor HTTP...")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False)
```

### 2.2 Ejecutar el gateway

```bash
chmod +x gateway.py
python3 gateway.py
```

**Salida esperada:**
```
======================================================================
  GATEWAY IoT - Raspberry Pi Zero W
  Práctica 5C
======================================================================
  Flask (HTTP local): 0.0.0.0:5000
  MQTT (servidor): devlabs.eium.com.mx:3000
  Agregación cada: 30 segundos
======================================================================

[MQTT] Intentando conexión a devlabs.eium.com.mx:3000
✓ [MQTT] Conectado al broker devlabs.eium.com.mx:3000
[Flask] Iniciando servidor HTTP...
 * Running on http://0.0.0.0:5000
```

---

## PARTE 3: ADAPTACIÓN DEL CÓDIGO ESP32

### 3.1 Código ESP32 para gateway (Integrante 3 - Todos programan)

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ==================== CONFIGURACIÓN ====================
const char* WIFI_SSID = "RED_LAB";
const char* WIFI_PASSWORD = "PASSWORD";

// IP de la Raspberry Pi (gateway)
const char* GATEWAY_IP = "192.168.X.X";  // ¡CAMBIAR POR IP REAL!
const int GATEWAY_PORT = 5000;

const char* DEVICE_ID = "esp32_1";  // CAMBIAR: esp32_1, esp32_2, ..., esp32_5

// ==================== VARIABLES ====================
unsigned long lastPostTime = 0;
const unsigned long POST_INTERVAL = 5000;  // POST cada 5 segundos
int messageCounter = 0;
float temperatureOffset = 0;

// ==================== CONECTAR WiFi ====================
void conectarWiFi() {
  Serial.println("\n[WiFi] Conectando...");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[WiFi] ✓ Conectado");
    Serial.printf("[WiFi] IP: %s\n", WiFi.localIP().toString().c_str());
    Serial.printf("[WiFi] RSSI: %d dBm\n", WiFi.RSSI());
  } else {
    Serial.println("\n[WiFi] ✗ Error");
    ESP.restart();
  }
}

// ==================== POST AL GATEWAY ====================
void postToGateway() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[HTTP] ✗ WiFi desconectado");
    return;
  }
  
  HTTPClient http;
  
  // URL del gateway LOCAL
  String url = "http://" + String(GATEWAY_IP) + ":" + String(GATEWAY_PORT) + "/gateway/data";
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(5000);
  
  // Simular temperatura
  float temp = 20.0 + temperatureOffset + random(-20, 30) / 10.0;
  
  // JSON
  StaticJsonDocument<256> doc;
  doc["device_id"] = DEVICE_ID;
  doc["temperatura"] = round(temp * 100) / 100.0;
  doc["timestamp"] = millis() / 1000;
  doc["seq"] = messageCounter;
  
  String payload;
  serializeJson(doc, payload);
  
  // POST
  unsigned long start = millis();
  int httpCode = http.POST(payload);
  unsigned long latency = millis() - start;
  
  Serial.println("\n[HTTP] → POST al Gateway");
  Serial.printf("  URL: %s\n", url.c_str());
  Serial.printf("  Payload: %s\n", payload.c_str());
  Serial.printf("  Código HTTP: %d\n", httpCode);
  Serial.printf("  Latencia: %lu ms\n", latency);
  
  if (httpCode == 200) {
    String response = http.getString();
    Serial.println("  ✓ Dato enviado al gateway (reenviado a MQTT)");
    
    // Parsear respuesta para ver si MQTT está conectado
    StaticJsonDocument<256> respDoc;
    deserializeJson(respDoc, response);
    bool mqttConnected = respDoc["mqtt_connected"];
    
    Serial.printf("  MQTT central: %s\n", mqttConnected ? "✓ Conectado" : "✗ Desconectado");
    
    messageCounter++;
  } else if (httpCode == 202) {
    Serial.println("  ⊙ Dato en buffer del gateway (MQTT offline)");
    messageCounter++;
  } else {
    Serial.printf("  ✗ Error: %s\n", http.errorToString(httpCode).c_str());
  }
  
  http.end();
}

// ==================== SETUP ====================
void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n========================================");
  Serial.println("  ESP32 - Gateway Mode");
  Serial.println("  Device: " + String(DEVICE_ID));
  Serial.println("  Gateway: " + String(GATEWAY_IP));
  Serial.println("========================================");
  
  // Offset de temperatura único
  if (String(DEVICE_ID) == "esp32_1") temperatureOffset = 0.0;
  else if (String(DEVICE_ID) == "esp32_2") temperatureOffset = 1.5;
  else if (String(DEVICE_ID) == "esp32_3") temperatureOffset = 3.0;
  else if (String(DEVICE_ID) == "esp32_4") temperatureOffset = 4.5;
  else if (String(DEVICE_ID) == "esp32_5") temperatureOffset = 6.0;
  
  conectarWiFi();
  
  Serial.println("\n[Sistema] Listo\n");
}

// ==================== LOOP ====================
void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    conectarWiFi();
  }
  
  unsigned long now = millis();
  if (now - lastPostTime >= POST_INTERVAL) {
    postToGateway();
    lastPostTime = now;
  }
  
  delay(10);
}
```

**IMPORTANTE:** Cambiar `GATEWAY_IP` por la IP real de la Raspberry Pi (obtenida con `hostname -I`).

---

## PARTE 4: EXPERIMENTOS

### 4.1 Experimento 1: Funcionamiento normal

**Objetivo:** Verificar flujo completo ESP32 → Gateway → Servidor

**Procedimiento:**
1. Gateway corriendo en Raspberry Pi
2. Broker MQTT corriendo en devlabs
3. Los 5 ESP32 enviando datos al gateway
4. Monitor MQTT en servidor:
   ```bash
   mosquitto_sub -h localhost -p 3000 -t "gateway/alpha/#" -v
   ```

**Observar:**
- Datos individuales llegando: `gateway/alpha/devices/esp32_X/data`
- Agregación cada 30 seg: `gateway/alpha/aggregate`

**Registrar:**
- Latencia ESP32 → Gateway: ____ ms
- Latencia total ESP32 → Servidor: ____ ms

### 4.2 Experimento 2: Edge Computing (Agregación)

**Objetivo:** Demostrar procesamiento edge

**Procedimiento:**
1. Los 5 ESP32 activos
2. Consultar endpoint de agregación local:
   ```bash
   curl http://<IP_RASPBERRY>:5000/gateway/aggregate | python3 -m json.tool
   ```

**Observar:**
- Estadísticas calculadas localmente (promedio, min, max, std)
- Comparar con tener que calcular esto en el servidor

**Análisis:**
- ¿Cuántos mensajes individuales se evitan con 1 agregación cada 30s?
- Con 100 dispositivos, ¿cuánto ancho de banda se ahorraría?

### 4.3 Experimento 3: Tolerancia a fallos

**Objetivo:** Evaluar buffering local cuando Internet falla

**Procedimiento:**

**Fase 1: Desconectar Internet del gateway**
```bash
# En la Raspberry Pi, deshabilitar WiFi WAN (simular fallo de Internet)
sudo ifconfig wlan0 down
```

**Fase 2: ESP32s siguen enviando**
- Los 5 ESP32 siguen enviando al gateway cada 5 segundos
- Gateway almacena en buffer local

**Fase 3: Verificar buffer**
```bash
# Desde red local
curl http://<IP_RASPBERRY>:5000/health
```

Observar: `messages_buffered` debe aumentar

**Fase 4: Reconectar Internet**
```bash
sudo ifconfig wlan0 up
```

**Fase 5: Observar recuperación**
- Gateway debe enviar todos los mensajes del buffer automáticamente
- Monitor MQTT debe mostrar ráfaga de mensajes

**Registrar:**
- Tiempo en modo offline: ____ segundos
- Mensajes almacenados en buffer: ____
- Tiempo de recuperación (envío de buffer): ____ segundos
- ¿Algún mensaje se perdió? SÍ / NO

### 4.4 Experimento 4: Comparación de latencias

**Objetivo:** Comparar latencia end-to-end en las 3 arquitecturas

**Metodología:**
1. Modificar código ESP32 para medir tiempo desde envío hasta confirmación
2. Ejecutar cada arquitectura 20 veces
3. Calcular estadísticas

**Tabla de resultados:**

| Arquitectura | Latencia promedio (ms) | Latencia mínima | Latencia máxima | Desv. estándar |
|--------------|------------------------|-----------------|-----------------|----------------|
| MQTT directo (5A) | | | | |
| REST directo (5B) | | | | |
| Gateway (5C) | | | | |

**Análisis:**
- ¿Cuánta latencia adicional introduce el gateway?
- ¿Es aceptable para aplicaciones IoT típicas?

---

## 7. PREGUNTAS DE REFLEXIÓN

### 7.1 Sobre el Gateway

1. **¿Cuáles son las principales ventajas del gateway observadas en los experimentos?**
   - Edge computing
   - Tolerancia a fallos
   - Reducción de tráfico

2. **¿El gateway es un punto único de fallo? ¿Cómo mitigar este riesgo?**
   - Proponer estrategias de redundancia
   - Gateways backup, health monitoring

3. **¿Qué tipos de procesamiento edge son adecuados para un gateway?**
   - Agregación estadística
   - Filtrado de ruido
   - Detección de anomalías
   - ¿Qué NO es adecuado? (Ej: ML intensivo)

### 7.2 Sobre arquitectura

4. **¿En qué escenarios recomendarían usar gateway vs comunicación directa?**
   - Dispositivos con conectividad limitada
   - Necesidad de procesamiento local
   - Reducción de costos de datos celulares

5. **Diseñar una arquitectura híbrida:**
   - Algunos dispositivos → Gateway
   - Otros dispositivos → Directo al servidor
   - Justificar cuáles van por dónde

### 7.3 Comparación final

6. **Tabla comparativa de las 3 arquitecturas (datos experimentales):**

| Criterio | MQTT Directo | REST Directo | Gateway |
|----------|--------------|--------------|---------|
| Latencia (ms) | | | |
| Overhead (bytes) | | | |
| Tiempo real | ✓ | ✗ | ✓ |
| Edge computing | ✗ | ✗ | ✓ |
| Tolerancia a fallos servidor | ✗ | ✗ | ✓ |
| Complejidad | Media | Baja | Alta |
| Escalabilidad | | | |
| Mejor para... | ? | ? | ? |

7. **Caso práctico: Sistema de monitoreo agrícola**
   - 50 sensores en campo (temperatura, humedad, pH del suelo)
   - Sin conectividad celular confiable
   - Necesidad de alertas locales (ej: riego automático)
   - Datos históricos en la nube
   
   **Diseñar arquitectura completa:**
   - ¿Usar gateway? Justificar
   - ¿Qué protocolo usar entre sensores y gateway?
   - ¿Qué procesamiento hacer en el gateway?
   - ¿Qué protocolo usar entre gateway y servidor?

---

## 8. ENTREGABLES

### 8.1 Reporte completo

- Portada con integrantes y roles
- Introducción teórica sobre gateways IoT
- Desarrollo:
  - Código del gateway (Python) comentado
  - Código ESP32 adaptado
  - Capturas de configuración Raspberry Pi
- Experimentos:
  - Evidencia de los 4 experimentos
  - Tablas de mediciones con datos reales
  - Gráficas de latencia
- Comparación de las 3 arquitecturas (5A, 5B, 5C)
- Respuestas a preguntas de reflexión
- Diagrama de arquitectura con gateway
- Caso práctico resuelto
- Conclusiones individuales y grupales

### 8.2 Evidencias específicas

- Fotografía del montaje físico (Raspberry Pi + ESP32)
- Captura del endpoint `/health` del gateway
- Logs del gateway mostrando recepción de múltiples ESP32
- Captura de mensajes de agregación cada 30s
- Evidencia de buffer funcionando (Experimento 3)
- Monitor MQTT mostrando datos llegando vía gateway

---

## 9. CRITERIOS DE EVALUACIÓN

**Total: 100 puntos**

| Criterio | Puntos |
|----------|--------|
| Gateway funcional (Python) | 25 |
| ESP32 adaptado correctamente | 15 |
| Experimentos completos | 25 |
| Comparación 3 arquitecturas | 20 |
| Respuestas y caso práctico | 10 |
| Formato y documentación | 5 |

---

## 10. CONSIDERACIONES FINALES

### 10.1 Tiempo estimado
- Configuración Raspberry Pi: 1.5 horas
- Programación gateway: 2 horas
- Adaptación ESP32: 1 hora
- Pruebas y debugging: 1.5 horas
- Experimentos: 2 horas
- Comparación y reporte: 2 horas
- **Total: 10 horas**

### 10.2 Troubleshooting común

**Problema:** ESP32 no se conecta al gateway
- Verificar que ESP32 y Raspberry Pi estén en la misma red WiFi
- Verificar IP de Raspberry Pi: `hostname -I`
- Ping desde ESP32 (usar código de prueba)

**Problema:** Gateway no conecta a MQTT
- Verificar que broker esté corriendo en devlabs
- Verificar puerto 3000
- Ver logs del gateway para errores

**Problema:** Raspberry Pi muy lenta
- Es normal, tiene solo 512MB RAM
- No correr aplicaciones innecesarias
- Usar Raspbian Lite (sin GUI)

### 10.3 Mejoras opcionales (+bonificación)

- Implementar autenticación HTTP básica
- Usar base de datos SQLite en gateway
- Dashboard web local en el gateway
- Múltiples protocolos (BLE + WiFi)
- Implementar MQTT también en ESP32 → Gateway

---

**Fecha de entrega:** [A definir]  
**Formato:** `Practica05C_Gateway_EquipoX.pdf`

---

*Universidad Modelo EIUM*  
*Práctica 5C: Arquitectura con Gateway*
