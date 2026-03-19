"""
=============================================================
Práctica 6B — Sistema de monitoreo en tiempo real
EIUM — Universidad Modelo

Carga el modelo entrenado en la Práctica 6A y evalúa
cada lectura que llega de los ESP32 por MQTT.

Hay 4 secciones marcadas con TODO — esas son las que implementas.
=============================================================
"""

import json
import joblib
import pandas as pd
import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt
from datetime import datetime
from collections import defaultdict

# ---- CONFIGURACIÓN ----
BROKER         = "localhost"
TOPIC          = "iot/lab/sensores"
ARCHIVO_MODELO = "modelo_normal.pkl"
# -----------------------

modelo   = None
umbral   = None
features = None
historial = defaultdict(list)   # device_id → lista de registros


# ================================================================
# TODO 1 — Cargar el modelo entrenado en la Práctica 6A
# ================================================================
def cargar_modelo(ruta: str) -> tuple:
    """
    Carga el archivo .pkl guardado en la Práctica 6A.
    Usa joblib.load().

    El archivo contiene un diccionario con tres claves:
      "modelo"   → el LinearRegression entrenado
      "umbral"   → el error máximo considerado normal
      "features" → lista de columnas que espera el modelo

    Imprime las features cargadas y el umbral.
    Retorna (modelo, umbral, features).
    """
    # Tu código aquí
    pass


# ================================================================
# TODO 2 — Preparar el vector de entrada
# ================================================================
def preparar_vector(lectura: dict, features: list) -> pd.DataFrame:
    """
    Convierte la lectura (dict del JSON) en un DataFrame
    de una sola fila con las columnas que el modelo espera.

    Importante: NO incluyas temperature_c — eso es lo que
    el modelo va a predecir. Solo las features de entrada.

    Retorna pd.DataFrame([lectura])[features]
    """
    # Tu código aquí
    pass


# ================================================================
# TODO 3 — Predecir y calcular el error
# ================================================================
def evaluar(modelo, vector: pd.DataFrame, temp_real: float) -> tuple:
    """
    Usa el modelo para predecir la temperatura esperada
    dado el vector de features.

    Calcula el error:
        error = temp_real - temp_predicha

    Retorna (temp_predicha, error).

    Pista: modelo.predict(vector) retorna un array — extrae [0].
    """
    # Tu código aquí
    pass


# ================================================================
# TODO 4 — Mostrar el resultado en consola
# ================================================================
def mostrar_resultado(device_id: str, temp_real: float,
                      temp_predicha: float, error: float,
                      es_alerta: bool):
    """
    Imprime una línea de log por cada lectura.

    Incluye al menos:
      - Hora (HH:MM:SS)
      - device_id
      - Temperatura real y predicha
      - Error de predicción
      - Indicador visual si es_alerta es True

    Ejemplo:
      [14:32:01] ESP32-A | real=23.1°C  pred=22.8°C  err= 0.3°C
      [14:32:02] ESP32-B | real=34.5°C  pred=22.9°C  err=11.6°C  *** ALERTA ***
    """
    # Tu código aquí
    pass


# ================================================================
# Scaffolding — No modificar
# ================================================================

def on_message(client, userdata, msg):
    try:
        lectura = json.loads(msg.payload.decode())
    except json.JSONDecodeError:
        return

    device_id = lectura.get("device_id", "?")
    temp_real = lectura.get("temperature_c")
    if temp_real is None:
        return

    try:
        vector              = preparar_vector(lectura, features)
        temp_predicha, error = evaluar(modelo, vector, temp_real)
        es_alerta           = abs(error) > umbral

        mostrar_resultado(device_id, temp_real, temp_predicha, error, es_alerta)

        historial[device_id].append({
            "timestamp":    datetime.now(),
            "temp_real":    temp_real,
            "temp_predicha": temp_predicha,
            "error":        error,
            "alerta":       es_alerta,
        })

    except Exception as e:
        print(f"Error procesando {device_id}: {e}")


def graficar_resumen():
    if not historial:
        print("Sin datos para graficar.")
        return

    n = len(historial)
    fig, axes = plt.subplots(n, 1, figsize=(12, 4 * n), sharex=False)
    if n == 1:
        axes = [axes]

    for ax, (device_id, datos) in zip(axes, sorted(historial.items())):
        tiempos  = [d["timestamp"] for d in datos]
        reales   = [d["temp_real"] for d in datos]
        predic   = [d["temp_predicha"] for d in datos]
        errores  = [d["error"] for d in datos]
        alertas  = [d["alerta"] for d in datos]

        ax.plot(tiempos, reales,  label="Temp real",     color="#EF4444", linewidth=1)
        ax.plot(tiempos, predic,  label="Temp predicha", color="#6366F1",
                linewidth=1, linestyle="--")

        # Marcar alertas
        for t, r, a in zip(tiempos, reales, alertas):
            if a:
                ax.scatter(t, r, color="red", s=15, zorder=5)

        tasa = sum(alertas) / len(alertas) * 100
        ax.set_title(f"{device_id} — {tasa:.1f}% alertas  |  "
                     f"error promedio: {sum(abs(e) for e in errores)/len(errores):.2f}°C")
        ax.set_ylabel("Temperatura (°C)")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right", fontsize=7)

    plt.suptitle("Temperatura real vs. predicha por dispositivo", fontsize=13)
    plt.tight_layout()
    plt.savefig("resultados.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("Gráfica guardada: resultados.png")

    print("\n" + "="*50)
    print("RESUMEN")
    print("="*50)
    for device_id, datos in sorted(historial.items()):
        errores = [abs(d["error"]) for d in datos]
        alertas = [d["alerta"] for d in datos]
        print(f"\n{device_id}:")
        print(f"  Lecturas:         {len(datos)}")
        print(f"  Error promedio:   {sum(errores)/len(errores):.2f}°C")
        print(f"  Error máximo:     {max(errores):.2f}°C")
        print(f"  Alertas:          {sum(alertas)} ({sum(alertas)/len(alertas)*100:.1f}%)")


# ---- Main ----
modelo, umbral, features = cargar_modelo(ARCHIVO_MODELO)
if modelo is None:
    print("ERROR: No se pudo cargar el modelo. Implementa el TODO 1.")
    exit(1)

client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, 1883)
client.subscribe(TOPIC)

print(f"Modelo cargado | features: {features} | umbral: {umbral:.2f}°C")
print(f"Escuchando en '{TOPIC}'... Ctrl+C para ver resumen.\n")

try:
    client.loop_forever()
except KeyboardInterrupt:
    client.disconnect()
    graficar_resumen()
