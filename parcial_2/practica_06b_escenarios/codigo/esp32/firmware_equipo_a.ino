/*
  =============================================================
  Práctica 6B — Escenario A
  [ARCHIVO PARA EL PROFESOR — no distribuir a los alumnos]
  =============================================================
  Comportamiento: servidor en operación completamente normal.
  Sirve como control: el modelo debería ver muy pocas anomalías.
*/

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <math.h>

const char* DEVICE_ID   = "ESP32-A";
const char* WIFI_SSID   = "TU_RED_WIFI";
const char* WIFI_PASS   = "TU_PASSWORD";
const char* MQTT_BROKER = "192.168.X.X";
const int   MQTT_PORT   = 1883;
const char* TOPIC       = "iot/lab/sensores";

WiFiClient   espClient;
PubSubClient mqtt(espClient);
int  t      = 0;
long ultimo = 0;

float simular_temperatura(int tick) {
  return 23.0 + sin(tick * 0.03) * 3.0 + (random(-10, 10)) * 0.08;
}
int simular_cpu(int tick) {
  int base = random(15, 60);
  if (tick % 25 == 0) base = random(60, 75);
  return base;
}
float simular_power(int cpu) { return 150.0 + cpu * 2.2 + random(-15, 15); }
int   simular_fan(float temp) { return (int)(900 + (temp - 20.0) * 90 + random(-50, 50)); }

void conectar_wifi() {
  Serial.print("Conectando WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println(" OK");
}
void conectar_mqtt() {
  while (!mqtt.connected()) {
    if (mqtt.connect(DEVICE_ID)) Serial.println("MQTT OK");
    else { delay(3000); }
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
  int   fan   = simular_fan(temp);

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
  Serial.printf("[%s | t=%d] temp=%.1f cpu=%d power=%.0f fan=%d\n",
                DEVICE_ID, t, temp, cpu, power, fan);
  t++;
}
