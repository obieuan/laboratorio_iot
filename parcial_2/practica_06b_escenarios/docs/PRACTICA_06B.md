# Práctica 6B — Escenarios en Vivo

## Sistema IoT con Machine Learning — Parte 2

**Curso:** IoT Avanzado — EIUM — Universidad Modelo
**Prerequisito:** Práctica 6A completada (necesitas `modelo_normal.pkl`)

---

## Objetivo

Aplicar el modelo de regresión entrenado en la Práctica 6A a datos nuevos
que llegan en tiempo real desde los ESP32.

El modelo predice la temperatura esperada de cada lectura. Cuando la
temperatura real se aleja de la predicción, el sistema lanza una alerta.

---

## Cómo funciona la detección

En la Práctica 6A entrenaste el modelo con datos normales y calculaste
el **umbral**: el error máximo de predicción que se considera normal.

```
temp_predicha = modelo.predict([cpu, power, fan])
error         = temp_real - temp_predicha

si |error| > umbral → alerta
```

Si el comportamiento del sensor cambia de alguna forma que rompa la
relación que el modelo aprendió, el error de predicción será grande.

---

## Antes de empezar

Copia `modelo_normal.pkl` de la Práctica 6A a esta carpeta:

```bash
cp ../practica_06a_datos_normales/modelo_normal.pkl codigo/python/
```

Sube el firmware que te corresponde a tu ESP32. La configuración
(WiFi, IP del broker) es igual que en la Práctica 6A.

---

## Práctica paso a paso

### Paso 1 — Implementar los 4 TODOs en `detector.py`

**TODO 1 — `cargar_modelo(ruta)`**
Carga el `.pkl` con `joblib.load()`. Imprime las features y el umbral.
Retorna `(modelo, umbral, features)`.

**TODO 2 — `preparar_vector(lectura, features)`**
Convierte el dict del JSON en un DataFrame de una fila.
Importante: **no incluyas `temperature_c`** — eso es lo que el modelo predice.

**TODO 3 — `evaluar(modelo, vector, temp_real)`**
Predice la temperatura con `modelo.predict(vector)[0]` y calcula el error.
Retorna `(temp_predicha, error)`.

**TODO 4 — `mostrar_resultado(...)`**
Diseña el log en consola. Muestra temperatura real, predicha, error y
una alerta visual cuando corresponda.

---

### Paso 2 — Correr el sistema en vivo (10-15 min)

```bash
python detector.py
```

Observa el output mientras los 3 ESP32s publican. Toma nota:
- ¿Todos los dispositivos tienen errores similares?
- ¿Alguno genera alertas consistentemente?
- ¿El error crece con el tiempo o es constante desde el inicio?

---

### Paso 3 — Analizar los resultados

Al presionar Ctrl+C se genera `resultados.png` con temperatura real
vs. predicha por dispositivo.

Responde **antes de la discusión en clase**:

1. ¿Qué dispositivo(s) generaron más alertas?
2. ¿El error fue inmediato o fue creciendo? ¿Qué implica cada caso?
3. ¿En qué dirección fue el error — la real fue mayor o menor que la predicha?
   ¿Qué dice eso sobre lo que cambió?
4. ¿Con qué umbral tiene sentido tu sistema — demasiado sensible, justo, poco sensible?

---

### Paso 4 — Ajustar el umbral (experimental)

El umbral está guardado en el modelo pero puedes sobreescribirlo para experimentar:

```python
umbral = 3.0   # solo errores mayores a 3°C generan alerta
umbral = 1.0   # más sensible, más alertas
```

¿Cómo afecta al número de alertas? ¿Existe un valor que balancee
detección vs. falsos positivos?

---

## Entregables

- `resultados.png`
- Respuestas a las 4 preguntas del Paso 3
- Hipótesis: ¿qué crees que estaba pasando en cada dispositivo?

---

## Discusión en clase

Cada equipo expone su hipótesis. Luego se revela qué simulaba cada firmware.

- ¿Coincidió tu hipótesis?
- ¿Qué tipo de cambio fue más fácil/difícil de detectar? ¿Por qué?
- La regresión predice temperatura a partir de otras variables — ¿qué tipo
  de falla **no** podría detectar este modelo?
- ¿Cómo mejorarías el sistema?
