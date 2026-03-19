# Guía de Práctica: De Datos IoT a Machine Learning

## Monitoreo de Cuarto de Servidores

**Curso:** IoT Avanzado — EIUM — Universidad Modelo  
**Duración:** 2 horas (teoría + práctica)

---

## Objetivo

Aprender a recolectar, explorar, visualizar y analizar datos generados por sensores IoT en un cuarto de servidores, aplicando técnicas simples de detección de anomalías como preparación para Machine Learning.

---

## Requisitos previos

### Instalación de librerías

Abre una terminal y ejecuta:

```bash
pip install pandas matplotlib
```

### Archivos necesarios

- `server_room_telemetry.csv` — dataset de telemetría (proporcionado por el profesor)
- `practica_iot_ml.py` — script completo de referencia

---

## Sobre el dataset

El archivo `server_room_telemetry.csv` contiene **864 registros** de 3 servidores monitoreados durante 24 horas con lecturas cada 5 minutos.

| Columna | Descripción | Unidad |
|---------|------------|--------|
| `device_id` | Identificador del servidor | SRV-01, SRV-02, SRV-03 |
| `timestamp` | Fecha y hora de la lectura | YYYY-MM-DD HH:MM:SS |
| `temperature_c` | Temperatura del servidor | °C |
| `power_w` | Consumo eléctrico | Watts |
| `cpu_percent` | Uso de CPU | % |
| `fan_rpm` | Velocidad de ventilador | RPM |

**El dataset contiene anomalías inyectadas intencionalmente.** Tu trabajo es encontrarlas y clasificarlas.

---

## Actividad paso a paso

### Paso 1 — Cargar los datos (5 min)

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("server_room_telemetry.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])

print(df.head())
print(df.shape)
```

**Preguntas:**
- ¿Cuántas filas y columnas tiene el dataset?
- ¿Cuántos servidores hay?

---

### Paso 2 — Explorar los datos (5 min)

```python
# Estadísticas descriptivas
print(df.describe())

# Valores faltantes
print(df.isnull().sum())
```

**Preguntas:**
- ¿Cuál es la temperatura promedio?
- ¿Hay valores faltantes? ¿En qué columna?
- ¿El rango de valores (min-max) se ve razonable para un cuarto de servidores?

---

### Paso 3 — Visualizar series de tiempo (5 min)

```python
# Graficar temperatura de un servidor
srv1 = df[df["device_id"] == "SRV-01"]

plt.figure(figsize=(12, 4))
plt.plot(srv1["timestamp"], srv1["temperature_c"], linewidth=0.8)
plt.xlabel("Tiempo")
plt.ylabel("Temperatura (°C)")
plt.title("SRV-01 — Temperatura 24h")
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

**Actividad:** Repite la gráfica para SRV-02 y SRV-03. Observa las diferencias.

**Preguntas:**
- ¿Ves algún pico inusual?
- ¿La temperatura sigue un patrón durante el día?

---

### Paso 4 — Detección de anomalías: Umbral fijo (5 min)

```python
TEMP_MAX = 30  # °C
TEMP_MIN = 10  # °C

df["alerta_umbral"] = (
    (df["temperature_c"] > TEMP_MAX) |
    (df["temperature_c"] < TEMP_MIN)
)

print(f"Alertas encontradas: {df['alerta_umbral'].sum()}")
print(df[df["alerta_umbral"]][["device_id", "timestamp", "temperature_c"]])
```

**Preguntas:**
- ¿Cuántas alertas detectaste?
- ¿De qué servidores son?
- ¿Los valores te parecen fallas reales o errores de sensor?

---

### Paso 5 — Detección de anomalías: Desviación estándar (5 min)

```python
for srv_id in df["device_id"].unique():
    srv = df[df["device_id"] == srv_id]["temperature_c"]
    mean = srv.mean()
    std = srv.std()
    print(f"{srv_id}: media={mean:.1f}°C, std={std:.1f}°C, "
          f"rango normal=[{mean-2*std:.1f}, {mean+2*std:.1f}]")

# Aplicar detección por z-score
df["alerta_zscore"] = False
for srv_id in df["device_id"].unique():
    mask = df["device_id"] == srv_id
    srv_temp = df.loc[mask, "temperature_c"]
    mean = srv_temp.mean()
    std = srv_temp.std()
    df.loc[mask, "alerta_zscore"] = abs(srv_temp - mean) > 2 * std

print(f"\nAlertas por z-score: {df['alerta_zscore'].sum()}")
```

**Preguntas:**
- ¿Hay diferencia entre las alertas del umbral fijo y las de desviación estándar?
- ¿Qué método es más flexible? ¿Por qué?

---

### Paso 6 (extra) — Visualizar anomalías sobre la gráfica

```python
srv1 = df[df["device_id"] == "SRV-01"]

plt.figure(figsize=(12, 4))
plt.plot(srv1["timestamp"], srv1["temperature_c"], linewidth=0.8, label="Normal")

# Marcar anomalías en rojo
anomalias = srv1[srv1["alerta_umbral"]]
plt.scatter(anomalias["timestamp"], anomalias["temperature_c"],
            color="red", s=30, label="Anomalía", zorder=5)

plt.xlabel("Tiempo")
plt.ylabel("Temperatura (°C)")
plt.title("SRV-01 — Anomalías detectadas")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

---

## Entregable

Al terminar la práctica, responde estas preguntas:

1. ¿Cuántas anomalías encontraste con cada método?
2. ¿Qué tipos de anomalías identificaste? (describe al menos 2)
3. ¿Cuál método te parece más útil y por qué?
4. ¿Cómo implementarías esto en un sistema IoT en tiempo real?

---

## Referencia rápida de pandas

| Función | Descripción |
|---------|------------|
| `df.head()` | Primeras 5 filas |
| `df.shape` | (filas, columnas) |
| `df.describe()` | Estadísticas: media, std, min, max |
| `df.isnull().sum()` | Contar valores faltantes |
| `df[df["col"] > val]` | Filtrar filas por condición |
| `df["col"].mean()` | Promedio de una columna |
| `df["col"].std()` | Desviación estándar |
| `df["col"].hist()` | Histograma rápido |

---

## Siguiente clase

**Machine Learning con scikit-learn:**
- Regresión lineal para predecir temperatura futura
- Clasificación para detectar y categorizar tipos de anomalía automáticamente
