# PRÁCTICA DE LABORATORIO No. 5A
## COMUNICACIÓN IoT BASADA EN EVENTOS: PROTOCOLO MQTT

---

## MODALIDAD DE TRABAJO

**Equipos:** 5 integrantes por equipo

**Recursos compartidos:**
- 1 laboratorio virtual por equipo (solicitado en https://devlabs.eium.com.mx)

**Recursos individuales:**
- 1 ESP32 (Node32) por integrante

---

## 1. OBJETIVO GENERAL

Implementar y analizar un sistema de comunicación IoT basado en eventos utilizando el protocolo MQTT, evaluando su comportamiento en tiempo real, escalabilidad y eficiencia al gestionar múltiples dispositivos simultáneamente.

---

## 2. OBJETIVOS ESPECÍFICOS

1. Configurar un broker MQTT (Mosquitto) en un servidor remoto compartido por el equipo.

2. Implementar clientes MQTT en múltiples dispositivos ESP32 que publiquen y se suscriban a topics jerárquicos.

3. Observar y documentar el comportamiento asíncrono y en tiempo real del protocolo MQTT.

4. Evaluar la escalabilidad del sistema MQTT al incrementar el número de dispositivos activos (1, 3, 5 dispositivos).

5. Analizar las ventajas del modelo publicador/suscriptor para aplicaciones IoT distribuidas.

---

## 3. INTRODUCCIÓN TEÓRICA

### 3.1 Paradigma de comunicación basada en eventos

En sistemas IoT, la comunicación basada en eventos (event-driven) permite que los dispositivos publiquen información cuando ocurre un cambio de estado o evento específico. Los consumidores de esta información permanecen suscritos a canales de datos y reciben actualizaciones automáticamente, sin necesidad de solicitudes explícitas. Este modelo es inherentemente asíncrono y habilita comunicación en tiempo real.

### 3.2 MQTT: Message Queuing Telemetry Transport

MQTT es un protocolo de mensajería ligero diseñado específicamente para entornos IoT con restricciones de ancho de banda y dispositivos con recursos limitados. Fue desarrollado por IBM en 1999 y se ha convertido en estándar de facto para comunicación IoT.

**Arquitectura MQTT:**

```
┌─────────────┐      Publish      ┌─────────────┐
│  Publisher  │ ─────────────────→ │             │
│  (ESP32_1)  │                    │             │
└─────────────┘                    │    MQTT     │      Subscribe + Receive
                                   │   Broker    │ ←──────────────────────┐
┌─────────────┐      Publish      │             │                        │
│  Publisher  │ ─────────────────→ │ (Mosquitto) │                        │
│  (ESP32_2)  │                    │             │                        │
└─────────────┘                    └─────────────┘                        │
                                                                          │
                                                                   ┌──────┴──────┐
                                                                   │ Subscriber  │
                                                                   │   (Client)  │
                                                                   └─────────────┘
```

**Componentes principales:**

1. **Broker:** Servidor central que recibe todas las publicaciones y las distribuye a los suscriptores apropiados. Gestiona conexiones, autenticación y enrutamiento de mensajes.

2. **Publisher (Publicador):** Cliente que envía mensajes a topics específicos. No necesita conocer quién recibirá los mensajes.

3. **Subscriber (Suscriptor):** Cliente que se registra para recibir mensajes de topics específicos. Recibe mensajes automáticamente cuando se publican.

4. **Topic:** Cadena jerárquica que actúa como filtro para mensajes. Estructura similar a directorios: `edificio/piso1/salon101/temperatura`

### 3.3 Características clave de MQTT

**1. Modelo Publish/Subscribe:**
- Desacoplamiento entre publicadores y suscriptores
- Comunicación de uno-a-muchos eficiente
- Escalabilidad natural del sistema

**2. Calidad de Servicio (QoS):**
- **QoS 0:** At most once (máximo una vez) - sin garantía de entrega
- **QoS 1:** At least once (al menos una vez) - garantiza entrega, puede duplicarse
- **QoS 2:** Exactly once (exactamente una vez) - garantiza entrega única

**3. Conexión persistente:**
- Conexión TCP/IP de larga duración
- Reduce overhead de establecimiento de conexión
- Permite notificación inmediata de eventos

**4. Mensaje de Last Will (Testamento):**
- El broker puede notificar a otros clientes si un dispositivo se desconecta inesperadamente
- Útil para monitoreo de disponibilidad

**5. Retained Messages:**
- El broker puede almacenar el último mensaje de un topic
- Nuevos suscriptores reciben inmediatamente el último valor conocido

**6. Overhead mínimo:**
- Paquete MQTT mínimo: 2 bytes de encabezado
- Comparado con HTTP: ~100-200 bytes por request

### 3.4 Topics jerárquicos en MQTT

Los topics en MQTT usan estructura jerárquica con separador `/`:

```
Estructura básica:
    organización/ubicación/dispositivo/métrica

Ejemplos:
    universidad/laboratorio/esp32_1/temperatura
    universidad/laboratorio/esp32_1/humedad
    universidad/laboratorio/esp32_2/temperatura
    universidad/comandos/broadcast
    universidad/comandos/esp32_1
```

**Wildcards en suscripciones:**
- **`+`** (single-level): Sustituye un nivel completo
  - `universidad/laboratorio/+/temperatura` → todos los dispositivos en laboratorio
- **`#`** (multi-level): Sustituye todos los niveles subsiguientes
  - `universidad/laboratorio/#` → todo del laboratorio

### 3.5 Ventajas de MQTT para IoT

| Aspecto | Ventaja |
|---------|---------|
| **Ancho de banda** | Overhead mínimo, ideal para redes de bajo ancho de banda |
| **Latencia** | Notificación inmediata de eventos (push model) |
| **Escalabilidad** | Broker maneja eficientemente miles de clientes |
| **Energía** | Conexión persistente reduce consumo vs múltiples conexiones HTTP |
| **Simplicidad** | API simple, fácil de implementar en dispositivos embebidos |
| **Confiabilidad** | Niveles de QoS garantizan entrega según necesidad |

---

## 4. MATERIALES Y HERRAMIENTAS

### 4.1 Hardware por equipo
- **5 ESP32 (Node32)** con conectividad WiFi (uno por integrante)
- **Cables USB** para programación de ESP32
- **5 computadoras** con puerto USB disponible

### 4.2 Software y accesos por equipo
- **Arduino IDE o PlatformIO** configurado para ESP32 (cada integrante)
- **Acceso SSH al laboratorio virtual compartido** (credenciales de https://devlabs.eium.com.mx)
- **Cliente SSH** (PuTTY, Terminal, o similar)
- **Cliente MQTT de pruebas** (MQTT Explorer - opcional pero recomendado)

### 4.3 Bibliotecas para ESP32
- `WiFi.h` - Conectividad WiFi (incluida en ESP32 core)
- `PubSubClient.h` - Cliente MQTT para Arduino (instalar desde Library Manager)
- `ArduinoJson.h` - Manejo de JSON (instalar desde Library Manager)

---

## 5. DESCRIPCIÓN DEL ENTORNO DE LABORATORIO

### 5.1 Solicitud del laboratorio virtual

Cada equipo debe solicitar un laboratorio virtual compartido accediendo a:

**https://devlabs.eium.com.mx**

El sistema proporcionará credenciales similares a:

```
Nombre del lab: lab-equipo1-1770154395140
Creado: 3/2/2026, 3:33:15 p.m.
Imagen: ubuntu:24.04
Tiempo restante: 23h 58m

Acceso SSH:
ssh -p 2200 usuario@devlabs.eium.com.mx
Usuario: usuario
Contraseña: usuario2024

Acceso HTTP/puertos:
http://devlabs.eium.com.mx:3000
Puerto principal: 3000
Puertos expuestos: 3000, 3001, 3002, 3003, 3004
```

**IMPORTANTE:** El laboratorio tiene una duración de 24 horas. Planifiquen adecuadamente el tiempo de trabajo del equipo.

### 5.2 Configuración de puertos para esta práctica

Para esta práctica utilizaremos:

| Puerto | Servicio | Descripción |
|--------|----------|-------------|
| 3000 | Broker MQTT (Mosquitto) | Servidor MQTT principal |
| 3001 | Monitor MQTT (opcional) | Dashboard web simple |
| (otros) | Reservados para prácticas futuras | No usar en esta práctica |

### 5.3 Arquitectura del sistema

```
┌──────────┐
│  ESP32_1 │─┐
└──────────┘ │
┌──────────┐ │
│  ESP32_2 │─┤
└──────────┘ │                                      ┌───────────────────────┐
┌──────────┐ │                                      │  devlabs.eium.com.mx  │
│  ESP32_3 │─┼──→ WiFi ──→ Internet ──→             │                       │
└──────────┘ │                                      │  ┌─────────────────┐  │
┌──────────┐ │                                      │  │ Mosquitto MQTT  │  │
│  ESP32_4 │─┤                                      │  │  Broker :3000   │  │
└──────────┘ │                                      │  └─────────────────┘  │
┌──────────┐ │                                      │                       │
│  ESP32_5 │─┘                                      │  ┌─────────────────┐  │
└──────────┘                                        │  │ Monitor Python  │  │
                                                    │  │   (opcional)    │  │
                                                    │  └─────────────────┘  │
                                                    └───────────────────────┘
```

---

## 6. DESARROLLO DE LA PRÁCTICA

### Organización del trabajo en equipo

**Roles sugeridos:**

| Rol | Responsable | Tareas principales |
|-----|-------------|-------------------|
| **Líder de infraestructura** | Integrante 1 | Configurar broker MQTT, verificar conectividad, resolver problemas de red |
| **Desarrollador principal** | Integrante 2 | Diseñar estructura de código ESP32, definir estructura de topics |
| **Responsable de pruebas** | Integrante 3 | Implementar scripts de monitoreo, realizar mediciones de latencia |
| **Documentador** | Integrante 4 | Capturar evidencias, documentar resultados, elaborar diagramas |
| **Coordinador de análisis** | Integrante 5 | Analizar datos, responder preguntas de reflexión, coordinar experimentos |

**Importante:** Todos los integrantes deben programar su propio ESP32 y participar en los experimentos.

---

## PARTE 1: CONFIGURACIÓN DEL BROKER MQTT

### 1.1 Instalación de Mosquitto (Integrante 1 - Líder de infraestructura)

**Paso 1:** Acceder al laboratorio virtual mediante SSH:
```bash
ssh -p 2200 usuario@devlabs.eium.com.mx
# Ingresar contraseña cuando se solicite
```

**Paso 2:** Actualizar el sistema e instalar Mosquitto:
```bash
sudo apt update
sudo apt install mosquitto mosquitto-clients -y
```

**Paso 3:** Verificar versión instalada:
```bash
mosquitto -h
```

**Salida esperada:** Información sobre Mosquitto (versión 2.x)

### 1.2 Configuración del broker

**Paso 1:** Crear archivo de configuración personalizado:
```bash
sudo nano /etc/mosquitto/conf.d/custom.conf
```

**Paso 2:** Agregar la siguiente configuración:
```conf
# Puerto de escucha (puerto expuesto del lab)
listener 3000

# Permitir conexiones anónimas (solo para laboratorio)
allow_anonymous true

# Máximo de conexiones simultáneas
max_connections 50

# Persistencia de mensajes
persistence true
persistence_location /var/lib/mosquitto/

# Log detallado para debugging
log_dest file /var/log/mosquitto/mosquitto.log
log_type all

# Configuración de QoS
max_queued_messages 1000
```

**Nota de seguridad:** En producción NUNCA usar `allow_anonymous true`. Siempre configurar autenticación mediante usuarios/contraseñas o certificados.

**Paso 3:** Guardar archivo (Ctrl+O, Enter, Ctrl+X)

**Paso 4:** Reiniciar servicio Mosquitto:
```bash
sudo systemctl restart mosquitto
sudo systemctl enable mosquitto  # Habilitar inicio automático
```

**Paso 5:** Verificar estado del servicio:
```bash
sudo systemctl status mosquitto
```

**Salida esperada:**
```
● mosquitto.service - Mosquitto MQTT Broker
   Loaded: loaded
   Active: active (running) since...
```

**Paso 6:** Verificar que Mosquitto escucha en el puerto correcto:
```bash
sudo netstat -tulpn | grep 3000
```

**Salida esperada:**
```
tcp        0      0 0.0.0.0:3000            0.0.0.0:*               LISTEN      1234/mosquitto
```

### 1.3 Pruebas básicas del broker (Todo el equipo)

**Actividad colaborativa:** Abrir dos terminales SSH al laboratorio virtual.

**Terminal 1 - Suscriptor (Integrante 3):**
```bash
mosquitto_sub -h localhost -p 3000 -t "test/conexion" -v
```

**Terminal 2 - Publicador (Integrante 2):**
```bash
mosquitto_pub -h localhost -p 3000 -t "test/conexion" -m "Hola desde el equipo!"
```

**Resultado esperado:** El mensaje "Hola desde el equipo!" debe aparecer inmediatamente en Terminal 1.

**Prueba adicional - Wildcards:**
```bash
# Terminal 1 - Suscribirse a todos los subtopics
mosquitto_sub -h localhost -p 3000 -t "test/#" -v

# Terminal 2 - Publicar en diferentes topics
mosquitto_pub -h localhost -p 3000 -t "test/nivel1" -m "Mensaje 1"
mosquitto_pub -h localhost -p 3000 -t "test/nivel1/nivel2" -m "Mensaje 2"
mosquitto_pub -h localhost -p 3000 -t "test/otro" -m "Mensaje 3"
```

Todos los mensajes deben aparecer en Terminal 1.

---

## PARTE 2: DISEÑO DE LA ESTRUCTURA DE TOPICS

### 2.1 Definición de jerarquía de topics (Integrante 2 - Desarrollador principal)

Para organizar eficientemente los datos de 5 ESP32, definiremos la siguiente estructura:

```
equipo/[nombre_equipo]/
    ├── dispositivos/
    │   ├── esp32_1/
    │   │   ├── datos/temperatura
    │   │   ├── datos/humedad
    │   │   ├── datos/contador
    │   │   └── estado/conexion
    │   ├── esp32_2/
    │   │   └── ...
    │   └── ...
    │
    ├── comandos/
    │   ├── individual/esp32_1
    │   ├── individual/esp32_2
    │   ├── ...
    │   └── broadcast
    │
    └── sistema/
        ├── estadisticas
        └── alertas
```

**Ejemplo de topics concretos:**
```
equipo/alpha/dispositivos/esp32_1/datos/temperatura
equipo/alpha/dispositivos/esp32_1/estado/conexion
equipo/alpha/comandos/individual/esp32_1
equipo/alpha/comandos/broadcast
equipo/alpha/sistema/estadisticas
```

### 2.2 Estrategia de subscripción

**Para el monitor del sistema:**
```
equipo/alpha/#  → Suscribirse a TODOS los mensajes del equipo
```

**Para cada ESP32:**
```
equipo/alpha/comandos/individual/esp32_X  → Comandos específicos
equipo/alpha/comandos/broadcast           → Comandos para todos
```

---

## PARTE 3: IMPLEMENTACIÓN EN ESP32

### 3.1 Instalación de bibliotecas (Todos los integrantes)

**Paso 1:** Abrir Arduino IDE

**Paso 2:** Instalar biblioteca PubSubClient:
- Ir a: Herramientas → Administrar bibliotecas
- Buscar: "PubSubClient"
- Instalar: PubSubClient by Nick O'Leary

**Paso 3:** Instalar biblioteca ArduinoJson:
- En el mismo administrador, buscar: "ArduinoJson"
- Instalar: ArduinoJson by Benoit Blanchon (versión 6.x)

### 3.2 Código base del ESP32 (Todos los integrantes)

**IMPORTANTE:** Cada integrante debe modificar el `DEVICE_ID` para que sea único (esp32_1, esp32_2, etc.)

```cpp
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ==================== CONFIGURACIÓN WiFi ====================
const char* WIFI_SSID = "NOMBRE_RED_WIFI";        // Cambiar
const char* WIFI_PASSWORD = "PASSWORD_WIFI";       // Cambiar

// ==================== CONFIGURACIÓN MQTT ====================
const char* MQTT_SERVER = "devlabs.eium.com.mx";   // No cambiar
const int MQTT_PORT = 3000;                        // No cambiar
const char* DEVICE_ID = "esp32_1";                 // CAMBIAR: esp32_1, esp32_2, ..., esp32_5

// ==================== ESTRUCTURA DE TOPICS ====================
String BASE_TOPIC = "equipo/alpha";
String topicPublicacionTemp;
String topicPublicacionEstado;
String topicSuscripcionComandosIndividual;
String topicSuscripcionComandosBroadcast;

// ==================== OBJETOS GLOBALES ====================
WiFiClient espClient;
PubSubClient mqttClient(espClient);

// ==================== VARIABLES GLOBALES ====================
unsigned long lastPublishTime = 0;
const unsigned long PUBLISH_INTERVAL = 3000;  // Publicar cada 3 segundos
int messageCounter = 0;
float temperatureOffset = 0;  // Offset único por dispositivo para simular diferencias

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
    Serial.println("\n[WiFi] ✓ Conectado exitosamente");
    Serial.print("[WiFi] IP local: ");
    Serial.println(WiFi.localIP());
    Serial.print("[WiFi] RSSI: ");
    Serial.println(WiFi.RSSI());
  } else {
    Serial.println("\n[WiFi] ✗ Error: No se pudo conectar");
    Serial.println("[WiFi] Reiniciando en 5 segundos...");
    delay(5000);
    ESP.restart();
  }
}

// ==================== FUNCIÓN: Callback MQTT ====================
void callbackMQTT(char* topic, byte* payload, unsigned int length) {
  // Convertir payload a String
  String mensaje = "";
  for (unsigned int i = 0; i < length; i++) {
    mensaje += (char)payload[i];
  }
  
  Serial.println("\n[MQTT] ← Mensaje recibido");
  Serial.println("  Topic: " + String(topic));
  Serial.println("  Payload: " + mensaje);
  
  // Procesar comandos
  if (mensaje == "LED_ON") {
    Serial.println("  Acción: Encender LED");
    // digitalWrite(LED_PIN, HIGH);  // Descomentar si tienen LED conectado
  } 
  else if (mensaje == "LED_OFF") {
    Serial.println("  Acción: Apagar LED");
    // digitalWrite(LED_PIN, LOW);
  }
  else if (mensaje == "RESET_COUNTER") {
    Serial.println("  Acción: Resetear contador");
    messageCounter = 0;
  }
  else if (mensaje == "STATUS") {
    Serial.println("  Acción: Publicar estado inmediato");
    publicarEstado();
  }
  else {
    Serial.println("  Comando no reconocido: " + mensaje);
  }
}

// ==================== FUNCIÓN: Conectar MQTT ====================
void conectarMQTT() {
  while (!mqttClient.connected()) {
    Serial.println("\n[MQTT] Conectando al broker...");
    Serial.println("  Servidor: " + String(MQTT_SERVER));
    Serial.println("  Puerto: " + String(MQTT_PORT));
    Serial.println("  Client ID: " + String(DEVICE_ID));
    
    // Intentar conexión con Last Will Testament
    String willTopic = BASE_TOPIC + "/dispositivos/" + DEVICE_ID + "/estado/conexion";
    
    if (mqttClient.connect(DEVICE_ID, willTopic.c_str(), 1, true, "offline")) {
      Serial.println("[MQTT] ✓ Conectado al broker");
      
      // Publicar estado online
      mqttClient.publish(willTopic.c_str(), "online", true);
      
      // Suscribirse a topics de comandos
      mqttClient.subscribe(topicSuscripcionComandosIndividual.c_str());
      mqttClient.subscribe(topicSuscripcionComandosBroadcast.c_str());
      
      Serial.println("[MQTT] ✓ Suscrito a:");
      Serial.println("  - " + topicSuscripcionComandosIndividual);
      Serial.println("  - " + topicSuscripcionComandosBroadcast);
      
    } else {
      Serial.print("[MQTT] ✗ Error de conexión. Estado: ");
      Serial.println(mqttClient.state());
      Serial.println("[MQTT] Reintentando en 5 segundos...");
      delay(5000);
    }
  }
}

// ==================== FUNCIÓN: Publicar Temperatura ====================
void publicarTemperatura() {
  // Simular temperatura: base 20°C + offset único + variación aleatoria
  float temperatura = 20.0 + temperatureOffset + random(-20, 30) / 10.0;
  
  // Crear JSON
  StaticJsonDocument<256> doc;
  doc["device_id"] = DEVICE_ID;
  doc["temperatura"] = round(temperatura * 100) / 100.0;  // 2 decimales
  doc["timestamp"] = millis() / 1000;
  doc["seq"] = messageCounter;
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  // Publicar
  bool exito = mqttClient.publish(topicPublicacionTemp.c_str(), jsonString.c_str(), false);
  
  if (exito) {
    Serial.println("\n[MQTT] → Datos publicados");
    Serial.println("  Topic: " + topicPublicacionTemp);
    Serial.println("  Payload: " + jsonString);
    messageCounter++;
  } else {
    Serial.println("\n[MQTT] ✗ Error al publicar datos");
  }
}

// ==================== FUNCIÓN: Publicar Estado ====================
void publicarEstado() {
  StaticJsonDocument<256> doc;
  doc["device_id"] = DEVICE_ID;
  doc["estado"] = "online";
  doc["uptime"] = millis() / 1000;
  doc["rssi"] = WiFi.RSSI();
  doc["ip"] = WiFi.localIP().toString();
  doc["mensajes_enviados"] = messageCounter;
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  mqttClient.publish(topicPublicacionEstado.c_str(), jsonString.c_str(), false);
  Serial.println("\n[MQTT] → Estado publicado: " + jsonString);
}

// ==================== SETUP ====================
void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\n");
  Serial.println("========================================");
  Serial.println("  ESP32 - Cliente MQTT");
  Serial.println("  Device ID: " + String(DEVICE_ID));
  Serial.println("========================================");
  
  // Configurar offset único por dispositivo (puedes ajustar)
  if (String(DEVICE_ID) == "esp32_1") temperatureOffset = 0.0;
  else if (String(DEVICE_ID) == "esp32_2") temperatureOffset = 1.5;
  else if (String(DEVICE_ID) == "esp32_3") temperatureOffset = 3.0;
  else if (String(DEVICE_ID) == "esp32_4") temperatureOffset = 4.5;
  else if (String(DEVICE_ID) == "esp32_5") temperatureOffset = 6.0;
  
  // Construir topics dinámicamente
  topicPublicacionTemp = BASE_TOPIC + "/dispositivos/" + DEVICE_ID + "/datos/temperatura";
  topicPublicacionEstado = BASE_TOPIC + "/dispositivos/" + DEVICE_ID + "/estado/status";
  topicSuscripcionComandosIndividual = BASE_TOPIC + "/comandos/individual/" + DEVICE_ID;
  topicSuscripcionComandosBroadcast = BASE_TOPIC + "/comandos/broadcast";
  
  // Conectar WiFi
  conectarWiFi();
  
  // Configurar MQTT
  mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
  mqttClient.setCallback(callbackMQTT);
  mqttClient.setBufferSize(512);  // Aumentar buffer si es necesario
  
  // Conectar al broker MQTT
  conectarMQTT();
  
  // Publicar estado inicial
  publicarEstado();
  
  Serial.println("\n[Sistema] Listo. Iniciando bucle principal...\n");
}

// ==================== LOOP ====================
void loop() {
  // Verificar conexión WiFi
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[WiFi] ✗ Desconectado. Reconectando...");
    conectarWiFi();
  }
  
  // Verificar conexión MQTT
  if (!mqttClient.connected()) {
    conectarMQTT();
  }
  
  // Mantener conexión MQTT (procesar mensajes entrantes)
  mqttClient.loop();
  
  // Publicar datos periódicamente
  unsigned long currentTime = millis();
  if (currentTime - lastPublishTime >= PUBLISH_INTERVAL) {
    publicarTemperatura();
    lastPublishTime = currentTime;
  }
  
  // Pequeño delay para evitar saturar el procesador
  delay(10);
}
```

### 3.3 Compilación y carga del código (Todos los integrantes)

**Paso 1:** Modificar las siguientes líneas en el código:
```cpp
const char* WIFI_SSID = "TU_RED_WIFI";            // Red del laboratorio
const char* WIFI_PASSWORD = "PASSWORD";            // Password de la red
const char* DEVICE_ID = "esp32_X";                // X = 1, 2, 3, 4, o 5 (ÚNICO por integrante)
```

**Paso 2:** Seleccionar placa y puerto:
- Herramientas → Placa → ESP32 Dev Module (o Node32s)
- Herramientas → Puerto → Seleccionar puerto COM correcto

**Paso 3:** Compilar (Verificar) el código

**Paso 4:** Si compila sin errores, cargar al ESP32 (Upload)

**Paso 5:** Abrir Monitor Serial (115200 baudios)

**Salida esperada en Monitor Serial:**
```
========================================
  ESP32 - Cliente MQTT
  Device ID: esp32_1
========================================

[WiFi] Conectando a: LAB_WIFI
...........
[WiFi] ✓ Conectado exitosamente
[WiFi] IP local: 192.168.1.105
[WiFi] RSSI: -45

[MQTT] Conectando al broker...
  Servidor: devlabs.eium.com.mx
  Puerto: 3000
  Client ID: esp32_1
[MQTT] ✓ Conectado al broker
[MQTT] ✓ Suscrito a:
  - equipo/alpha/comandos/individual/esp32_1
  - equipo/alpha/comandos/broadcast

[MQTT] → Estado publicado: {...}

[Sistema] Listo. Iniciando bucle principal...

[MQTT] → Datos publicados
  Topic: equipo/alpha/dispositivos/esp32_1/datos/temperatura
  Payload: {"device_id":"esp32_1","temperatura":21.3,"timestamp":15,"seq":0}
```

---

## PARTE 4: MONITOREO Y OBSERVACIÓN

### 4.1 Script de monitoreo Python (Integrante 3 - Responsable de pruebas)

Crear un script que se suscriba a todos los mensajes del equipo:

```bash
cd ~
nano mqtt_monitor.py
```

```python
#!/usr/bin/env python3
"""
Monitor MQTT para Práctica 5A
Escucha todos los mensajes del equipo y los muestra en consola
"""

import paho.mqtt.client as mqtt
import json
from datetime import datetime
import sys

# Configuración
BROKER = "localhost"
PORT = 3000
BASE_TOPIC = "equipo/alpha/#"

# Contadores
message_count = {}
total_messages = 0

def on_connect(client, userdata, flags, rc):
    """Callback cuando se conecta al broker"""
    if rc == 0:
        print("=" * 70)
        print("✓ CONECTADO AL BROKER MQTT")
        print("=" * 70)
        print(f"Broker: {BROKER}:{PORT}")
        print(f"Suscrito a: {BASE_TOPIC}")
        print("=" * 70)
        print()
        client.subscribe(BASE_TOPIC)
    else:
        print(f"✗ Error de conexión. Código: {rc}")
        sys.exit(1)

def on_message(client, userdata, msg):
    """Callback cuando se recibe un mensaje"""
    global message_count, total_messages
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    topic = msg.topic
    payload = msg.payload.decode('utf-8', errors='ignore')
    
    # Contar mensajes
    total_messages += 1
    if topic in message_count:
        message_count[topic] += 1
    else:
        message_count[topic] = 1
    
    # Formatear salida
    print(f"┌─ [{timestamp}] Mensaje #{total_messages}")
    print(f"│  Topic: {topic}")
    
    # Intentar parsear como JSON para mejor formato
    try:
        data = json.loads(payload)
        print(f"│  Payload:")
        for key, value in data.items():
            print(f"│    {key}: {value}")
    except:
        print(f"│  Payload: {payload}")
    
    print(f"└─ Total del topic: {message_count[topic]} mensajes")
    print()

def on_disconnect(client, userdata, rc):
    """Callback cuando se desconecta"""
    print("\n✗ Desconectado del broker")
    if rc != 0:
        print(f"Desconexión inesperada. Código: {rc}")

# Crear cliente MQTT
client = mqtt.Client(client_id="monitor_python")
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# Conectar al broker
try:
    print("Conectando al broker MQTT...")
    client.connect(BROKER, PORT, 60)
    
    # Iniciar loop (bloquea hasta Ctrl+C)
    print("Presiona Ctrl+C para detener el monitor\n")
    client.loop_forever()
    
except KeyboardInterrupt:
    print("\n\n" + "=" * 70)
    print("RESUMEN DE LA SESIÓN")
    print("=" * 70)
    print(f"Total de mensajes recibidos: {total_messages}")
    print(f"Topics únicos: {len(message_count)}")
    print("\nDistribución por topic:")
    for topic, count in sorted(message_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {count:4d}  {topic}")
    print("=" * 70)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    sys.exit(1)
finally:
    client.disconnect()
```

**Guardar y ejecutar:**
```bash
# Instalar dependencias
pip3 install paho-mqtt

# Dar permisos de ejecución
chmod +x mqtt_monitor.py

# Ejecutar
python3 mqtt_monitor.py
```

### 4.2 Monitoreo con mosquitto_sub (Alternativa simple)

Si no quieren usar Python, pueden usar directamente:

```bash
# Suscribirse a todos los mensajes con formato verbose
mosquitto_sub -h localhost -p 3000 -t "equipo/alpha/#" -v

# O solo a temperaturas
mosquitto_sub -h localhost -p 3000 -t "equipo/alpha/dispositivos/+/datos/temperatura" -v
```

---

## PARTE 5: EXPERIMENTOS Y MEDICIONES

### 5.1 Experimento 1: Escalabilidad (Todo el equipo)

**Objetivo:** Observar cómo el sistema maneja el incremento de dispositivos activos.

**Metodología:**

1. **Escenario A - 1 dispositivo:**
   - Solo ESP32_1 encendido y publicando
   - Monitor observando durante 2 minutos
   - Registrar: Frecuencia de mensajes, latencia percibida

2. **Escenario B - 3 dispositivos:**
   - ESP32_1, ESP32_2, ESP32_3 activos simultáneamente
   - Monitor observando durante 2 minutos
   - Registrar: Frecuencia total de mensajes, cualquier mensaje perdido

3. **Escenario C - 5 dispositivos:**
   - Todos los ESP32 activos simultáneamente
   - Monitor observando durante 2 minutos
   - Registrar: Rendimiento del broker (usar `htop` en el servidor)

**Tabla de resultados:**

| Escenario | Dispositivos activos | Mensajes/min totales | Latencia observada | Mensajes perdidos | CPU del broker (%) |
|-----------|---------------------|----------------------|-------------------|-------------------|-------------------|
| A | 1 | | | | |
| B | 3 | | | | |
| C | 5 | | | | |

### 5.2 Experimento 2: Comunicación bidireccional (Todo el equipo)

**Objetivo:** Verificar la capacidad de enviar comandos a dispositivos específicos.

**Procedimiento:**

1. Todos los ESP32 activos y monitoreando

2. Desde el laboratorio virtual, enviar comandos individuales:
```bash
# Comando a ESP32_1 específicamente
mosquitto_pub -h localhost -p 3000 -t "equipo/alpha/comandos/individual/esp32_1" -m "LED_ON"

# Comando a ESP32_3
mosquitto_pub -h localhost -p 3000 -t "equipo/alpha/comandos/individual/esp32_3" -m "STATUS"
```

3. Verificar en el Monitor Serial de cada ESP32 que SOLO el ESP32 destinatario procesa el comando

4. Enviar comando broadcast:
```bash
mosquitto_pub -h localhost -p 3000 -t "equipo/alpha/comandos/broadcast" -m "RESET_COUNTER"
```

5. Verificar que TODOS los ESP32 procesan el comando

**Registro de resultados:**
- ¿Todos los ESP32 recibieron el comando broadcast? SÍ / NO
- ¿Los comandos individuales llegaron solo al destinatario correcto? SÍ / NO
- Tiempo aproximado entre publicación y recepción: ____ ms

### 5.3 Experimento 3: Tolerancia a desconexiones (Todo el equipo)

**Objetivo:** Observar el comportamiento del sistema ante desconexiones temporales.

**Procedimiento:**

1. Los 5 ESP32 activos y publicando normalmente

2. **Integrante 2:** Desconectar físicamente su ESP32 (desenchufar USB)

3. Observar en el monitor:
   - ¿Aparece mensaje de "offline" del Last Will Testament?
   - ¿Los otros 4 ESP32 siguen funcionando sin interrupción?

4. **Integrante 2:** Reconectar su ESP32

5. Observar:
   - ¿Cuánto tiempo tarda en reconectar?
   - ¿Se recupera automáticamente?
   - ¿Aparece mensaje de "online"?

**Registro de resultados:**
- Tiempo de reconexión: ____ segundos
- ¿Recuperación automática? SÍ / NO
- ¿Se notificó la desconexión (Last Will)? SÍ / NO
- ¿Los demás dispositivos se afectaron? SÍ / NO

### 5.4 Experimento 4: Medición de latencia (Integrante 5 - Coordinador de análisis)

**Objetivo:** Cuantificar la latencia end-to-end del sistema MQTT.

**Metodología:**

1. Modificar temporalmente el código de UN ESP32 para incluir timestamp preciso

2. Publicar mensaje con timestamp del ESP32

3. En el laboratorio virtual, usar un script que registre tiempo de recepción

4. Calcular: Latencia = tiempo_recepción - timestamp_envío

**Script de medición (guardar como `medir_latencia.py`):**

```python
import paho.mqtt.client as mqtt
import json
import time

latencias = []

def on_message(client, userdata, msg):
    tiempo_recepcion = time.time()
    try:
        data = json.loads(msg.payload.decode())
        timestamp_envio = data.get('timestamp', 0)
        if timestamp_envio > 0:
            latencia_ms = (tiempo_recepcion - timestamp_envio) * 1000
            latencias.append(latencia_ms)
            print(f"Latencia: {latencia_ms:.2f} ms")
            
            if len(latencias) >= 20:
                print(f"\nPromedio: {sum(latencias)/len(latencias):.2f} ms")
                print(f"Mínima: {min(latencias):.2f} ms")
                print(f"Máxima: {max(latencias):.2f} ms")
                client.disconnect()
    except:
        pass

client = mqtt.Client()
client.on_message = on_message
client.connect("localhost", 3000, 60)
client.subscribe("equipo/alpha/dispositivos/esp32_1/datos/temperatura")
client.loop_forever()
```

**Nota:** Este script requiere que el ESP32 use `time()` Unix epoch en lugar de `millis()`.

**Registrar:**
- Latencia promedio: ____ ms
- Latencia mínima: ____ ms
- Latencia máxima: ____ ms

---

## 7. PREGUNTAS DE REFLEXIÓN

Responder de forma argumentada basándose en las observaciones experimentales:

### 7.1 Sobre el protocolo MQTT

1. **¿Qué sucede cuando se publica un mensaje y no hay suscriptores conectados?**
   - Describir el comportamiento observado
   - Explicar las implicaciones para diseño de sistemas IoT

2. **¿Cómo afecta la calidad de servicio (QoS) al comportamiento del sistema?**
   - Aunque no implementaron QoS 1 o 2, investigar y explicar diferencias
   - ¿En qué casos usarían QoS 0, 1 o 2?

3. **¿Cuál es el papel del broker en este modelo de comunicación?**
   - ¿Es el broker un punto único de fallo?
   - ¿Cómo se podría mitigar este riesgo?

### 7.2 Sobre escalabilidad

4. **¿Cómo escala el sistema al aumentar de 1 a 5 dispositivos?**
   - Usar datos del Experimento 1
   - ¿Observaron degradación del rendimiento?
   - ¿Cuál sería el límite teórico con este broker?

5. **¿Qué ventajas tiene la estructura jerárquica de topics?**
   - Comparar con tener un solo topic para todos los datos
   - Discutir organización y escalabilidad

### 7.3 Sobre comunicación bidireccional

6. **¿Qué ventajas tiene la comunicación asíncrona bidireccional de MQTT?**
   - Comparar con modelos donde solo el cliente puede iniciar comunicación
   - Dar ejemplos de casos de uso

7. **¿Cómo se implementaría un sistema de notificaciones críticas usando MQTT?**
   - Diseñar estructura de topics
   - Considerar QoS y Retained Messages

### 7.4 Sobre tolerancia a fallos

8. **¿Por qué es útil el mensaje de Last Will Testament?**
   - Explicar el mecanismo
   - Proponer casos de uso prácticos

9. **¿Cómo maneja MQTT las desconexiones temporales de red?**
   - Usar observaciones del Experimento 3
   - Investigar el parámetro "keep-alive"

### 7.5 Aplicaciones prácticas

10. **Diseñar un sistema IoT real usando MQTT:**
    - Escoger un caso de uso (ej: monitoreo de invernadero, sistema de alarma, etc.)
    - Definir arquitectura de topics
    - Especificar QoS para diferentes tipos de mensajes
    - Justificar decisiones

---

## 8. ENTREGABLES

El equipo debe entregar un **reporte técnico** en formato PDF que incluya:

### 8.1 Portada
- Título de la práctica
- Nombres completos y matrículas de todos los integrantes
- Roles asignados a cada integrante
- Fecha de realización
- Nombre del laboratorio virtual asignado (ej: lab-equipo1-1770154395140)

### 8.2 Marco teórico (1-2 páginas)
- Resumen del protocolo MQTT
- Explicación del modelo publish/subscribe
- Ventajas de MQTT para IoT

### 8.3 Desarrollo experimental

**Configuración del broker:**
- Captura de `systemctl status mosquitto` mostrando servicio activo
- Contenido del archivo de configuración `/etc/mosquitto/conf.d/custom.conf`
- Captura de prueba de conexión básica (mosquitto_pub/sub)

**Implementación en ESP32:**
- Código fuente completo de 1 ESP32 (puede ser cualquiera, todos son similares)
- Capturas del Monitor Serial de al menos 3 ESP32 diferentes mostrando:
  - Conexión exitosa al broker
  - Publicación de datos
  - Recepción de comandos

**Monitor del sistema:**
- Captura del script Python mostrando mensajes de los 5 dispositivos
- O capturas de mosquitto_sub mostrando los mensajes

### 8.4 Resultados de experimentos

**Experimento 1 - Escalabilidad:**
- Tabla de resultados completamente llena
- Gráfica de "Mensajes/minuto vs Número de dispositivos"
- Análisis de escalabilidad observada

**Experimento 2 - Comunicación bidireccional:**
- Capturas de comandos enviados y respuestas en ESP32
- Evidencia de comando broadcast llegando a todos los dispositivos

**Experimento 3 - Tolerancia a desconexiones:**
- Descripción detallada de lo observado
- Tiempos de reconexión medidos

**Experimento 4 - Latencia:**
- Tabla con al menos 20 mediciones
- Estadísticas: promedio, mínima, máxima, desviación estándar
- Gráfica de distribución de latencias (histograma o box plot)

### 8.5 Respuestas a preguntas de reflexión
- Las 10 preguntas respondidas de forma completa y argumentada
- Usar datos experimentales para respaldar respuestas
- Incluir diseño del sistema IoT (pregunta 10)

### 8.6 Diagrama de arquitectura
- Diagrama profesional mostrando:
  - Los 5 ESP32
  - Broker MQTT en devlabs
  - Estructura jerárquica de topics
  - Flujos de mensajes (publish/subscribe)
  - Anotaciones claras

### 8.7 División del trabajo
Tabla detallando:

| Integrante | Rol | Tareas realizadas | % Contribución |
|------------|-----|-------------------|----------------|
| Nombre 1 | Líder de infraestructura | Config broker, resolución de problemas | 20% |
| Nombre 2 | Desarrollador principal | Diseño de código, estructura topics | 20% |
| ... | ... | ... | ... |

### 8.8 Conclusiones

**Individuales (cada integrante - 1 párrafo c/u):**
- Principal aprendizaje adquirido
- Aspecto más desafiante de la práctica
- Aplicación práctica que propondría

**Grupal (2-3 párrafos):**
- Análisis de ventajas de MQTT para IoT
- Limitaciones observadas
- Recomendaciones para futuros equipos

### 8.9 Referencias
- Formato IEEE
- Incluir documentación oficial de Mosquitto y PubSubClient
- Tutoriales o recursos adicionales consultados

---

## 9. CRITERIOS DE EVALUACIÓN

**Total: 100 puntos**

| Criterio | Puntos | Descripción |
|----------|--------|-------------|
| **Implementación del broker** | 15 | Broker correctamente configurado, funcionando, evidencia completa |
| **Código ESP32** | 20 | Los 5 ESP32 funcionan, código bien estructurado, comentado |
| **Experimentos** | 25 | Los 4 experimentos realizados correctamente, datos reales |
| **Análisis y reflexión** | 20 | Respuestas completas, argumentadas, usan datos experimentales |
| **Diagrama** | 10 | Claro, correcto, profesional |
| **Trabajo en equipo** | 5 | Evidencia de colaboración, roles claros |
| **Formato y presentación** | 5 | Redacción clara, sin errores, formato profesional |

### Rúbrica detallada - Experimentos (25 puntos)

| Nivel | Puntos | Criterios |
|-------|--------|-----------|
| Excelente | 23-25 | Los 4 experimentos completos, datos reales y consistentes, análisis profundo, gráficas profesionales |
| Satisfactorio | 18-22 | 3-4 experimentos completos, datos reales, análisis adecuado |
| Suficiente | 13-17 | 2-3 experimentos, datos básicos, análisis superficial |
| Insuficiente | 0-12 | Menos de 2 experimentos, datos inventados o inconsistentes |

---

## 10. CONSIDERACIONES FINALES

### 10.1 Tiempo estimado
- Configuración del broker: 1 hora
- Programación de ESP32: 2 horas
- Pruebas y debugging: 1 hora
- Experimentos: 2 horas
- Análisis y reporte: 2 horas
- **Total: 8 horas**

### 10.2 Tips importantes

✅ **DO:**
- Documentar TODO durante el proceso (capturas, notas)
- Probar la conexión del broker ANTES de programar los ESP32
- Usar nombres únicos de DEVICE_ID
- Respaldar código frecuentemente
- Trabajar colaborativamente en los experimentos

❌ **DON'T:**
- NO esperar al último momento para hacer capturas
- NO inventar datos de mediciones
- NO usar el mismo DEVICE_ID en múltiples ESP32
- NO olvidar respaldar antes de que expire el laboratorio (24h)

### 10.3 Comandos útiles de respaldo

```bash
# Respaldar configuración de Mosquitto
sudo cp /etc/mosquitto/conf.d/custom.conf ~/backup_mosquitto.conf

# Ver logs del broker
sudo tail -f /var/log/mosquitto/mosquitto.log

# Verificar mensajes en broker
mosquitto_sub -h localhost -p 3000 -t "#" -v > ~/all_messages.log &

# Monitorear rendimiento del broker
htop  # Buscar proceso 'mosquitto'
```

### 10.4 Solución de problemas comunes

**Problema:** ESP32 no se conecta al broker
- Verificar que el broker esté corriendo: `sudo systemctl status mosquitto`
- Verificar puerto correcto: 3000
- Verificar WiFi del ESP32: imprimir IP local
- Verificar firewall: el puerto debe estar expuesto en devlabs

**Problema:** No aparecen mensajes en el monitor
- Verificar que el topic de suscripción sea correcto
- Usar wildcard `#` para suscribirse a todo: `equipo/alpha/#`
- Verificar que el ESP32 esté publicando (ver Monitor Serial)

**Problema:** ESP32 se desconecta constantemente
- Verificar calidad de señal WiFi (RSSI)
- Aumentar parámetro keep-alive en código
- Verificar que no haya demasiados dispositivos en la red

---

## ANEXO A: Estructura completa de topics

```
equipo/alpha/
│
├── dispositivos/
│   ├── esp32_1/
│   │   ├── datos/
│   │   │   ├── temperatura
│   │   │   ├── humedad (opcional)
│   │   │   └── contador (opcional)
│   │   └── estado/
│   │       ├── conexion (Last Will)
│   │       └── status
│   │
│   ├── esp32_2/
│   │   └── [misma estructura]
│   ├── esp32_3/
│   │   └── [misma estructura]
│   ├── esp32_4/
│   │   └── [misma estructura]
│   └── esp32_5/
│       └── [misma estructura]
│
├── comandos/
│   ├── individual/
│   │   ├── esp32_1
│   │   ├── esp32_2
│   │   ├── esp32_3
│   │   ├── esp32_4
│   │   └── esp32_5
│   └── broadcast
│
└── sistema/
    ├── estadisticas
    └── alertas
```

---

**Fecha de entrega:** [A definir por el profesor]

**Formato de entrega:**
- Archivo: `Practica05A_MQTT_EquipoX.pdf`
- Código: `Practica05A_Codigo_EquipoX.zip`

---

*Universidad Modelo EIUM - Ingeniería en Software / IoT*  
*Práctica 5A: Comunicación IoT con MQTT*  
*Versión 1.0 - Febrero 2026*
