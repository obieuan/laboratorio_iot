#!/usr/bin/env python3
"""Gateway IoT - Raspberry Pi Zero W - Práctica 5C"""
from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import json
import threading
import time
from datetime import datetime
from collections import defaultdict
import statistics

# CONFIGURACIÓN
FLASK_PORT = 5000
MQTT_BROKER = "devlabs.eium.com.mx"
MQTT_PORT = 3000
MQTT_TOPIC = "gateway/alpha"
AGGREGATION_INTERVAL = 30
MAX_BUFFER = 1000

app = Flask(__name__)
device_buffer = defaultdict(list)
offline_buffer = []
mqtt_client = mqtt.Client(client_id="gateway_rpi")
mqtt_connected = False

stats = {
    'messages_received': 0,
    'messages_sent': 0,
    'messages_buffered': 0,
    'devices_registered': set(),
    'start_time': time.time()
}

# MQTT CALLBACKS
def on_mqtt_connect(client, userdata, flags, rc):
    global mqtt_connected
    mqtt_connected = (rc == 0)
    status = "✓ Conectado" if rc == 0 else f"✗ Error: {rc}"
    print(f"[MQTT] {status}")
    
    if rc == 0 and offline_buffer:
        print(f"[MQTT] Enviando {len(offline_buffer)} mensajes del buffer")
        for msg in offline_buffer:
            client.publish(msg['topic'], msg['payload'], qos=1)
        offline_buffer.clear()
        stats['messages_buffered'] = 0

def on_mqtt_disconnect(client, userdata, rc):
    global mqtt_connected
    mqtt_connected = False
    print(f"[MQTT] Desconectado")

mqtt_client.on_connect = on_mqtt_connect
mqtt_client.on_disconnect = on_mqtt_disconnect

def connect_mqtt():
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()
    except Exception as e:
        print(f"[MQTT] Error: {e}")

def publish_to_mqtt(topic, payload, qos=1):
    if mqtt_connected:
        result = mqtt_client.publish(topic, payload, qos=qos)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            stats['messages_sent'] += 1
            return True
    
    if len(offline_buffer) < MAX_BUFFER:
        offline_buffer.append({'topic': topic, 'payload': payload})
        stats['messages_buffered'] = len(offline_buffer)
    return False

# EDGE COMPUTING
def calculate_statistics(readings):
    if not readings:
        return None
    temps = [r['temperatura'] for r in readings]
    return {
        'count': len(temps),
        'avg': round(statistics.mean(temps), 2),
        'min': round(min(temps), 2),
        'max': round(max(temps), 2),
        'std': round(statistics.stdev(temps), 2) if len(temps) > 1 else 0
    }

def periodic_aggregation():
    while True:
        time.sleep(AGGREGATION_INTERVAL)
        if not device_buffer:
            continue
        
        aggregation = {
            'gateway_id': 'rpi_zero_alpha',
            'timestamp': time.time(),
            'devices': []
        }
        
        for device_id, readings in device_buffer.items():
            if readings:
                aggregation['devices'].append({
                    'device_id': device_id,
                    'statistics': calculate_statistics(readings),
                    'last_reading': readings[-1]
                })
        
        topic = f"{MQTT_TOPIC}/aggregate"
        payload = json.dumps(aggregation)
        if publish_to_mqtt(topic, payload):
            print(f"[Edge] Agregación: {len(aggregation['devices'])} dispositivos")

# FLASK ENDPOINTS
@app.route('/health', methods=['GET'])
def health():
    uptime = time.time() - stats['start_time']
    return jsonify({
        'status': 'online',
        'uptime_seconds': round(uptime, 2),
        'mqtt_connected': mqtt_connected,
        'devices_registered': len(stats['devices_registered']),
        'messages_received': stats['messages_received'],
        'messages_sent': stats['messages_sent'],
        'messages_buffered': stats['messages_buffered']
    }), 200

@app.route('/gateway/data', methods=['POST'])
def receive_data():
    stats['messages_received'] += 1
    data = request.get_json()
    
    if not data or 'device_id' not in data:
        return jsonify({'error': 'device_id required'}), 400
    
    device_id = data['device_id']
    stats['devices_registered'].add(device_id)
    
    data['gateway_timestamp'] = time.time()
    data['gateway_received_at'] = datetime.now().isoformat()
    
    device_buffer[device_id].append(data)
    if len(device_buffer[device_id]) > 100:
        device_buffer[device_id].pop(0)
    
    topic = f"{MQTT_TOPIC}/devices/{device_id}/data"
    payload = json.dumps(data)
    success = publish_to_mqtt(topic, payload)
    
    temp = data.get('temperatura', 'N/A')
    status = '✓' if success else '⊙'
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {device_id}: {temp}°C {status}")
    
    return jsonify({
        'status': 'success' if success else 'buffered',
        'device_id': device_id,
        'mqtt_connected': mqtt_connected
    }), 200 if success else 202

@app.route('/gateway/devices', methods=['GET'])
def list_devices():
    devices_info = []
    for device_id in stats['devices_registered']:
        readings = device_buffer.get(device_id, [])
        if readings:
            devices_info.append({
                'device_id': device_id,
                'last_temperature': readings[-1].get('temperatura'),
                'reading_count': len(readings)
            })
    return jsonify({'device_count': len(devices_info), 'devices': devices_info}), 200

@app.route('/gateway/aggregate', methods=['GET'])
def get_aggregate():
    aggregation = {}
    for device_id, readings in device_buffer.items():
        if readings:
            aggregation[device_id] = {
                'statistics': calculate_statistics(readings),
                'last_reading': readings[-1]
            }
    return jsonify({'aggregation': aggregation}), 200

if __name__ == '__main__':
    print("=" * 70)
    print("  GATEWAY IoT - Raspberry Pi Zero W")
    print("=" * 70)
    print(f"  Flask: {FLASK_PORT}")
    print(f"  MQTT: {MQTT_BROKER}:{MQTT_PORT}")
    print("=" * 70)
    
    connect_mqtt()
    
    agg_thread = threading.Thread(target=periodic_aggregation, daemon=True)
    agg_thread.start()
    
    app.run(host='0.0.0.0', port=FLASK_PORT, debug=False)
