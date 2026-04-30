"""
SIMULADOR DE SENSORES IoT
Esto simula 3 servidores mandando telemetría.
NO MODIFICAR — es el equivalente a tu ESP32 mandando datos.

Uso: python sensor_simulator.py
Requiere: pip install requests
Asegúrate de que tu server.py esté corriendo en localhost:5000
"""

import requests
import random
import math
import time
from datetime import datetime

SERVER_URL = "http://localhost:5000/api/sensor"

servers = {
    "SRV-01": {"base_temp": 22.0, "base_power": 180},
    "SRV-02": {"base_temp": 23.5, "base_power": 220},
    "SRV-03": {"base_temp": 21.0, "base_power": 160},
}

count = 0

def generate(srv_id, params):
    global count
    count += 1
    now = datetime.now()
    hour = now.hour + now.minute / 60.0
    wf = 0.3 * math.exp(-0.5 * ((hour - 14) / 4) ** 2)
    
    temp = params["base_temp"] + wf * 5 + random.gauss(0, 0.3)
    if srv_id == "SRV-01" and count % 30 == 0:
        temp += random.uniform(10, 15)
    
    return {
        "device_id": srv_id,
        "timestamp": now.strftime("%H:%M:%S"),
        "temperature_c": round(temp, 1),
        "power_w": round(params["base_power"] + wf * 80 + random.gauss(0, 3), 1),
        "cpu_percent": round(max(5, min(100, 25 + wf * 60 + random.gauss(0, 5))), 1),
        "fan_rpm": round(max(800, 1000 + (temp - 22) * 200 + random.gauss(0, 20)), 0),
    }

if __name__ == '__main__':
    print("=" * 50)
    print("  SIMULADOR DE SENSORES IoT")
    print("  Mandando datos a:", SERVER_URL)
    print("=" * 50)
    
    print("\n  Conectando...", end="", flush=True)
    while True:
        try:
            requests.get("http://localhost:5000", timeout=1)
            print(" OK!\n")
            break
        except:
            print(".", end="", flush=True)
            time.sleep(1)
    
    while True:
        for srv_id, params in servers.items():
            data = generate(srv_id, params)
            try:
                r = requests.post(SERVER_URL, json=data, timeout=2)
                ok = "OK" if r.status_code == 200 else "FAIL"
            except:
                ok = "ERR"
            
            alert = " *** ANOMALIA ***" if data["temperature_c"] > 30 else ""
            print(f"  [{ok}] {data['device_id']}  "
                  f"{data['temperature_c']:>5}°C  "
                  f"{data['power_w']:>6}W  "
                  f"{data['cpu_percent']:>5}%  "
                  f"{data['fan_rpm']:>6} RPM{alert}")
        
        print()
        time.sleep(2)
