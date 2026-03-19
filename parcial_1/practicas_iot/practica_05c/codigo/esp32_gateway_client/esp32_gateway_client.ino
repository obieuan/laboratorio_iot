/*
 * ESP32 Gateway Client - Práctica 5C
 * Envía datos a Raspberry Pi Gateway
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* WIFI_SSID = "RED_LAB";
const char* WIFI_PASSWORD = "PASSWORD";
const char* GATEWAY_IP = "192.168.X.X";  // ¡CAMBIAR!
const int GATEWAY_PORT = 5000;
const char* DEVICE_ID = "esp32_1";  // CAMBIAR

unsigned long lastPostTime = 0;
const unsigned long POST_INTERVAL = 5000;
int messageCounter = 0;
float temperatureOffset = 0;

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
  } else {
    Serial.println("\n[WiFi] ✗ Error");
    ESP.restart();
  }
}

void postToGateway() {
  if (WiFi.status() != WL_CONNECTED) return;
  
  HTTPClient http;
  String url = "http://" + String(GATEWAY_IP) + ":" + String(GATEWAY_PORT) + "/gateway/data";
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(5000);
  
  float temp = 20.0 + temperatureOffset + random(-20, 30) / 10.0;
  
  StaticJsonDocument<256> doc;
  doc["device_id"] = DEVICE_ID;
  doc["temperatura"] = round(temp * 100) / 100.0;
  doc["timestamp"] = millis() / 1000;
  doc["seq"] = messageCounter;
  
  String payload;
  serializeJson(doc, payload);
  
  unsigned long start = millis();
  int httpCode = http.POST(payload);
  unsigned long latency = millis() - start;
  
  Serial.println("\n[HTTP] → POST al Gateway");
  Serial.printf("  URL: %s\n", url.c_str());
  Serial.printf("  Código: %d | Latencia: %lu ms\n", httpCode, latency);
  
  if (httpCode == 200) {
    String response = http.getString();
    StaticJsonDocument<256> respDoc;
    deserializeJson(respDoc, response);
    bool mqttConnected = respDoc["mqtt_connected"];
    Serial.printf("  ✓ Enviado | MQTT central: %s\n", mqttConnected ? "✓" : "✗");
    messageCounter++;
  } else if (httpCode == 202) {
    Serial.println("  ⊙ En buffer (MQTT offline)");
    messageCounter++;
  }
  
  http.end();
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n========================================");
  Serial.println("  ESP32 - Gateway Mode");
  Serial.println("  Device: " + String(DEVICE_ID));
  Serial.println("  Gateway: " + String(GATEWAY_IP));
  Serial.println("========================================");
  
  if (String(DEVICE_ID) == "esp32_1") temperatureOffset = 0.0;
  else if (String(DEVICE_ID) == "esp32_2") temperatureOffset = 1.5;
  else if (String(DEVICE_ID) == "esp32_3") temperatureOffset = 3.0;
  else if (String(DEVICE_ID) == "esp32_4") temperatureOffset = 4.5;
  else if (String(DEVICE_ID) == "esp32_5") temperatureOffset = 6.0;
  
  conectarWiFi();
  Serial.println("\n[Sistema] Listo\n");
}

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
