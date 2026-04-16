"""
=============================================================
DEMO — Receptor de Webhooks
EIUM — Universidad Modelo

Este script simula ser un sistema externo que recibe notificaciones:
un canal de Slack, un sistema de alertas, un servicio de email, etc.

Corre este script en una terminal.
Cuando alguien haga POST a http://localhost:5001/webhook,
verás el mensaje aquí.

Ejecutar:
    python webhook_receiver.py
=============================================================
"""

from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)
received_count = 0


@app.route('/webhook', methods=['POST'])
def receive_webhook():
    global received_count
    received_count += 1

    data = request.get_json()
    now  = datetime.now().strftime("%H:%M:%S")

    print(f"\n{'='*50}")
    print(f"  WEBHOOK RECIBIDO #{received_count}  —  {now}")
    print(f"{'='*50}")

    if data:
        for key, value in data.items():
            print(f"  {key:<20} {value}")
    else:
        print("  (payload vacío)")

    print(f"{'='*50}\n")

    # En un sistema real aquí irían:
    #   - requests.post(SLACK_URL, json={"text": "Alerta: ..."})
    #   - smtplib.sendmail(...)
    #   - db.insert(data)
    #   - trigger otro workflow

    return jsonify({"status": "received", "count": received_count})


@app.route('/', methods=['GET'])
def index():
    return f"Receptor de webhooks activo. Recibidos: {received_count}"


if __name__ == '__main__':
    print("=" * 50)
    print("  Receptor de Webhooks")
    print("  Escuchando en: http://localhost:5001/webhook")
    print("  Esperando POSTs...")
    print("=" * 50)
    app.run(port=5001, debug=False)
