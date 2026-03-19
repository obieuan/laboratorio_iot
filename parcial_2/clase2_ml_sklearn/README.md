# Clase 2 — Machine Learning con scikit-learn

**Curso:** IoT Avanzado — EIUM — Universidad Modelo
**Prerequisito:** Clase 1 (Datos IoT → Análisis)

## Archivos

| Archivo | Descripción |
|---------|-------------|
| `clase2_ml_sklearn.pptx` | Presentación de la clase |
| `guia_practica2_ml_sklearn.md` | Guía paso a paso de la práctica |
| `practica2_ml_sklearn.py` | Script completo de referencia |
| `server_room_telemetry.csv` | Dataset de telemetría (mismo de clase 1) |

## Inicio rápido

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Correr el script desde esta carpeta
cd clase2_ml_sklearn
python practica2_ml_sklearn.py
```

> El script genera 3 gráficas PNG en esta misma carpeta al terminar.

## Contenido

- **Regresión Lineal:** predecir temperatura a partir de CPU, consumo y hora
- **Clasificación (Árbol de Decisión):** detectar y categorizar anomalías automáticamente
