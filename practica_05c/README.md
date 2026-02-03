# Práctica 5C: Arquitectura IoT con Gateway

Gateway IoT usando Raspberry Pi Zero W.

## Archivos

- `docs/PRACTICA_05C.md` - Documento completo
- `codigo/esp32_gateway_client/esp32_gateway_client.ino` - Cliente para gateway
- `codigo/gateway/gateway.py` - Gateway en Raspberry Pi

## Inicio Rápido

### Gateway (Raspberry Pi)
```bash
cd codigo/gateway
pip3 install flask paho-mqtt
python3 gateway.py
```

### ESP32
1. Cambiar IP del gateway en el código
2. Compilar y cargar
