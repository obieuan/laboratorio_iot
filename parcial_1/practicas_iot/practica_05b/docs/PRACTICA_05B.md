# PRÁCTICA DE LABORATORIO No. 5B
## COMUNICACIÓN IoT REQUEST/RESPONSE: API REST

---

## MODALIDAD DE TRABAJO

**Equipos:** 5 integrantes por equipo

**Recursos compartidos:**
- 1 laboratorio virtual por equipo (el mismo de la Práctica 5A)

**Recursos individuales:**
- 1 ESP32 (Node32) por integrante

---

## 1. OBJETIVO GENERAL

Implementar y analizar un sistema de comunicación IoT basado en el paradigma request/response utilizando una API REST, evaluando su comportamiento en términos de latencia, sincronización y eficiencia al gestionar múltiples dispositivos mediante polling.

---

## 2. OBJETIVOS ESPECÍFICOS

1. Desarrollar una API REST completa en Python (Flask) que gestione datos de múltiples dispositivos IoT simultáneamente.

2. Implementar clientes HTTP en ESP32 que envíen datos mediante solicitudes POST a la API.

3. Observar y documentar el comportamiento síncrono del modelo request/response.

4. Implementar y evaluar estrategias de polling para obtener datos en tiempo cuasi-real.

5. Comparar experimentalmente la arquitectura REST con MQTT (Práctica 5A) en términos de latencia, overhead y escalabilidad.

---

## 3. INTRODUCCIÓN TEÓRICA

### 3.1 Paradigma Request/Response

El modelo request/response es el fundamento de las arquitecturas web tradicionales. En este paradigma, la comunicación siempre es iniciada por el cliente mediante una solicitud (request), y el servidor responde con los datos solicitados. Este modelo es inherentemente síncrono: el cliente debe esperar la respuesta del servidor antes de continuar.

**Características principales:**
- **Stateless:** Cada solicitud es independiente y contiene toda la información necesaria
- **Cliente-iniciada:** El servidor nunca inicia comunicación espontáneamente
- **Síncrona:** El cliente bloquea esperando respuesta (o maneja asíncronamente)

### 3.2 REST: Representational State Transfer

REST es un estilo arquitectónico definido por Roy Fielding en 2000 que establece principios para diseñar servicios web escalables.

**Principios REST:**

1. **Cliente-Servidor:** Separación de responsabilidades entre frontend y backend
2. **Stateless:** El servidor no mantiene estado de sesión del cliente
3. **Cacheable:** Las respuestas deben indicar si pueden ser cacheadas
4. **Interfaz uniforme:** URLs predecibles, uso estándar de verbos HTTP
5. **Sistema en capas:** Arquitectura puede incluir proxies, load balancers, etc.

### 3.3 Verbos HTTP en REST

REST utiliza los verbos HTTP para indicar operaciones CRUD:

| Verbo HTTP | Operación | Uso en IoT |
|------------|-----------|------------|
| **GET** | Leer | Consultar datos de sensores, obtener configuración |
| **POST** | Crear | Enviar nuevas lecturas de sensores |
| **PUT** | Actualizar (completo) | Actualizar configuración completa de dispositivo |
| **PATCH** | Actualizar (parcial) | Modificar parámetro específico |
| **DELETE** | Eliminar | Eliminar datos antiguos, desregistrar dispositivo |

En esta práctica nos enfocaremos principalmente en **POST** (para que ESP32 envíe datos) y **GET** (para consultar datos).

### 3.4 Estructura de una API REST

Una API REST bien diseñada sigue convenciones claras:

**Ejemplo de endpoints:**
```
GET    /devices                    # Lista todos los dispositivos
GET    /devices/{id}               # Obtiene datos de un dispositivo específico
POST   /devices/{id}/data          # Envía nueva lectura de un dispositivo
GET    /devices/{id}/data          # Obtiene histórico de lecturas
GET    /devices/{id}/data/latest   # Obtiene última lectura
GET    /stats                      # Obtiene estadísticas agregadas
```

**Códigos de estado HTTP comunes:**
- **200 OK:** Solicitud exitosa
- **201 Created:** Recurso creado exitosamente (POST)
- **400 Bad Request:** Error en la solicitud del cliente
- **404 Not Found:** Recurso no encontrado
- **500 Internal Server Error:** Error del servidor

### 3.5 El problema del "Tiempo Real" en REST

REST no fue diseñado para comunicación en tiempo real. Para simular tiempo real, existen estrategias:

**1. Polling (Consulta periódica):**
```
┌─────────┐              ┌─────────┐
│ Cliente │              │ Servidor│
└────┬────┘              └────┬────┘
     │   GET /data            │
     │───────────────────────>│
     │   200 OK + datos       │
     │<───────────────────────│
     │                        │
     │ (espera 5 segundos)    │
     │                        │
     │   GET /data            │
     │───────────────────────>│
     │   200 OK + datos       │
     │<───────────────────────│
```

**Ventajas:** Simple de implementar  
**Desventajas:** Desperdicio de ancho de banda, latencia inherente

**2. Long Polling:**
El servidor mantiene la conexión abierta hasta tener datos nuevos.

**3. Server-Sent Events (SSE):**
El servidor puede enviar múltiples mensajes sobre una sola conexión HTTP.

**4. WebSockets:**
Conexión bidireccional persistente (ya no es REST puro).

En esta práctica implementaremos **polling tradicional** y evaluaremos su efectividad.

### 3.6 Comparación conceptual: MQTT vs REST

| Aspecto | MQTT (Práctica 5A) | REST API (Práctica 5B) |
|---------|-------------------|----------------------|
| **Modelo** | Publish/Subscribe | Request/Response |
| **Iniciativa** | Bidireccional (push/pull) | Unidireccional (client-pull) |
| **Conexión** | Persistente | Por solicitud |
| **Overhead** | Mínimo (~2 bytes) | Alto (~100-200 bytes) |
| **Tiempo real** | Nativo (push) | Simulado (polling) |
| **Complejidad** | Media (broker requerido) | Baja (servidor HTTP simple) |
| **Escalabilidad** | Excelente | Buena (con caching) |
| **Debugging** | Requiere tools especiales | Fácil (navegador, curl) |

---

## 4. MATERIALES Y HERRAMIENTAS

### 4.1 Hardware (igual que Práctica 5A)
- **5 ESP32 (Node32)** con conectividad WiFi
- **Cables USB** para programación
- **5 computadoras** con puerto USB

### 4.2 Software y accesos
- **Arduino IDE o PlatformIO** configurado para ESP32
- **Acceso SSH al mismo laboratorio virtual** de Práctica 5A
- **Navegador web** (para probar endpoints)
- **Postman o similar** (opcional, para pruebas avanzadas)

### 4.3 Bibliotecas para ESP32
- `WiFi.h` - Conectividad WiFi
- `HTTPClient.h` - Cliente HTTP para hacer requests
- `ArduinoJson.h` - Manejo de JSON

### 4.4 Software para el servidor
- **Python 3** (ya instalado en el laboratorio)
- **Flask:** Framework web minimalista
- **Flask-CORS:** Para permitir requests desde diferentes orígenes

---

## 5. ARQUITECTURA DEL SISTEMA

### 5.1 Distribución de puertos

Para esta práctica utilizaremos:

| Puerto | Servicio | Descripción |
|--------|----------|-------------|
| 3000 | (Mosquitto de Práctica 5A) | No usar en esta práctica |
| **3001** | **API REST Flask** | Servidor HTTP principal |
| 3002 | Dashboard web (opcional) | Visualización de datos |

### 5.2 Diagrama de arquitectura

```
┌──────────┐                           ┌────────────────────────┐
│  ESP32_1 │─┐                         │  devlabs.eium.com.mx   │
└──────────┘ │                         │                        │
┌──────────┐ │  POST /devices/{id}/data│  ┌──────────────────┐ │
│  ESP32_2 │─┤─────────────────────────┼─>│   Flask API      │ │
└──────────┘ │                         │  │   Puerto 3001    │ │
┌──────────┐ │                         │  │                  │ │
│  ESP32_3 │─┤                         │  │  Endpoints:      │ │
└──────────┘ │                         │  │  - POST /data    │ │
┌──────────┐ │                         │  │  - GET /devices  │ │
│  ESP32_4 │─┤                         │  │  - GET /summary  │ │
└──────────┘ │                         │  │  - GET /stats    │ │
┌──────────┐ │                         │  └──────────────────┘ │
│  ESP32_5 │─┘                         │                        │
└──────────┘                           │  ┌──────────────────┐ │
                                       │  │   Almacenamiento │ │
┌──────────────┐  GET /summary         │  │   en memoria     │ │
│  Navegador/  │<──────────────────────┼──│  (dict/list)     │ │
│   Cliente    │                       │  └──────────────────┘ │
└──────────────┘                       └────────────────────────┘
     ↑                                           
     │  Polling cada N segundos                 
     └──────────────────────────────────────────
```

---

## 6. DESARROLLO DE LA PRÁCTICA

### Organización del trabajo en equipo

**Roles para esta práctica:**

| Rol | Responsable | Tareas principales |
|-----|-------------|-------------------|
| **Desarrollador API** | Integrante 1 | Desarrollar API Flask, definir endpoints |
| **Desarrollador ESP32** | Integrante 2 | Implementar cliente HTTP en ESP32 |
| **Tester y QA** | Integrante 3 | Probar endpoints, implementar cliente de polling |
| **Analista de datos** | Integrante 4 | Analizar latencias, comparar con MQTT |
| **Documentador** | Integrante 5 | Capturar evidencias, documentar experimentos |

---

## PARTE 1: DESARROLLO DE LA API REST

### 1.1 Instalación de dependencias (Integrante 1)

**Paso 1:** Conectarse al laboratorio virtual:
```bash
ssh -p 2200 usuario@devlabs.eium.com.mx
```

**Paso 2:** Instalar Flask y dependencias:
```bash
sudo apt install python3-pip -y
pip3 install flask flask-cors
```

**Paso 3:** Crear directorio para la API:
```bash
mkdir ~/api_rest
cd ~/api_rest
```

### 1.2 Implementación de la API completa

**Crear archivo `app.py`:**

```bash
nano app.py
```

```python
#!/usr/bin/env python3
"""
API REST para Práctica 5B - Comunicación IoT
Maneja datos de múltiples dispositivos ESP32
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from collections import defaultdict
import time
import statistics

app = Flask(__name__)
CORS(app)  # Permitir requests desde cualquier origen

# ==================== ALMACENAMIENTO ====================
# Estructura: {device_id: [lista de lecturas]}
device_data = defaultdict(list)

# Límite de lecturas almacenadas por dispositivo
MAX_READINGS_PER_DEVICE = 100

# Estadísticas globales
stats_global = {
    'total_requests': 0,
    'requests_by_device': defaultdict(int),
    'api_start_time': time.time()
}

# ==================== UTILIDADES ====================
def get_timestamp():
    """Retorna timestamp ISO 8601"""
    return datetime.now().isoformat()

def calculate_device_stats(readings):
    """Calcula estadísticas de lecturas de un dispositivo"""
    if not readings:
        return None
    
    temperatures = [r['temperatura'] for r in readings if 'temperatura' in r]
    
    if not temperatures:
        return None
    
    return {
        'count': len(temperatures),
        'avg': round(statistics.mean(temperatures), 2),
        'min': round(min(temperatures), 2),
        'max': round(max(temperatures), 2),
        'std': round(statistics.stdev(temperatures), 2) if len(temperatures) > 1 else 0
    }

# ==================== ENDPOINT: ROOT ====================
@app.route('/', methods=['GET'])
def root():
    """Información básica de la API"""
    uptime = time.time() - stats_global['api_start_time']
    
    return jsonify({
        'api': 'IoT REST API - Práctica 5B',
        'version': '1.0',
        'status': 'online',
        'uptime_seconds': round(uptime, 2),
        'total_requests': stats_global['total_requests'],
        'devices_registered': len(device_data),
        'timestamp': get_timestamp()
    }), 200

# ==================== ENDPOINT: POST DATA ====================
@app.route('/devices/<device_id>/data', methods=['POST'])
def post_device_data(device_id):
    """
    Recibe datos de un dispositivo específico
    
    Esperado JSON:
    {
        "temperatura": 23.5,
        "timestamp": 1234567890
    }
    """
    stats_global['total_requests'] += 1
    stats_global['requests_by_device'][device_id] += 1
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Validar que venga temperatura
        if 'temperatura' not in data:
            return jsonify({'error': 'temperatura field required'}), 400
        
        # Agregar metadata del servidor
        reading = {
            'device_id': device_id,
            'temperatura': float(data['temperatura']),
            'timestamp_device': data.get('timestamp', 0),
            'timestamp_server': time.time(),
            'received_at': get_timestamp()
        }
        
        # Almacenar (mantener solo últimas MAX_READINGS)
        device_data[device_id].append(reading)
        if len(device_data[device_id]) > MAX_READINGS_PER_DEVICE:
            device_data[device_id].pop(0)  # Eliminar la más antigua
        
        # Log en consola del servidor
        print(f"[{get_timestamp()}] POST from {device_id}: {data['temperatura']}°C")
        
        return jsonify({
            'status': 'success',
            'device_id': device_id,
            'reading_number': len(device_data[device_id]),
            'timestamp': get_timestamp()
        }), 201
    
    except Exception as e:
        print(f"Error processing POST: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== ENDPOINT: GET DEVICE DATA ====================
@app.route('/devices/<device_id>/data', methods=['GET'])
def get_device_data(device_id):
    """
    Obtiene histórico de lecturas de un dispositivo
    
    Query params:
    - limit: número máximo de lecturas a retornar (default: 10)
    """
    stats_global['total_requests'] += 1
    
    if device_id not in device_data:
        return jsonify({'error': f'Device {device_id} not found'}), 404
    
    # Obtener parámetro limit
    limit = request.args.get('limit', default=10, type=int)
    limit = min(limit, MAX_READINGS_PER_DEVICE)  # No más que el máximo
    
    # Retornar últimas N lecturas (más recientes primero)
    readings = device_data[device_id][-limit:][::-1]
    
    return jsonify({
        'device_id': device_id,
        'count': len(readings),
        'limit': limit,
        'total_readings': len(device_data[device_id]),
        'data': readings
    }), 200

# ==================== ENDPOINT: GET LATEST ====================
@app.route('/devices/<device_id>/data/latest', methods=['GET'])
def get_latest_data(device_id):
    """Obtiene la lectura más reciente de un dispositivo"""
    stats_global['total_requests'] += 1
    
    if device_id not in device_data or len(device_data[device_id]) == 0:
        return jsonify({'error': f'No data for device {device_id}'}), 404
    
    latest = device_data[device_id][-1]
    
    return jsonify({
        'device_id': device_id,
        'latest_reading': latest
    }), 200

# ==================== ENDPOINT: GET ALL DEVICES ====================
@app.route('/devices', methods=['GET'])
def get_all_devices():
    """Lista todos los dispositivos registrados con su última lectura"""
    stats_global['total_requests'] += 1
    
    devices_list = []
    
    for device_id, readings in device_data.items():
        if readings:
            latest = readings[-1]
            devices_list.append({
                'device_id': device_id,
                'last_temperature': latest.get('temperatura'),
                'last_seen': latest.get('received_at'),
                'total_readings': len(readings)
            })
    
    return jsonify({
        'count': len(devices_list),
        'devices': sorted(devices_list, key=lambda x: x['device_id'])
    }), 200

# ==================== ENDPOINT: GET SUMMARY ====================
@app.route('/summary', methods=['GET'])
def get_summary():
    """Resumen consolidado de todos los dispositivos"""
    stats_global['total_requests'] += 1
    
    summary = []
    
    for device_id in sorted(device_data.keys()):
        readings = device_data[device_id]
        if readings:
            latest = readings[-1]
            device_stats = calculate_device_stats(readings)
            
            summary.append({
                'device_id': device_id,
                'latest_temperature': latest.get('temperatura'),
                'last_seen': latest.get('received_at'),
                'statistics': device_stats
            })
    
    return jsonify({
        'timestamp': get_timestamp(),
        'devices_count': len(summary),
        'devices': summary
    }), 200

# ==================== ENDPOINT: GET STATS ====================
@app.route('/stats', methods=['GET'])
def get_stats():
    """Estadísticas generales del sistema"""
    stats_global['total_requests'] += 1
    
    uptime = time.time() - stats_global['api_start_time']
    
    # Estadísticas agregadas
    all_temps = []
    for readings in device_data.values():
        all_temps.extend([r['temperatura'] for r in readings if 'temperatura' in r])
    
    system_stats = None
    if all_temps:
        system_stats = {
            'total_readings': len(all_temps),
            'avg_temperature': round(statistics.mean(all_temps), 2),
            'min_temperature': round(min(all_temps), 2),
            'max_temperature': round(max(all_temps), 2),
            'std_temperature': round(statistics.stdev(all_temps), 2) if len(all_temps) > 1 else 0
        }
    
    return jsonify({
        'uptime_seconds': round(uptime, 2),
        'total_requests': stats_global['total_requests'],
        'requests_per_device': dict(stats_global['requests_by_device']),
        'devices_registered': len(device_data),
        'system_statistics': system_stats,
        'timestamp': get_timestamp()
    }), 200

# ==================== ENDPOINT: DELETE DEVICE ====================
@app.route('/devices/<device_id>', methods=['DELETE'])
def delete_device(device_id):
    """Elimina todos los datos de un dispositivo"""
    stats_global['total_requests'] += 1
    
    if device_id not in device_data:
        return jsonify({'error': f'Device {device_id} not found'}), 404
    
    del device_data[device_id]
    
    return jsonify({
        'status': 'success',
        'message': f'Device {device_id} deleted',
        'timestamp': get_timestamp()
    }), 200

# ==================== MAIN ====================
if __name__ == '__main__':
    print("=" * 70)
    print("  API REST - Práctica 5B")
    print("=" * 70)
    print(f"  Puerto: 3001")
    print(f"  Endpoints disponibles:")
    print(f"    GET  /")
    print(f"    POST /devices/<id>/data")
    print(f"    GET  /devices/<id>/data")
    print(f"    GET  /devices/<id>/data/latest")
    print(f"    GET  /devices")
    print(f"    GET  /summary")
    print(f"    GET  /stats")
    print(f"    DELETE /devices/<id>")
    print("=" * 70)
    print()
    
    # Iniciar servidor en puerto 3001 (puerto expuesto del laboratorio)
    app.run(host='0.0.0.0', port=3001, debug=False)
```

**Guardar:** Ctrl+O, Enter, Ctrl+X

### 1.3 Ejecutar la API

```bash
# Dar permisos de ejecución
chmod +x app.py

# Ejecutar (se mantendrá corriendo)
python3 app.py
```

**Salida esperada:**
```
======================================================================
  API REST - Práctica 5B
======================================================================
  Puerto: 3001
  Endpoints disponibles:
    GET  /
    POST /devices/<id>/data
    ...
======================================================================

 * Serving Flask app 'app'
 * Running on http://0.0.0.0:3001
```

### 1.4 Pruebas básicas de la API (Integrante 3 - Tester)

Abrir otra terminal SSH y probar los endpoints:

**Prueba 1: Root endpoint**
```bash
curl http://localhost:3001/
```

**Respuesta esperada:**
```json
{
  "api": "IoT REST API - Práctica 5B",
  "status": "online",
  ...
}
```

**Prueba 2: Enviar datos de prueba**
```bash
curl -X POST http://localhost:3001/devices/esp32_test/data \
  -H "Content-Type: application/json" \
  -d '{"temperatura": 25.5, "timestamp": 123456}'
```

**Respuesta esperada:**
```json
{
  "status": "success",
  "device_id": "esp32_test",
  "reading_number": 1,
  ...
}
```

**Prueba 3: Consultar datos**
```bash
curl http://localhost:3001/devices/esp32_test/data
```

**Prueba 4: Resumen de todos los dispositivos**
```bash
curl http://localhost:3001/summary
```

---

## PARTE 2: IMPLEMENTACIÓN EN ESP32

### 2.1 Código del cliente HTTP (Integrante 2 - Todos deben programarlo)

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ==================== CONFIGURACIÓN ====================
const char* WIFI_SSID = "NOMBRE_RED";           // Cambiar
const char* WIFI_PASSWORD = "PASSWORD";          // Cambiar

const char* API_URL = "http://devlabs.eium.com.mx:3001";
const char* DEVICE_ID = "esp32_1";               // CAMBIAR: esp32_1, esp32_2, ..., esp32_5

// ==================== VARIABLES GLOBALES ====================
unsigned long lastPostTime = 0;
const unsigned long POST_INTERVAL = 3000;  // POST cada 3 segundos
int messageCounter = 0;
float temperatureOffset = 0;

// ==================== FUNCIÓN: Conectar WiFi ====================
void conectarWiFi() {
  Serial.println("\n[WiFi] Conectando a: " + String(WIFI_SSID));
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int intentos = 0;
  while (WiFi.status() != WL_CONNECTED && intentos < 30) {
    delay(500);
    Serial.print(".");
    intentos++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[WiFi] ✓ Conectado");
    Serial.printf("[WiFi] IP: %s\n", WiFi.localIP().toString().c_str());
  } else {
    Serial.println("\n[WiFi] ✗ Error de conexión");
    delay(5000);
    ESP.restart();
  }
}

// ==================== FUNCIÓN: POST Datos ====================
void postDatos() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[HTTP] ✗ WiFi desconectado");
    return;
  }
  
  HTTPClient http;
  
  // Construir URL completa
  String url = String(API_URL) + "/devices/" + String(DEVICE_ID) + "/data";
  
  Serial.println("\n[HTTP] → POST Request");
  Serial.println("  URL: " + url);
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(5000);
  
  // Simular temperatura
  float temperatura = 20.0 + temperatureOffset + random(-20, 30) / 10.0;
  
  // Crear JSON
  StaticJsonDocument<256> doc;
  doc["temperatura"] = round(temperatura * 100) / 100.0;
  doc["timestamp"] = millis() / 1000;
  doc["seq"] = messageCounter;
  
  String jsonPayload;
  serializeJson(doc, jsonPayload);
  
  Serial.println("  Payload: " + jsonPayload);
  
  // Enviar POST
  unsigned long startTime = millis();
  int httpCode = http.POST(jsonPayload);
  unsigned long responseTime = millis() - startTime;
  
  if (httpCode > 0) {
    Serial.printf("  Código HTTP: %d\n", httpCode);
    Serial.printf("  Tiempo de respuesta: %lu ms\n", responseTime);
    
    if (httpCode == 201 || httpCode == 200) {
      String response = http.getString();
      Serial.println("  Respuesta: " + response);
      messageCounter++;
      Serial.println("  ✓ Datos enviados exitosamente");
    } else {
      Serial.println("  ⚠ Código inesperado");
    }
  } else {
    Serial.printf("  ✗ Error: %s\n", http.errorToString(httpCode).c_str());
  }
  
  http.end();
}

// ==================== FUNCIÓN: GET Última Lectura ====================
void getUltimaLectura() {
  if (WiFi.status() != WL_CONNECTED) return;
  
  HTTPClient http;
  String url = String(API_URL) + "/devices/" + String(DEVICE_ID) + "/data/latest";
  
  Serial.println("\n[HTTP] ← GET Request");
  Serial.println("  URL: " + url);
  
  http.begin(url);
  
  int httpCode = http.GET();
  
  if (httpCode == 200) {
    String payload = http.getString();
    Serial.println("  ✓ Respuesta recibida:");
    Serial.println(payload);
    
    // Parsear JSON
    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, payload);
    
    if (!error) {
      float temp = doc["latest_reading"]["temperatura"];
      Serial.printf("  Última temperatura registrada: %.2f°C\n", temp);
    }
  } else {
    Serial.printf("  ✗ Error HTTP: %d\n", httpCode);
  }
  
  http.end();
}

// ==================== SETUP ====================
void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\n========================================");
  Serial.println("  ESP32 - Cliente HTTP REST");
  Serial.println("  Device ID: " + String(DEVICE_ID));
  Serial.println("========================================");
  
  // Configurar offset único
  if (String(DEVICE_ID) == "esp32_1") temperatureOffset = 0.0;
  else if (String(DEVICE_ID) == "esp32_2") temperatureOffset = 1.5;
  else if (String(DEVICE_ID) == "esp32_3") temperatureOffset = 3.0;
  else if (String(DEVICE_ID) == "esp32_4") temperatureOffset = 4.5;
  else if (String(DEVICE_ID) == "esp32_5") temperatureOffset = 6.0;
  
  conectarWiFi();
  
  // Enviar primera lectura inmediatamente
  delay(2000);
  postDatos();
  
  Serial.println("\n[Sistema] Listo\n");
}

// ==================== LOOP ====================
void loop() {
  // Verificar WiFi
  if (WiFi.status() != WL_CONNECTED) {
    conectarWiFi();
  }
  
  // POST periódico
  unsigned long currentTime = millis();
  if (currentTime - lastPostTime >= POST_INTERVAL) {
    postDatos();
    lastPostTime = currentTime;
  }
  
  delay(10);
}
```

### 2.2 Compilar y cargar (Todos los integrantes)

**Pasos:**
1. Cambiar `WIFI_SSID` y `WIFI_PASSWORD`
2. Cambiar `DEVICE_ID` a único (esp32_1, esp32_2, etc.)
3. Compilar y cargar a ESP32
4. Abrir Monitor Serial (115200 baudios)

**Salida esperada:**
```
========================================
  ESP32 - Cliente HTTP REST
  Device ID: esp32_1
========================================

[WiFi] Conectando a: LAB_WIFI
..........
[WiFi] ✓ Conectado
[WiFi] IP: 192.168.1.105

[HTTP] → POST Request
  URL: http://devlabs.eium.com.mx:3001/devices/esp32_1/data
  Payload: {"temperatura":21.34,"timestamp":2,"seq":0}
  Código HTTP: 201
  Tiempo de respuesta: 145 ms
  Respuesta: {"status":"success",...}
  ✓ Datos enviados exitosamente
```

---

## PARTE 3: CLIENTE DE POLLING

### 3.1 Script de consultas periódicas (Integrante 3)

```bash
nano ~/polling_client.py
```

```python
#!/usr/bin/env python3
"""
Cliente de Polling para API REST
Consulta periódicamente el endpoint /summary
"""

import requests
import time
from datetime import datetime
import sys

API_URL = "http://localhost:3001"
POLLING_INTERVAL = 5  # segundos

def limpiar_pantalla():
    print("\033[2J\033[H", end="")  # Limpiar pantalla (Linux/Mac)

def mostrar_resumen():
    try:
        response = requests.get(f"{API_URL}/summary", timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            
            limpiar_pantalla()
            print("=" * 70)
            print(f"  RESUMEN DEL SISTEMA - {datetime.now().strftime('%H:%M:%S')}")
            print("=" * 70)
            print(f"  Dispositivos activos: {data['devices_count']}")
            print("=" * 70)
            
            for device in data['devices']:
                device_id = device['device_id']
                temp = device['latest_temperature']
                last_seen = device['last_seen']
                stats = device.get('statistics', {})
                
                print(f"\n  📡 {device_id}")
                print(f"     Temperatura actual: {temp}°C")
                print(f"     Última actualización: {last_seen}")
                
                if stats:
                    print(f"     Estadísticas:")
                    print(f"       • Lecturas: {stats['count']}")
                    print(f"       • Promedio: {stats['avg']}°C")
                    print(f"       • Rango: [{stats['min']}°C - {stats['max']}°C]")
            
            print("\n" + "=" * 70)
            print(f"  Próxima actualización en {POLLING_INTERVAL} segundos...")
            print("  Presiona Ctrl+C para detener")
            print("=" * 70)
        else:
            print(f"Error HTTP: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    print("Iniciando cliente de polling...")
    print(f"Consultando {API_URL}/summary cada {POLLING_INTERVAL} segundos\n")
    
    try:
        while True:
            mostrar_resumen()
            time.sleep(POLLING_INTERVAL)
    
    except KeyboardInterrupt:
        print("\n\n✓ Cliente de polling detenido")
        sys.exit(0)

if __name__ == "__main__":
    main()
```

**Ejecutar:**
```bash
chmod +x polling_client.py
pip3 install requests
python3 polling_client.py
```

---

## PARTE 4: EXPERIMENTOS Y MEDICIONES

### 4.1 Experimento 1: Escalabilidad con REST

**Objetivo:** Evaluar cómo REST maneja múltiples clientes concurrentes

**Metodología:**
1. Escenario A: Solo ESP32_1 activo
2. Escenario B: ESP32_1, ESP32_2, ESP32_3 activos
3. Escenario C: Todos (1-5) activos

**Mediciones:**
- POST requests/minuto al servidor
- Tiempo de respuesta promedio
- Códigos HTTP de error (si hay)
- CPU del servidor (`htop`)

**Tabla de resultados:**

| Escenario | Dispositivos | POST/min | Tiempo resp. promedio (ms) | Errores | CPU servidor |
|-----------|--------------|----------|---------------------------|---------|--------------|
| A | 1 | | | | |
| B | 3 | | | | |
| C | 5 | | | | |

### 4.2 Experimento 2: Latencia de actualización con Polling

**Objetivo:** Medir cuánto tarda un dato en estar "visible" para el cliente

**Metodología:**
1. ESP32 envía POST con timestamp
2. Cliente de polling consulta GET
3. Medir: tiempo_GET - tiempo_POST = latencia percibida

**Probar con diferentes frecuencias de polling:**
- Polling cada 1 segundo
- Polling cada 5 segundos  
- Polling cada 10 segundos

**Tabla:**

| Frecuencia de polling | Latencia percibida promedio | Requests GET/min | Sensación de "tiempo real" (1-5) |
|-----------------------|-----------------------------|------------------|----------------------------------|
| 1 seg | | | |
| 5 seg | | | |
| 10 seg | | | |

### 4.3 Experimento 3: Overhead de HTTP

**Objetivo:** Cuantificar el overhead del protocolo HTTP comparado con MQTT

**Metodología:**

Usar Wireshark o `tcpdump` para capturar tráfico:

```bash
# En el servidor
sudo tcpdump -i any port 3001 -w /tmp/rest_traffic.pcap
```

**Analizar:**
- Tamaño promedio de request HTTP POST
- Tamaño promedio de response HTTP
- Comparar con MQTT (de Práctica 5A)

### 4.4 Experimento 4: Comparación directa MQTT vs REST

**Objetivo:** Comparación cuantitativa de ambas arquitecturas

**Metodología:**
1. Tener datos de Práctica 5A (MQTT)
2. Ejecutar mismo escenario con REST
3. Comparar métricas directamente

**Tabla comparativa:**

| Métrica | MQTT (Práctica 5A) | REST (Práctica 5B) |
|---------|-------------------|-------------------|
| Latencia promedio (ms) | | |
| Overhead por mensaje (bytes) | | |
| Mensajes/min (5 dispositivos) | | |
| CPU servidor (%) | | |
| ¿Tiempo real nativo? | Sí | No (polling) |
| Complejidad de código cliente | | |

---

## 7. PREGUNTAS DE REFLEXIÓN

### 7.1 Sobre REST y HTTP

1. **¿Qué sucede con los datos enviados por POST si nadie hace GET?**
   - Permanecen almacenados en el servidor
   - Analizar implicaciones de persistencia

2. **¿Por qué REST es inherentemente síncrono?**
   - Explicar el modelo request-response
   - Contrastar con MQTT push

3. **¿Qué papel juegan los códigos de estado HTTP?**
   - Explicar 200, 201, 404, 500
   - ¿Por qué son importantes para debugging?

### 7.2 Sobre polling

4. **¿Cómo afecta la frecuencia de polling a la latencia percibida?**
   - Usar datos del Experimento 2
   - Graficar relación polling vs latencia

5. **¿Cuál es el trade-off entre frecuencia de polling y carga del servidor?**
   - Analizar requests/minuto
   - Discutir escalabilidad

### 7.3 Comparación con MQTT

6. **¿En qué escenarios REST es MEJOR que MQTT?**
   - Simplicidad
   - Debugging
   - Familiaridad del equipo
   - Infraestructura existente

7. **¿En qué escenarios MQTT es MEJOR que REST?**
   - Tiempo real
   - Consumo de ancho de banda
   - Comunicación bidireccional

8. **¿Se puede combinar REST y MQTT en un mismo sistema?**
   - Proponer arquitectura híbrida
   - Definir qué usa cada protocolo

### 7.4 Aplicación práctica

9. **Diseñar un sistema de monitoreo de flota vehicular:**
   - 50 vehículos enviando posición GPS cada 30 seg
   - Dashboard web en tiempo cuasi-real
   - ¿Usar REST o MQTT? Justificar

10. **Proponer mejoras a la API REST desarrollada:**
    - Autenticación
    - Persistencia (base de datos)
    - Paginación
    - Rate limiting

---

## 8. ENTREGABLES

### 8.1 Estructura del reporte

- Portada
- Introducción teórica (resumen REST)
- Desarrollo: Código de API + Código ESP32
- Experimentos: Tablas y gráficas
- Comparación MQTT vs REST
- Respuestas a preguntas
- Diagrama de arquitectura
- Conclusiones
- Referencias

### 8.2 Evidencias específicas

- Logs de la API mostrando POST de los 5 ESP32
- Captura del endpoint `/summary` en navegador
- Logs del Monitor Serial de 3 ESP32
- Output del script de polling
- Mediciones de latencia y overhead
- Tabla comparativa completa MQTT vs REST

---

## 9. CRITERIOS DE EVALUACIÓN

**Total: 100 puntos**

| Criterio | Puntos |
|----------|--------|
| API REST funcional | 25 |
| Código ESP32 (5 dispositivos) | 20 |
| Experimentos completos | 25 |
| Comparación MQTT vs REST | 15 |
| Respuestas a preguntas | 10 |
| Formato y documentación | 5 |

---

## 10. CONSIDERACIONES FINALES

### 10.1 Tiempo estimado
- Desarrollo de API: 2 horas
- Programación ESP32: 1 hora
- Pruebas y debugging: 1 hora
- Experimentos: 2 horas
- Análisis y reporte: 2 horas
- **Total: 8 horas**

### 10.2 Comandos útiles

```bash
# Ver logs de la API
tail -f /path/to/api/logs

# Probar endpoint con curl
curl -X POST http://localhost:3001/devices/test/data \
  -H "Content-Type: application/json" \
  -d '{"temperatura": 25.5}'

# Ver estadísticas
curl http://localhost:3001/stats | python3 -m json.tool
```

---

**Fecha de entrega:** [A definir]  
**Formato:** `Practica05B_REST_EquipoX.pdf`

---

*Universidad Modelo EIUM*  
*Práctica 5B: Comunicación REST*
