# Guía de Práctica: Machine Learning para IoT

## Regresión y Clasificación con scikit-learn

**Curso:** IoT Avanzado — EIUM — Universidad Modelo  
**Duración:** 2 horas (más teoría, práctica guiada al final)  
**Prerequisito:** Haber completado la clase 1 (Datos IoT → Análisis)

---

## Objetivo

Entender los conceptos fundamentales de Machine Learning supervisado (regresión y clasificación) y aplicarlos al dataset de cuarto de servidores usando scikit-learn.

---

## Requisitos

```bash
pip install pandas matplotlib scikit-learn
```

### Archivos

- `server_room_telemetry.csv` — mismo dataset de la clase anterior
- `practica2_ml_sklearn.py` — script completo de referencia

---

## Conceptos clave antes de empezar

### Programación tradicional vs ML

| | Programación tradicional | Machine Learning |
|---|---|---|
| **Entrada** | Reglas + datos | Datos + resultados esperados |
| **Salida** | Resultado | Reglas aprendidas |
| **Ejemplo** | `if temp > 30: alerta` | El modelo aprende qué es "anormal" |

### Regresión vs Clasificación

| | Regresión | Clasificación |
|---|---|---|
| **Predice** | Un número continuo | Una etiqueta / categoría |
| **Pregunta** | ¿Cuánto? | ¿Qué tipo? |
| **Ejemplo IoT** | ¿Cuál será la temperatura en 10 min? | ¿Este registro es normal o anomalía? |
| **Algoritmo** | `LinearRegression` | `DecisionTreeClassifier` |

### Train/Test Split

Siempre dividimos los datos en dos grupos antes de entrenar:

- **Entrenamiento (80%):** El modelo aprende de estos datos
- **Prueba (20%):** Evaluamos si el modelo realmente aprendió

Es como estudiar con el libro (train) y después hacer el examen (test). Si evalúas con las mismas preguntas que estudiaste, no sabes si realmente aprendiste.

---

## Práctica paso a paso (30 min)

### Paso 1 — Preparar datos

```python
import pandas as pd
from sklearn.model_selection import train_test_split

df = pd.read_csv("server_room_telemetry.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["hour"] = df["timestamp"].dt.hour + df["timestamp"].dt.minute / 60

# Eliminar filas con datos faltantes
df_clean = df.dropna(subset=["temperature_c"]).copy()
print(f"Registros limpios: {len(df_clean)}")
```

**¿Por qué crear la columna `hour`?** Porque la temperatura de un servidor sigue patrones diurnos — más alta en horario laboral. El modelo necesita esta información como número, no como texto de timestamp.

---

### Paso 2 — Regresión Lineal

```python
from sklearn.linear_model import LinearRegression

# Features y target
X = df_clean[["cpu_percent", "power_w", "hour"]]
y = df_clean["temperature_c"]

# Dividir datos
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Entrenar
modelo = LinearRegression()
modelo.fit(X_train, y_train)

# Evaluar
print(f"R² = {modelo.score(X_test, y_test):.3f}")
```

**¿Qué significa R²?** Es un número entre 0 y 1 que indica qué tan bien predice el modelo. R²=0.85 significa que el modelo explica el 85% de la variación en la temperatura.

**Preguntas:**
- ¿Qué R² obtuviste?
- Prueba quitar una feature (e.g., solo `cpu_percent` y `hour`). ¿Cambia el R²?

---

### Paso 3 — Clasificación con Árbol de Decisión

```python
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

# Crear etiquetas
df_clean["label"] = "normal"
df_clean.loc[df_clean["temperature_c"] > 30, "label"] = "temp_alta"
df_clean.loc[df_clean["temperature_c"] < 10, "label"] = "temp_imposible"
df_clean.loc[df_clean["power_w"] > 350, "label"] = "power_alto"

# Features y target
X = df_clean[["temperature_c", "cpu_percent", "power_w", "fan_rpm"]]
y = df_clean["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Entrenar
arbol = DecisionTreeClassifier(max_depth=4, random_state=42)
arbol.fit(X_train, y_train)

# Evaluar
pred = arbol.predict(X_test)
print(f"Accuracy = {accuracy_score(y_test, pred):.3f}")
```

**¿Qué es `max_depth=4`?** Limita cuántas "preguntas" puede hacer el árbol. Un árbol muy profundo memoriza los datos (overfitting). Uno muy corto no aprende lo suficiente (underfitting).

**Preguntas:**
- ¿Qué accuracy obtuviste?
- Prueba con `max_depth=2` y `max_depth=10`. ¿Qué pasa?

---

### Paso 4 — Comparar y reflexionar

Responde estas preguntas:

1. La regresión predice un **número** y la clasificación una **etiqueta**. ¿Para qué usarías cada una en tu proyecto IoT?
2. ¿Qué pasa si el modelo tiene R²=0.99 en entrenamiento pero R²=0.50 en test? (pista: overfitting)
3. Las etiquetas de clasificación las creamos con reglas manuales. ¿Eso no es lo mismo que la clase anterior? ¿Cuál es la ventaja del modelo?

**Respuesta esperada para la 3:** La ventaja es que el modelo puede generalizar a datos nuevos usando combinaciones de features que no programamos explícitamente. Además, una vez entrenado, puede clasificar en tiempo real sin ejecutar todas las reglas manualmente.

---

## Referencia rápida de scikit-learn

| Función | Descripción |
|---------|------------|
| `train_test_split(X, y, test_size=0.2)` | Divide datos en train/test |
| `LinearRegression()` | Crea modelo de regresión |
| `DecisionTreeClassifier(max_depth=4)` | Crea árbol de decisión |
| `modelo.fit(X_train, y_train)` | Entrena el modelo |
| `modelo.predict(X_test)` | Genera predicciones |
| `modelo.score(X_test, y_test)` | R² para regresión |
| `accuracy_score(y_test, pred)` | % aciertos para clasificación |
