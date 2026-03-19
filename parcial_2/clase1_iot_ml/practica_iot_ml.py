"""
=============================================================
Clase: De Datos IoT a Machine Learning
Escenario: Monitoreo de Cuarto de Servidores
EIUM — Universidad Modelo — Prof. Gabriel
=============================================================

Este script cubre paso a paso el análisis de datos IoT:
1. Instalación y carga de datos
2. Exploración de datos (EDA)
3. Visualización de series de tiempo
4. Detección de anomalías (umbral fijo y desviación estándar)
5. Análisis y clasificación de anomalías

Dataset: server_room_telemetry.csv
- 864 registros (3 servidores × 288 lecturas c/5 min = 24 horas)
- Columnas: device_id, timestamp, temperature_c, power_w, cpu_percent, fan_rpm
- Contiene 4 tipos de anomalías inyectadas
"""

# ============================================================
# PASO 0: Instalación (ejecutar en terminal si no tienes las librerías)
# ============================================================
# pip install pandas matplotlib

# ============================================================
# PASO 1: Cargar datos
# ============================================================
import pandas as pd
import matplotlib.pyplot as plt

# Cargar CSV
df = pd.read_csv("server_room_telemetry.csv")

# Convertir timestamp a datetime para poder graficar bien
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Vista rápida
print("=" * 60)
print("PASO 1: Vista general del dataset")
print("=" * 60)
print(f"\nForma del dataset: {df.shape[0]} filas × {df.shape[1]} columnas")
print(f"\nColumnas: {list(df.columns)}")
print(f"\nServidores: {df['device_id'].unique()}")
print(f"\nPrimeras 5 filas:")
print(df.head())

# ============================================================
# PASO 2: Exploración de datos (EDA)
# ============================================================
print("\n" + "=" * 60)
print("PASO 2: Exploración de datos")
print("=" * 60)

# Estadísticas descriptivas
print("\nEstadísticas descriptivas:")
print(df.describe())

# Valores faltantes
print("\nValores faltantes por columna:")
print(df.isnull().sum())

# Tipos de datos
print("\nTipos de datos:")
print(df.dtypes)

# Rango de tiempo
print(f"\nRango temporal: {df['timestamp'].min()} → {df['timestamp'].max()}")

# ============================================================
# PASO 3: Visualización — Series de tiempo
# ============================================================
print("\n" + "=" * 60)
print("PASO 3: Visualización")
print("=" * 60)

# --- Gráfica 1: Temperatura de los 3 servidores ---
fig, axes = plt.subplots(3, 1, figsize=(14, 8), sharex=True)
fig.suptitle("Temperatura por Servidor — 24 horas", fontsize=16, fontweight="bold")

colors = {"SRV-01": "#0891B2", "SRV-02": "#10B981", "SRV-03": "#F59E0B"}

for ax, srv_id in zip(axes, ["SRV-01", "SRV-02", "SRV-03"]):
    srv = df[df["device_id"] == srv_id]
    ax.plot(srv["timestamp"], srv["temperature_c"],
            linewidth=0.8, color=colors[srv_id], label=srv_id)
    ax.set_ylabel("Temp (°C)")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)

axes[-1].set_xlabel("Tiempo")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("grafica_temperatura_servidores.png", dpi=150, bbox_inches="tight")
plt.show()
print("→ Gráfica guardada: grafica_temperatura_servidores.png")

# --- Gráfica 2: Consumo eléctrico ---
fig, ax = plt.subplots(figsize=(14, 4))
for srv_id in df["device_id"].unique():
    srv = df[df["device_id"] == srv_id]
    ax.plot(srv["timestamp"], srv["power_w"],
            linewidth=0.8, color=colors[srv_id], label=srv_id, alpha=0.8)

ax.set_title("Consumo Eléctrico por Servidor", fontsize=14, fontweight="bold")
ax.set_xlabel("Tiempo")
ax.set_ylabel("Potencia (W)")
ax.legend()
ax.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("grafica_consumo_servidores.png", dpi=150, bbox_inches="tight")
plt.show()
print("→ Gráfica guardada: grafica_consumo_servidores.png")

# --- Gráfica 3: Histograma de temperatura ---
fig, ax = plt.subplots(figsize=(8, 4))
# Filtrar NaN para el histograma
temp_valid = df["temperature_c"].dropna()
ax.hist(temp_valid, bins=40, color="#0891B2", edgecolor="white", alpha=0.8)
ax.set_title("Distribución de Temperatura (todos los servidores)", fontsize=14, fontweight="bold")
ax.set_xlabel("Temperatura (°C)")
ax.set_ylabel("Frecuencia")
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("histograma_temperatura.png", dpi=150, bbox_inches="tight")
plt.show()
print("→ Gráfica guardada: histograma_temperatura.png")

# ============================================================
# PASO 4: Detección de anomalías
# ============================================================
print("\n" + "=" * 60)
print("PASO 4: Detección de anomalías")
print("=" * 60)

# --- Método 1: Umbral fijo ---
TEMP_MAX = 30      # °C — arriba de esto es sospechoso
TEMP_MIN = 10      # °C — abajo de esto es imposible en un cuarto de servidores
POWER_MAX = 350    # W — consumo anormalmente alto

df["alerta_umbral"] = (
    (df["temperature_c"] > TEMP_MAX) |
    (df["temperature_c"] < TEMP_MIN) |
    (df["power_w"] > POWER_MAX)
)

n_alertas_umbral = df["alerta_umbral"].sum()
print(f"\nMétodo 1 — Umbral fijo:")
print(f"  Reglas: temp > {TEMP_MAX}°C, temp < {TEMP_MIN}°C, power > {POWER_MAX}W")
print(f"  Alertas encontradas: {n_alertas_umbral}")

# Mostrar las alertas
if n_alertas_umbral > 0:
    print("\n  Muestra de alertas:")
    print(df[df["alerta_umbral"]][["device_id", "timestamp", "temperature_c", "power_w"]].head(10).to_string(index=False))

# --- Método 2: Desviación estándar (por servidor) ---
df["alerta_zscore"] = False

for srv_id in df["device_id"].unique():
    mask = df["device_id"] == srv_id
    srv_data = df.loc[mask, "temperature_c"]

    mean = srv_data.mean()
    std = srv_data.std()

    # Valores a más de 2 desviaciones estándar
    is_anomaly = abs(srv_data - mean) > 2 * std
    df.loc[mask, "alerta_zscore"] = is_anomaly

    print(f"\n  {srv_id}: media={mean:.1f}°C, std={std:.1f}°C, rango normal=[{mean-2*std:.1f}, {mean+2*std:.1f}]")

n_alertas_zscore = df["alerta_zscore"].sum()
print(f"\nMétodo 2 — Desviación estándar (2σ):")
print(f"  Alertas encontradas: {n_alertas_zscore}")

# --- Método 3 (bonus): Valores faltantes como anomalía ---
df["dato_faltante"] = df["temperature_c"].isnull()
n_faltantes = df["dato_faltante"].sum()
print(f"\nDatos faltantes (posible falla de sensor): {n_faltantes}")

# ============================================================
# PASO 5: Visualizar anomalías en la gráfica
# ============================================================
print("\n" + "=" * 60)
print("PASO 5: Visualización de anomalías")
print("=" * 60)

fig, axes = plt.subplots(3, 1, figsize=(14, 9), sharex=True)
fig.suptitle("Anomalías Detectadas — Temperatura por Servidor", fontsize=16, fontweight="bold")

for ax, srv_id in zip(axes, ["SRV-01", "SRV-02", "SRV-03"]):
    srv = df[df["device_id"] == srv_id]

    # Línea normal
    ax.plot(srv["timestamp"], srv["temperature_c"],
            linewidth=0.8, color=colors[srv_id], label=srv_id)

    # Marcar anomalías por umbral
    anomalias = srv[srv["alerta_umbral"]]
    if len(anomalias) > 0:
        ax.scatter(anomalias["timestamp"], anomalias["temperature_c"],
                   color="red", s=30, zorder=5, label="Anomalía (umbral)")

    # Marcar anomalías por z-score
    anomalias_z = srv[srv["alerta_zscore"] & ~srv["alerta_umbral"]]
    if len(anomalias_z) > 0:
        ax.scatter(anomalias_z["timestamp"], anomalias_z["temperature_c"],
                   color="orange", s=30, zorder=5, marker="^", label="Anomalía (2σ)")

    ax.set_ylabel("Temp (°C)")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(True, alpha=0.3)

axes[-1].set_xlabel("Tiempo")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("anomalias_detectadas.png", dpi=150, bbox_inches="tight")
plt.show()
print("→ Gráfica guardada: anomalias_detectadas.png")

# ============================================================
# PASO 6: Resumen de hallazgos
# ============================================================
print("\n" + "=" * 60)
print("RESUMEN DE HALLAZGOS")
print("=" * 60)

print(f"""
Dataset: {df.shape[0]} lecturas de {df['device_id'].nunique()} servidores en 24 horas

Anomalías detectadas:
  • Umbral fijo:          {n_alertas_umbral} alertas
  • Desviación estándar:  {n_alertas_zscore} alertas
  • Datos faltantes:      {n_faltantes} registros

Tipos de anomalía en los datos:
  1. Falla de enfriamiento (SRV-01): pico de temperatura ~35-40°C
  2. Pico de consumo (SRV-02): power_w > 350W
  3. Sensor con datos faltantes (SRV-03): temperature_c = NaN
  4. Temperatura imposible (SRV-03): valores negativos (-5 a 2°C)

Pregunta para reflexionar:
  ¿Cómo podrías usar estos métodos en tu proyecto IoT?
  ¿Qué ventajas tendría un modelo ML sobre estos métodos simples?

Siguiente clase: ML con scikit-learn
  → Regresión: predecir temperatura futura
  → Clasificación: detectar tipo de anomalía automáticamente
""")
