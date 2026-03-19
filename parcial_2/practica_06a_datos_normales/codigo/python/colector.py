"""
=============================================================
Práctica 6A — Colector de datos y entrenamiento del modelo
EIUM — Universidad Modelo

Este script:
  1. Se suscribe al topic MQTT y guarda las lecturas en vivo
  2. Al terminar, entrenas un modelo de regresión lineal
  3. Guardas el modelo para usarlo en la Práctica 6B

Hay 4 secciones marcadas con TODO — esas son las que implementas.
=============================================================
"""

import json
import joblib
import pandas as pd
import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt
from datetime import datetime
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# ---- CONFIGURACIÓN ----
BROKER          = "localhost"
TOPIC           = "iot/lab/sensores"
MINIMO_LECTURAS = 300          # ~2.5 min con 3 ESP32s a 2 lecturas/seg
ARCHIVO_DATOS   = "datos_normales.csv"
ARCHIVO_MODELO  = "modelo_normal.pkl"
# -----------------------

lecturas = []


# ================================================================
# TODO 1 — Parsear el mensaje MQTT
# ================================================================
def procesar_mensaje(payload: str) -> dict | None:
    """
    Recibe el payload del mensaje MQTT como string JSON.
    Retorna un diccionario con los campos del sensor,
    o None si el mensaje está malformado.

    Campos esperados: device_id, temperature_c, cpu_percent,
                      power_w, fan_rpm

    Pista: json.loads() dentro de un try/except.
    """
    # Tu código aquí
    pass


# ================================================================
# TODO 2 — Definir features y target
# ================================================================
def preparar_X_y(df: pd.DataFrame):
    """
    Separa el DataFrame en:
      - X : las columnas que el modelo usará como entrada
      - y : la columna que el modelo debe predecir (temperature_c)

    Reflexiona: ¿qué variables conocería el sistema ANTES
    de medir la temperatura? Esas son tus features.
    ¿Tiene sentido incluir device_id? ¿Por qué no?

    Retorna (X, y).
    """
    # Tu código aquí
    pass


# ================================================================
# TODO 3 — Entrenar el modelo
# ================================================================
def entrenar_modelo(X, y) -> tuple:
    """
    Entrena un LinearRegression igual que en la Clase 2.

    Pasos:
      1. Divide en train/test con train_test_split (test_size=0.2)
      2. Crea y entrena un LinearRegression
      3. Imprime R² en train y en test
      4. Calcula los errores de predicción sobre X_train:
            errores = y_train - modelo.predict(X_train)
         y guarda el umbral:
            umbral = errores.std() * 2
         (lecturas con error mayor a este umbral se considerarán anómalas)
      5. Imprime el umbral

    Retorna (modelo, umbral).
    """
    # Tu código aquí
    pass


# ================================================================
# TODO 4 — Guardar el modelo
# ================================================================
def guardar_modelo(modelo, umbral: float, features: list[str]):
    """
    Guarda en ARCHIVO_MODELO un diccionario con:
      {
        "modelo":   modelo,
        "umbral":   umbral,
        "features": features   ← las columnas de X, en orden
      }

    Usa joblib.dump().
    Imprime confirmación con la ruta guardada.

    En la Práctica 6B necesitarás cargar exactamente
    las mismas features en el mismo orden.
    """
    # Tu código aquí
    pass


# ================================================================
# Scaffolding — No modificar
# ================================================================

def on_message(client, userdata, msg):
    lectura = procesar_mensaje(msg.payload.decode())
    if lectura is None:
        return

    lectura["timestamp"] = datetime.now().isoformat()
    lecturas.append(lectura)
    n = len(lecturas)

    device = lectura.get("device_id", "?")
    temp   = lectura.get("temperature_c", "?")
    cpu    = lectura.get("cpu_percent", "?")
    print(f"[{n:4d}] {device} | temp={temp}°C  cpu={cpu}%", end="")

    if n < MINIMO_LECTURAS:
        print(f"  (faltan {MINIMO_LECTURAS - n} para entrenar)")
    else:
        print(f"  ← listo (Ctrl+C para entrenar)")


def entrenar_y_guardar():
    print(f"\n{'='*60}")
    print(f"Recolectadas {len(lecturas)} lecturas. Iniciando entrenamiento.")
    print(f"{'='*60}\n")

    df = pd.DataFrame(lecturas)
    df.to_csv(ARCHIVO_DATOS, index=False)
    print(f"Datos guardados: {ARCHIVO_DATOS}\n")

    print("Resumen por dispositivo:")
    print(df.groupby("device_id")[["temperature_c", "cpu_percent", "power_w", "fan_rpm"]].mean().round(1))

    # Graficar temperatura por dispositivo
    fig, ax = plt.subplots(figsize=(12, 4))
    for device_id, grupo in df.groupby("device_id"):
        ax.plot(grupo.index, grupo["temperature_c"], label=device_id, linewidth=0.8)
    ax.set_title("Temperatura durante recolección")
    ax.set_ylabel("Temperatura (°C)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("datos_normales.png", dpi=150)
    plt.show()

    X, y = preparar_X_y(df)
    if X is None:
        print("ERROR: preparar_X_y() retornó None. Implementa el TODO 2.")
        return

    resultado = entrenar_modelo(X, y)
    if resultado is None:
        print("ERROR: entrenar_modelo() retornó None. Implementa el TODO 3.")
        return

    modelo, umbral = resultado
    guardar_modelo(modelo, umbral, list(X.columns))
    print(f"\nListo. Usa {ARCHIVO_MODELO} en la Práctica 6B.")


def main():
    if len(lecturas) < MINIMO_LECTURAS:
        print(f"Solo hay {len(lecturas)} lecturas (mínimo {MINIMO_LECTURAS}).")
        return
    entrenar_y_guardar()


client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, 1883)
client.subscribe(TOPIC)

print(f"Escuchando en '{TOPIC}'...")
print(f"Necesitas {MINIMO_LECTURAS} lecturas (~{MINIMO_LECTURAS//6} min)")
print(f"Presiona Ctrl+C cuando quieras entrenar.\n")

try:
    client.loop_forever()
except KeyboardInterrupt:
    client.disconnect()
    main()
