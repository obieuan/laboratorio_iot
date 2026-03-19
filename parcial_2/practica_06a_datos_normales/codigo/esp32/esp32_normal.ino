/*
  =============================================================
  Práctica 6A — Recolección de datos normales
  EIUM — Universidad Modelo

  Simula un servidor funcionando en condiciones normales.
  Publica por MQTT cada 500ms.

  IMPORTANTE: Cambia DEVICE_ID según tu equipo:
    Equipo 1 → "ESP32-A"
    Equipo 2 → "ESP32-B"
    Equipo 3 → "ESP32-C"
  =============================================================
*/

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <math.h>

// ---- CONFIGURACIÓN — editar antes de compilar ----
const char* DEVICE_ID   = "ESP32-A";       // <-- cambiar por equipo
const char* WIFI_SSID   = "TU_RED_WIFI";
const char* WIFI_PASS   = "TU_PASSWORD";
const char* MQTT_BROKER = "192.168.X.X";   // IP de la laptop con el broker
const int   MQTT_PORT   = 1883;
const char* TOPIC       = "iot/lab/sensores";
// --------------------------------------------------

WiFiClient   espClient;
PubSubClient mqtt(espClient);

int  t       = 0;   // contador de tiempo (ticks)
long ultimo  = 0;

// ---- Funciones de simulación ----

float simular_temperatura(int tick) {
  // Patrón sinusoidal suave: entre 20°C y 26°C
  float base  = 23.0 + sin(tick * 0.03) * 3.0;
  float ruido = (random(-10, 10)) * 0.08;
  return base + ruido;
}

int simular_cpu(int tick) {
  // Carga aleatoria con ráfagas cortas ocasionales
  int base = random(15, 60);
  if (tick % 25 == 0) base = random(60, 75);  // ráfaga breve
  return base;
}

float simular_power(int cpu) {
  // Correlacionado con CPU: más carga → más consumo
  return 150.0 + cpu * 2.2 + random(-15, 15);
}

int simular_fan(float temp) {
  // Fan sube cuando la temperatura sube
  return (int)(900 + (temp - 20.0) * 90 + random(-50, 50));
}

// ---- Setup ----

void conectar_wifi() {
  Serial.print("Conectando WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" OK — IP: " + WiFi.localIP().toString());
}

void conectar_mqtt() {
  while (!mqtt.connected()) {
    Serial.print("Conectando MQTT...");
    if (mqtt.connect(DEVICE_ID)) {
      Serial.println(" OK");
    } else {
      Serial.println(" fallo, reintentando en 3s");
      delay(3000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  randomSeed(analogRead(0));
  conectar_wifi();
  mqtt.setServer(MQTT_BROKER, MQTT_PORT);
}

// ---- Loop ----

void loop() {
  if (!mqtt.connected()) conectar_mqtt();
  mqtt.loop();

  if (millis() - ultimo < 500) return;
  ultimo = millis();

  float temp  = simular_temperatura(t);
  int   cpu   = simular_cpu(t);
  float power = simular_power(cpu);
  int   fan   = simular_fan(temp);

  // Armar JSON
  StaticJsonDocument<200> doc;
  doc["device_id"]     = DEVICE_ID;
  doc["temperature_c"] = serialized(String(temp, 1));
  doc["cpu_percent"]   = cpu;
  doc["power_w"]       = serialized(String(power, 0));
  doc["fan_rpm"]       = fan;
  doc["tick"]          = t;

  char buffer[256];
  serializeJson(doc, buffer);
  mqtt.publish(TOPIC, buffer);

  Serial.printf("[%s | t=%d] temp=%.1f cpu=%d%% power=%.0fW fan=%drpm\n",
                DEVICE_ID, t, temp, cpu, power, fan);
  t++;
}
