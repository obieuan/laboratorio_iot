# Práctica 6A — Aprendiendo lo Normal

Recolección de datos normales y entrenamiento del modelo de detección de anomalías.

## Archivos

| Archivo | Descripción |
|---------|-------------|
| `docs/PRACTICA_06A.md` | Guía completa de la práctica |
| `codigo/esp32/esp32_normal.ino` | Firmware ESP32 — simula servidor normal |
| `codigo/python/colector.py` | Suscriptor MQTT + entrenamiento (con TODOs) |
| `codigo/python/requirements.txt` | Dependencias Python |

## Inicio rápido

```bash
pip install -r codigo/python/requirements.txt
python codigo/python/colector.py
```

## Entregables

- `datos_normales.csv`
- `modelo_normal.pkl` ← necesario para Práctica 6B
