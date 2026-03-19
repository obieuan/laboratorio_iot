# Práctica 6A — Datos en vivo con MQTT

## Sistema IoT con Machine Learning — Parte 1: Recolección y Entrenamiento

**Curso:** IoT Avanzado — EIUM — Universidad Modelo
**Prerequisito:** Clase 2 (ML con scikit-learn), Práctica 5A (MQTT)

---

## Objetivo

Recolectar datos de los sensores IoT en tiempo real via MQTT y entrenar
un modelo de regresión lineal que aprenda el comportamiento del sistema.

El modelo que generes hoy se usará en la Práctica 6B — guárdalo bien.

---

## Conexión con la Clase 2

En la Clase 2 entrenaste un `LinearRegression` para predecir temperatura
a partir de datos de un CSV. Aquí harás exactamente lo mismo, pero los
datos vienen de sensores reales en tiempo real via MQTT.

```python
# Clase 2 — datos de un archivo
df = pd.read_csv("server_room_telemetry.csv")

# Práctica 6A — datos del sensor en vivo
# (los recibes por MQTT y los acumulas tú mismo)
```

El modelo, el entrenamiento y la evaluación son idénticos.

---

## Materiales

- 3 ESP32 con el firmware de la Práctica 6A
- Broker MQTT corriendo en una laptop (ver instalación abajo)
- Python con las dependencias instaladas

---

## Preparación

### 1. Instalar broker MQTT

```bash
# Windows
winget install mosquitto

# Iniciar
mosquitto -v
```

### 2. Instalar dependencias Python

```bash
pip install -r requirements.txt
```

### 3. Configurar el ESP32

Abre `esp32_normal.ino` y edita antes de compilar:

```cpp
const char* DEVICE_ID   = "ESP32-A";      // Equipo 1=A, 2=B, 3=C
const char* WIFI_SSID   = "TU_RED_WIFI";
const char* WIFI_PASS   = "TU_PASSWORD";
const char* MQTT_BROKER = "192.168.X.X";  // IP de la laptop con el broker
```

---

## Práctica paso a paso

### Paso 1 — Verificar la comunicación (5 min)

Con el broker corriendo y el ESP32 encendido, verifica que llegan datos:

```bash
mosquitto_sub -h localhost -t "iot/lab/sensores"
```

Deberías ver un JSON cada 500ms por cada ESP32 conectado:
```json
{"device_id":"ESP32-A","temperature_c":22.4,"cpu_percent":35,"power_w":227,"fan_rpm":1103}
```

---

### Paso 2 — Recolectar datos (10-15 min)

Ejecuta el colector y espera a tener suficientes lecturas:

```bash
python colector.py
```

Cuando el script indique que está listo, presiona **Ctrl+C** para entrenar.

---

### Paso 3 — Implementar los 4 TODOs en `colector.py`

**TODO 1 — `procesar_mensaje(payload)`**
Parsea el JSON que llega por MQTT. Si el mensaje es inválido, retorna `None`.

**TODO 2 — `preparar_X_y(df)`**
Separa el DataFrame en features (X) y target (y = `temperature_c`).
Pregunta clave: ¿qué variables conocería el sistema **antes** de medir
la temperatura? Esas son tus features.

**TODO 3 — `entrenar_modelo(X, y)`**
Usa `train_test_split` y `LinearRegression` igual que en la Clase 2.
Además, calcula el **umbral de error normal**:

```python
errores = y_train - modelo.predict(X_train)
umbral  = errores.std() * 2
```

Este umbral define qué tan grande puede ser el error de predicción
antes de considerarlo anómalo.

**TODO 4 — `guardar_modelo(modelo, umbral, features)`**
Guarda los tres valores en un archivo `.pkl` con `joblib.dump()`.
En la Práctica 6B necesitarás cargar exactamente las mismas features.

---

### Paso 4 — Explorar los datos recolectados

El script genera `datos_normales.csv` y una gráfica automáticamente.

Responde:
1. ¿Qué R² obtuviste? ¿Es similar al de la Clase 2?
2. ¿Qué features elegiste? ¿Por qué no incluiste `device_id`?
3. ¿Qué significa el umbral que calculaste?
4. ¿Por qué recolectamos datos de los 3 dispositivos y no solo de uno?

---

## Entregables

- `datos_normales.csv`
- `modelo_normal.pkl` ← **necesario para la Práctica 6B**
- `datos_normales.png`
- Respuestas a las preguntas del Paso 4

---

## Siguiente

En la **Práctica 6B** cada equipo sube un firmware diferente a su ESP32
y corre el modelo que entrenaron hoy sobre los datos en vivo.
