#!/usr/bin/env python3
"""
Monitor MQTT para Práctica 5A
Universidad Modelo EIUM

Escucha todos los mensajes del equipo y los muestra en consola
con formato legible y estadísticas en tiempo real.
"""

import paho.mqtt.client as mqtt
import json
from datetime import datetime
import sys

# ==================== CONFIGURACIÓN ====================
BROKER = "localhost"
PORT = 3000
BASE_TOPIC = "equipo/alpha/#"

# ==================== ESTADÍSTICAS ====================
message_count = {}
total_messages = 0

# ==================== CALLBACKS MQTT ====================
def on_connect(client, userdata, flags, rc):
    """Callback cuando se conecta al broker"""
    if rc == 0:
        print("=" * 70)
        print("✓ CONECTADO AL BROKER MQTT")
        print("=" * 70)
        print(f"Broker: {BROKER}:{PORT}")
        print(f"Suscrito a: {BASE_TOPIC}")
        print("=" * 70)
        print()
        client.subscribe(BASE_TOPIC)
    else:
        print(f"✗ Error de conexión. Código: {rc}")
        sys.exit(1)

def on_message(client, userdata, msg):
    """Callback cuando se recibe un mensaje"""
    global message_count, total_messages
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    topic = msg.topic
    payload = msg.payload.decode('utf-8', errors='ignore')
    
    # Contar mensajes
    total_messages += 1
    if topic in message_count:
        message_count[topic] += 1
    else:
        message_count[topic] = 1
    
    # Formatear salida
    print(f"┌─ [{timestamp}] Mensaje #{total_messages}")
    print(f"│  Topic: {topic}")
    
    # Intentar parsear como JSON para mejor formato
    try:
        data = json.loads(payload)
        print(f"│  Payload:")
        for key, value in data.items():
            print(f"│    {key}: {value}")
    except:
        print(f"│  Payload: {payload}")
    
    print(f"└─ Total del topic: {message_count[topic]} mensajes")
    print()

def on_disconnect(client, userdata, rc):
    """Callback cuando se desconecta"""
    print("\n✗ Desconectado del broker")
    if rc != 0:
        print(f"Desconexión inesperada. Código: {rc}")

# ==================== MAIN ====================
def main():
    # Crear cliente MQTT
    client = mqtt.Client(client_id="monitor_python")
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    # Conectar al broker
    try:
        print("Conectando al broker MQTT...")
        client.connect(BROKER, PORT, 60)
        
        # Iniciar loop (bloquea hasta Ctrl+C)
        print("Presiona Ctrl+C para detener el monitor\n")
        client.loop_forever()
        
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("RESUMEN DE LA SESIÓN")
        print("=" * 70)
        print(f"Total de mensajes recibidos: {total_messages}")
        print(f"Topics únicos: {len(message_count)}")
        print("\nDistribución por topic:")
        for topic, count in sorted(message_count.items(), key=lambda x: x[1], reverse=True):
            print(f"  {count:4d}  {topic}")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
