/*
 * ESP32 HTTP Client - Práctica 5B
 * Universidad Modelo EIUM
 * 
 * Cliente HTTP que envía datos a una API REST
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// CONFIGURACIÓN
const char* WIFI_SSID = "NOMBRE_RED";
const char* WIFI_PASSWORD = "PASSWORD";
const char* API_URL = "http://devlabs.eium.com.mx:3001";
const char* DEVICE_ID = "esp32_1";  // CAMBIAR: esp32_1, esp32_2, ..., esp32_5

// VARIABLES
unsigned long lastPostTime = 0;
const unsigned long POST_INTERVAL = 3000;
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

void postDatos() {
  if (WiFi.status() != WL_CONNECTED) return;
  
  HTTPClient http;
  String url = String(API_URL) + "/devices/" + String(DEVICE_ID) + "/data";
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(5000);
  
  float temperatura = 20.0 + temperatureOffset + random(-20, 30) / 10.0;
  
  StaticJsonDocument<256> doc;
  doc["temperatura"] = round(temperatura * 100) / 100.0;
  doc["timestamp"] = millis() / 1000;
  doc["seq"] = messageCounter;
  
  String jsonPayload;
  serializeJson(doc, jsonPayload);
  
  Serial.println("\n[HTTP] → POST Request");
  Serial.println("  URL: " + url);
  Serial.println("  Payload: " + jsonPayload);
  
  unsigned long startTime = millis();
  int httpCode = http.POST(jsonPayload);
  unsigned long responseTime = millis() - startTime;
  
  if (httpCode > 0) {
    Serial.printf("  Código HTTP: %d\n", httpCode);
    Serial.printf("  Tiempo de respuesta: %lu ms\n", responseTime);
    
    if (httpCode == 201 || httpCode == 200) {
      String response = http.getString();
      Serial.println("  ✓ Datos enviados exitosamente");
      messageCounter++;
    }
  } else {
    Serial.printf("  ✗ Error: %s\n", http.errorToString(httpCode).c_str());
  }
  
  http.end();
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n========================================");
  Serial.println("  ESP32 - Cliente HTTP REST");
  Serial.println("  Device: " + String(DEVICE_ID));
  Serial.println("========================================");
  
  if (String(DEVICE_ID) == "esp32_1") temperatureOffset = 0.0;
  else if (String(DEVICE_ID) == "esp32_2") temperatureOffset = 1.5;
  else if (String(DEVICE_ID) == "esp32_3") temperatureOffset = 3.0;
  else if (String(DEVICE_ID) == "esp32_4") temperatureOffset = 4.5;
  else if (String(DEVICE_ID) == "esp32_5") temperatureOffset = 6.0;
  
  conectarWiFi();
  delay(2000);
  postDatos();
  
  Serial.println("\n[Sistema] Listo\n");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    conectarWiFi();
  }
  
  unsigned long currentTime = millis();
  if (currentTime - lastPostTime >= POST_INTERVAL) {
    postDatos();
    lastPostTime = currentTime;
  }
  
  delay(10);
}
