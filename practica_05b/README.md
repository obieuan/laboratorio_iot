# Práctica 5B: Comunicación IoT con REST API

Implementación de API REST y clientes HTTP en ESP32.

## Archivos

- `docs/PRACTICA_05B.md` - Documento completo de la práctica
- `codigo/esp32_http_client/esp32_http_client.ino` - Cliente HTTP ESP32
- `codigo/api_rest/app.py` - API REST en Flask
- `codigo/api_rest/polling_client.py` - Cliente de polling

## Inicio Rápido

### API REST
```bash
cd codigo/api_rest
pip3 install flask flask-cors
python3 app.py
```

### ESP32
1. Cambiar configuración en el archivo .ino
2. Compilar y cargar
