# Práctica 5A: Comunicación IoT con MQTT

Implementación de comunicación en tiempo real usando el protocolo MQTT.

## Archivos

- `docs/PRACTICA_05A.md` - Documento completo de la práctica
- `codigo/esp32_mqtt_client/esp32_mqtt_client.ino` - Código para ESP32
- `codigo/python/mqtt_monitor.py` - Monitor MQTT en Python

## Inicio Rápido

### ESP32
1. Abrir `esp32_mqtt_client.ino` en Arduino IDE
2. Cambiar `WIFI_SSID`, `WIFI_PASSWORD` y `DEVICE_ID`
3. Compilar y cargar

### Monitor Python
```bash
cd codigo/python
pip3 install paho-mqtt
python3 mqtt_monitor.py
```
