"""
=============================================================
Actividad 3 — Disparar un webhook cuando hay una alerta
EIUM — Universidad Modelo

Este servidor recibe datos de sensores (igual que server.py).
Tu tarea: cuando la temperatura supere el umbral, notificar
a un sistema externo via webhook.

Prerequisito: webhook_receiver.py corriendo en localhost:5001

Ejecutar:
    # Terminal 1
    python webhook_receiver.py

    # Terminal 2
    python actividad_3.py

    # Terminal 3
    python sim.py
=============================================================
"""

import requests
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# ---- CONFIGURACIÓN ----
WEBHOOK_URL       = "http://localhost:5001/webhook"
TEMP_UMBRAL       = 35.0   # °C — por encima de esto se dispara el webhook
# -----------------------


# ================================================================
# TODO 1 — Implementar disparar_webhook(data)
# ================================================================
def disparar_webhook(data: dict):
    """
    Envía un HTTP POST a WEBHOOK_URL con información de la alerta.

    El payload que mandes debe incluir al menos:
      - device_id
      - temperature_c
      - timestamp
      - un campo "alerta" con un mensaje descriptivo

    Usa requests.post() con json=payload.
    Imprime confirmación si el POST fue exitoso (status 200),
    o el error si falló.

    Pista: es exactamente lo que hacía sim.py para mandar datos al servidor.
    """
    # Tu código aquí
    pass


# ================================================================
# TODO 2 — Llamar a disparar_webhook cuando corresponda
# ================================================================
@app.route('/api/sensor', methods=['POST'])
def receive_sensor_data():
    """
    Recibe datos del sensor via HTTP POST.
    Ya está implementado el log en consola.

    Tu tarea: si temperature_c supera TEMP_UMBRAL,
    llama a disparar_webhook(data).
    """
    data = request.get_json()
    temp   = data.get('temperature_c', 0)
    device = data.get('device_id', '?')
    now    = datetime.now().strftime("%H:%M:%S")

    estado = "ALERTA" if temp > TEMP_UMBRAL else "normal"
    print(f"[{now}] {device}  temp={temp}°C  → {estado}")

    # TODO: si temp > TEMP_UMBRAL, disparar el webhook


    return jsonify({"status": "ok"})


if __name__ == '__main__':
    print("=" * 50)
    print("  Servidor IoT con Webhooks")
    print(f"  API:     http://localhost:5000/api/sensor")
    print(f"  Webhook: {WEBHOOK_URL}")
    print(f"  Umbral:  {TEMP_UMBRAL}°C")
    print("=" * 50)
    app.run(port=5000, debug=False)
