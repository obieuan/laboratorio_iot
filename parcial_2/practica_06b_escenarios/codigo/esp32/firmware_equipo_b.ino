/*
  =============================================================
  Práctica 6B — Escenario B
  [ARCHIVO PARA EL PROFESOR — no distribuir a los alumnos]
  =============================================================
  Comportamiento: falla progresiva del sistema de enfriamiento.

  Lo que ocurre:
    - El fan pierde velocidad gradualmente (se está muriendo)
    - Sin enfriamiento, la temperatura sube lentamente
    - CPU y consumo eléctrico son NORMALES — no es sobrecarga
    - La anomalía NO es un spike, es una tendencia sostenida

  Pista para el alumno (si la necesita): "algo cambia con el tiempo"
*/

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <math.h>

const char* DEVICE_ID   = "ESP32-B";
const char* WIFI_SSID   = "TU_RED_WIFI";
const char* WIFI_PASS   = "TU_PASSWORD";
const char* MQTT_BROKER = "192.168.X.X";
const int   MQTT_PORT   = 1883;
const char* TOPIC       = "iot/lab/sensores";

WiFiClient   espClient;
PubSubClient mqtt(espClient);
int  t      = 0;
long ultimo = 0;

// Degradación: el fan pierde ~0.3% de capacidad por tick
// A los 200 ticks (100s) ya funciona al 40% → temperatura crítica
float degradacion_fan(int tick) {
  float factor = max(0.15f, 1.0f - tick * 0.003f);  // mínimo 15%
  return factor;
}

float simular_temperatura(int tick) {
  // Sin enfriamiento la temperatura sube. La relación con el fan se rompe.
  float temp_base = 22.0 + tick * 0.06;  // sube ~0.06°C por tick
  temp_base = min(temp_base, 45.0f);     // techo físico
  float ruido = (random(-8, 8)) * 0.1;
  return temp_base + ruido;
}

int simular_cpu(int tick) {
  // CPU completamente normal — eso es lo engañoso del escenario
  return random(15, 60);
}

float simular_power(int cpu) {
  return 150.0 + cpu * 2.2 + random(-15, 15);  // normal, correlacionado con CPU
}

int simular_fan(int tick) {
  // Fan pierde RPM progresivamente
  float factor  = degradacion_fan(tick);
  int   rpm_max = 1800;
  return (int)(rpm_max * factor + random(-30, 30));
}

void conectar_wifi() {
  Serial.print("Conectando WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println(" OK");
}
void conectar_mqtt() {
  while (!mqtt.connected()) {
    if (mqtt.connect(DEVICE_ID)) Serial.println("MQTT OK");
    else delay(3000);
  }
}
void setup() {
  Serial.begin(115200);
  randomSeed(analogRead(0));
  conectar_wifi();
  mqtt.setServer(MQTT_BROKER, MQTT_PORT);
}
void loop() {
  if (!mqtt.connected()) conectar_mqtt();
  mqtt.loop();
  if (millis() - ultimo < 500) return;
  ultimo = millis();

  float temp  = simular_temperatura(t);
  int   cpu   = simular_cpu(t);
  float power = simular_power(cpu);
  int   fan   = simular_fan(t);

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
  Serial.printf("[%s | t=%d] temp=%.1f cpu=%d power=%.0f fan=%d (degradacion=%.0f%%)\n",
                DEVICE_ID, t, temp, cpu, power, fan, degradacion_fan(t) * 100);
  t++;
}
