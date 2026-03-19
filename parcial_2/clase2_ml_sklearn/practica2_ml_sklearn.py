"""
=============================================================
Clase 2: Machine Learning para IoT
Regresión Lineal y Clasificación con scikit-learn
EIUM — Universidad Modelo — Prof. Gabriel
=============================================================

Requisitos:
  pip install pandas matplotlib scikit-learn

Usa el mismo dataset: server_room_telemetry.csv
"""

# ============================================================
# PASO 0: Cargar y preparar datos
# ============================================================
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

df = pd.read_csv("server_room_telemetry.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Feature engineering: extraer hora del día (patrón diurno)
df["hour"] = df["timestamp"].dt.hour + df["timestamp"].dt.minute / 60

# Eliminar filas con NaN en temperature_c (son anomalías de sensor)
df_clean = df.dropna(subset=["temperature_c"]).copy()

print("=" * 60)
print("DATOS PREPARADOS")
print("=" * 60)
print(f"Registros totales: {len(df)}")
print(f"Registros limpios: {len(df_clean)}")
print(f"Eliminados (NaN): {len(df) - len(df_clean)}")
print(f"\nColumnas disponibles como features:")
print(f"  cpu_percent, power_w, fan_rpm, hour")
print(f"\nTarget para regresión: temperature_c")

# ============================================================
# PARTE 1: REGRESIÓN LINEAL
# Objetivo: predecir temperatura a partir de CPU, power y hora
# ============================================================
print("\n" + "=" * 60)
print("PARTE 1: REGRESIÓN LINEAL")
print("=" * 60)

from sklearn.linear_model import LinearRegression

# Definir features (X) y target (y)
X_reg = df_clean[["cpu_percent", "power_w", "hour"]]
y_reg = df_clean["temperature_c"]

# Dividir en entrenamiento (80%) y prueba (20%)
X_train, X_test, y_train, y_test = train_test_split(
    X_reg, y_reg, test_size=0.2, random_state=42
)

print(f"\nDatos de entrenamiento: {len(X_train)} registros")
print(f"Datos de prueba:        {len(X_test)} registros")

# Crear y entrenar el modelo
modelo_reg = LinearRegression()
modelo_reg.fit(X_train, y_train)

# Evaluar
r2_train = modelo_reg.score(X_train, y_train)
r2_test = modelo_reg.score(X_test, y_test)

print(f"\nResultados:")
print(f"  R² en entrenamiento: {r2_train:.4f}")
print(f"  R² en prueba:        {r2_test:.4f}")
print(f"  (1.0 = perfecto, 0.0 = no predice nada)")

# Coeficientes aprendidos
print(f"\nCoeficientes aprendidos:")
for feat, coef in zip(["cpu_percent", "power_w", "hour"], modelo_reg.coef_):
    print(f"  {feat}: {coef:.4f}")
print(f"  intercepto: {modelo_reg.intercept_:.4f}")

# Ejemplo de predicción
ejemplo = [[40, 200, 14]]  # CPU=40%, power=200W, hora=14:00
pred = modelo_reg.predict(ejemplo)
print(f"\nEjemplo de predicción:")
print(f"  CPU=40%, power=200W, hora=14:00")
print(f"  Temperatura predicha: {pred[0]:.1f}°C")

# --- Gráfica: real vs predicho ---
y_pred = modelo_reg.predict(X_test)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Scatter: real vs predicho
ax = axes[0]
ax.scatter(y_test, y_pred, alpha=0.3, s=10, color="#7C3AED")
ax.plot([y_test.min(), y_test.max()],
        [y_test.min(), y_test.max()],
        "r--", linewidth=1.5, label="Predicción perfecta")
ax.set_xlabel("Temperatura Real (°C)")
ax.set_ylabel("Temperatura Predicha (°C)")
ax.set_title(f"Regresión Lineal — R² = {r2_test:.3f}")
ax.legend()
ax.grid(True, alpha=0.3)

# Residuales
ax = axes[1]
residuales = y_test.values - y_pred
ax.hist(residuales, bins=30, color="#7C3AED", edgecolor="white", alpha=0.8)
ax.set_xlabel("Error (°C)")
ax.set_ylabel("Frecuencia")
ax.set_title("Distribución de Errores")
ax.axvline(0, color="red", linestyle="--", linewidth=1)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("regresion_resultados.png", dpi=150, bbox_inches="tight")
plt.show()
print("→ Gráfica guardada: regresion_resultados.png")


# ============================================================
# PARTE 2: CLASIFICACIÓN CON ÁRBOL DE DECISIÓN
# Objetivo: clasificar registros como normal o anomalía
# ============================================================
print("\n" + "=" * 60)
print("PARTE 2: CLASIFICACIÓN — ÁRBOL DE DECISIÓN")
print("=" * 60)

from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report

# Crear etiquetas basadas en las reglas de la clase anterior
# (en un caso real, estas etiquetas vendrían de un experto)
df_clean["label"] = "normal"
df_clean.loc[df_clean["temperature_c"] > 30, "label"] = "temp_alta"
df_clean.loc[df_clean["temperature_c"] < 10, "label"] = "temp_imposible"
df_clean.loc[df_clean["power_w"] > 350, "label"] = "power_alto"

print(f"\nDistribución de etiquetas:")
print(df_clean["label"].value_counts().to_string())

# Features y target
X_clf = df_clean[["temperature_c", "cpu_percent", "power_w", "fan_rpm"]]
y_clf = df_clean["label"]

# Train/test split
X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(
    X_clf, y_clf, test_size=0.2, random_state=42
)

# Entrenar árbol de decisión
arbol = DecisionTreeClassifier(max_depth=4, random_state=42)
arbol.fit(X_train_c, y_train_c)

# Predecir y evaluar
y_pred_c = arbol.predict(X_test_c)
accuracy = accuracy_score(y_test_c, y_pred_c)

print(f"\nAccuracy: {accuracy:.4f} ({accuracy*100:.1f}%)")
print(f"\nReporte detallado:")
print(classification_report(y_test_c, y_pred_c))

# Importancia de features
print("Importancia de cada feature:")
for feat, imp in zip(X_clf.columns, arbol.feature_importances_):
    bar = "█" * int(imp * 40)
    print(f"  {feat:15s}: {imp:.3f} {bar}")

# Ejemplo de predicción
ejemplo_normal = [[23.5, 30, 200, 1100]]
ejemplo_anomalo = [[38.0, 90, 400, 2000]]

print(f"\nEjemplos de predicción:")
print(f"  temp=23.5, cpu=30, power=200, fan=1100")
print(f"  → Predicción: {arbol.predict(ejemplo_normal)[0]}")
print(f"\n  temp=38.0, cpu=90, power=400, fan=2000")
print(f"  → Predicción: {arbol.predict(ejemplo_anomalo)[0]}")

# --- Gráfica: importancia de features ---
fig, ax = plt.subplots(figsize=(8, 4))
importances = arbol.feature_importances_
features = X_clf.columns
colors = ["#7C3AED", "#A78BFA", "#C4B5FD", "#DDD6FE"]
bars = ax.barh(features, importances, color=colors, edgecolor="white")
ax.set_xlabel("Importancia")
ax.set_title("Árbol de Decisión — Importancia de Features")
ax.grid(True, alpha=0.3, axis="x")

for bar, val in zip(bars, importances):
    ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
            f"{val:.3f}", va="center", fontsize=10)

plt.tight_layout()
plt.savefig("clasificacion_importancia.png", dpi=150, bbox_inches="tight")
plt.show()
print("→ Gráfica guardada: clasificacion_importancia.png")

# --- Gráfica: scatter coloreado por predicción ---
fig, ax = plt.subplots(figsize=(10, 5))
color_map = {"normal": "#10B981", "temp_alta": "#EF4444",
             "temp_imposible": "#3B82F6", "power_alto": "#F59E0B"}
for label in y_pred_c:
    pass  # just to get unique labels

for label, color in color_map.items():
    mask = y_pred_c == label
    if mask.sum() > 0:
        ax.scatter(X_test_c.loc[mask, "temperature_c"],
                   X_test_c.loc[mask, "power_w"],
                   c=color, label=label, s=20, alpha=0.7)

ax.set_xlabel("Temperatura (°C)")
ax.set_ylabel("Consumo (W)")
ax.set_title("Clasificación de Registros — Árbol de Decisión")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("clasificacion_scatter.png", dpi=150, bbox_inches="tight")
plt.show()
print("→ Gráfica guardada: clasificacion_scatter.png")


# ============================================================
# RESUMEN
# ============================================================
print("\n" + "=" * 60)
print("RESUMEN")
print("=" * 60)
print(f"""
REGRESIÓN LINEAL:
  Predice temperatura a partir de CPU, power, hora
  R² = {r2_test:.3f} (explica {r2_test*100:.0f}% de la variación)
  Uso: anticipar temperaturas futuras → prevenir sobrecalentamiento

CLASIFICACIÓN (Árbol de Decisión):
  Clasifica registros en: normal, temp_alta, temp_imposible, power_alto
  Accuracy = {accuracy*100:.1f}%
  Uso: detectar y categorizar anomalías automáticamente

DIFERENCIA CLAVE:
  Regresión → responde con un NÚMERO (¿cuánto?)
  Clasificación → responde con una ETIQUETA (¿qué tipo?)

SIGUIENTE PASO EN TU PROYECTO:
  1. Recolectar datos de tu sistema IoT
  2. Etiquetar eventos (normal vs anomalía)
  3. Entrenar un modelo
  4. Desplegarlo para clasificar datos en tiempo real
""")
