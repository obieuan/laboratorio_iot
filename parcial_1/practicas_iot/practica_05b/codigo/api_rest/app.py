#!/usr/bin/env python3
"""API REST - Práctica 5B"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from collections import defaultdict
import time
import statistics

app = Flask(__name__)
CORS(app)

device_data = defaultdict(list)
MAX_READINGS = 100

stats_global = {
    'total_requests': 0,
    'requests_by_device': defaultdict(int),
    'api_start_time': time.time()
}

@app.route('/', methods=['GET'])
def root():
    uptime = time.time() - stats_global['api_start_time']
    return jsonify({
        'api': 'IoT REST API - Práctica 5B',
        'version': '1.0',
        'status': 'online',
        'uptime_seconds': round(uptime, 2),
        'devices_registered': len(device_data)
    }), 200

@app.route('/devices/<device_id>/data', methods=['POST'])
def post_device_data(device_id):
    stats_global['total_requests'] += 1
    stats_global['requests_by_device'][device_id] += 1
    
    data = request.get_json()
    if not data or 'temperatura' not in data:
        return jsonify({'error': 'temperatura required'}), 400
    
    reading = {
        'device_id': device_id,
        'temperatura': float(data['temperatura']),
        'timestamp_device': data.get('timestamp', 0),
        'timestamp_server': time.time(),
        'received_at': datetime.now().isoformat()
    }
    
    device_data[device_id].append(reading)
    if len(device_data[device_id]) > MAX_READINGS:
        device_data[device_id].pop(0)
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] POST from {device_id}: {data['temperatura']}°C")
    
    return jsonify({
        'status': 'success',
        'device_id': device_id,
        'reading_number': len(device_data[device_id])
    }), 201

@app.route('/devices/<device_id>/data', methods=['GET'])
def get_device_data(device_id):
    stats_global['total_requests'] += 1
    if device_id not in device_data:
        return jsonify({'error': f'Device {device_id} not found'}), 404
    
    limit = request.args.get('limit', default=10, type=int)
    readings = device_data[device_id][-limit:][::-1]
    
    return jsonify({
        'device_id': device_id,
        'count': len(readings),
        'data': readings
    }), 200

@app.route('/summary', methods=['GET'])
def get_summary():
    stats_global['total_requests'] += 1
    summary = []
    
    for device_id in sorted(device_data.keys()):
        readings = device_data[device_id]
        if readings:
            latest = readings[-1]
            temps = [r['temperatura'] for r in readings]
            summary.append({
                'device_id': device_id,
                'latest_temperature': latest.get('temperatura'),
                'last_seen': latest.get('received_at'),
                'statistics': {
                    'count': len(temps),
                    'avg': round(statistics.mean(temps), 2),
                    'min': round(min(temps), 2),
                    'max': round(max(temps), 2)
                }
            })
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'devices_count': len(summary),
        'devices': summary
    }), 200

if __name__ == '__main__':
    print("=" * 70)
    print("  API REST - Práctica 5B")
    print("  Puerto: 3001")
    print("=" * 70)
    app.run(host='0.0.0.0', port=3001, debug=False)
