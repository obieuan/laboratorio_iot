"""
=============================================================
Actividad 2 — Conectar MQTT con el dashboard WebSocket
EIUM — Universidad Modelo

Este script es el puente entre el broker MQTT y el dashboard.
Cuando llegue un mensaje al topic MQTT, lo reenvías al servidor
via HTTP POST — y el servidor lo empuja a todos los dashboards.

Arquitectura:
  [ESP32 / sim.py] → MQTT → [este script] → HTTP POST → [server.py] → WebSocket → [Dashboard]

Prerequisitos:
  - server.py corriendo en localhost:5000  (python server.py)
  - Broker MQTT corriendo en localhost     (mosquitto -v)
  - En otra terminal: python sim.py  (o un ESP32 real)

Dependencias:
  pip install paho-mqtt requests
=============================================================
"""

import json
import requests
import paho.mqtt.client as mqtt

# ---- CONFIGURACIÓN ----
BROKER     = "localhost"
TOPIC      = "iot/lab/sensores"
SERVER_URL = "http://localhost:5000/api/sensor"
# -----------------------


# ================================================================
# TODO 1 — Implementar el callback on_message
# ================================================================
def on_message(client, userdata, msg):
    """
    Se ejecuta cada vez que llega un mensaje al topic MQTT.

    Pasos:
      1. Decodifica el payload: msg.payload.decode()
      2. Parsea el JSON con json.loads() dentro de un try/except
      3. Envía el dict al servidor con requests.post(SERVER_URL, json=data)
      4. Imprime confirmación: device_id y temperatura

    Si el JSON está malformado, imprime el error y no hagas nada.
    """
    # Tu código aquí
    pass


# ================================================================
# TODO 2 — Conectar al broker y suscribirse al topic
# ================================================================
def main():
    """
    Crea el cliente MQTT, asigna on_message,
    conecta a BROKER en el puerto 1883,
    suscríbete a TOPIC,
    e inicia el loop con client.loop_forever().

    Pista: es exactamente como en la Práctica 5A.
    """
    # Tu código aquí
    pass


if __name__ == '__main__':
    print("=" * 50)
    print("Bridge MQTT → WebSocket Dashboard")
    print(f"  Escuchando: {BROKER} / {TOPIC}")
    print(f"  Reenviando: {SERVER_URL}")
    print("=" * 50)
    main()
