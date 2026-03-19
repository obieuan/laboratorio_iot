#!/usr/bin/env python3
"""Cliente de Polling - Práctica 5B"""
import requests
import time
from datetime import datetime

API_URL = "http://localhost:3001"
POLLING_INTERVAL = 5

def mostrar_resumen():
    try:
        response = requests.get(f"{API_URL}/summary", timeout=3)
        if response.status_code == 200:
            data = response.json()
            print("\033[2J\033[H", end="")  # Limpiar pantalla
            print("=" * 70)
            print(f"  RESUMEN - {datetime.now().strftime('%H:%M:%S')}")
            print("=" * 70)
            print(f"  Dispositivos: {data['devices_count']}")
            print("=" * 70)
            
            for device in data['devices']:
                print(f"\n  📡 {device['device_id']}")
                print(f"     Temp: {device['latest_temperature']}°C")
                if 'statistics' in device:
                    stats = device['statistics']
                    print(f"     Stats: Avg={stats['avg']}°C, Range=[{stats['min']}-{stats['max']}°C]")
            
            print("\n" + "=" * 70)
            print(f"  Próxima actualización en {POLLING_INTERVAL}s (Ctrl+C para salir)")
            print("=" * 70)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print(f"Polling cada {POLLING_INTERVAL} segundos...\n")
    try:
        while True:
            mostrar_resumen()
            time.sleep(POLLING_INTERVAL)
    except KeyboardInterrupt:
        print("\n\n✓ Cliente detenido")
