# Práctica 6B — Escenarios en Vivo

Aplicar el modelo de la Práctica 6A a datos nuevos en tiempo real.

## Archivos

| Archivo | Descripción |
|---------|-------------|
| `docs/PRACTICA_06B.md` | Guía completa de la práctica |
| `codigo/esp32/firmware_equipo_a.ino` | Firmware para Equipo A |
| `codigo/esp32/firmware_equipo_b.ino` | Firmware para Equipo B |
| `codigo/esp32/firmware_equipo_c.ino` | Firmware para Equipo C |
| `codigo/python/detector.py` | Sistema de análisis en tiempo real (con TODOs) |
| `codigo/python/requirements.txt` | Dependencias Python |

## Prerequisito

Tener `modelo_normal.pkl` de la Práctica 6A en la carpeta `codigo/python/`.

## Inicio rápido

```bash
cp ../practica_06a_datos_normales/modelo_normal.pkl codigo/python/
python codigo/python/detector.py
```
