# 02 · Fases y tareas

Cada tarea tiene un ID estable para referenciarla en commits y PRs (p. ej. `feat(fuzzy): mamdani engine [T1.3]`).

## F0 · Decisiones, contratos y preparación

| ID | Tarea | Criterio de aceptación | Depende de |
|---|---|---|---|
| T0.1 | Cerrar decisiones D1–D5 ([análisis 06](../analisis/06-decisiones-pendientes.md)) | Cada decisión registrada con su justificación | — |
| T0.2 | Consultar al docente la interpretación del cromosoma (D1) | Respuesta registrada; si no hay respuesta, se aplica el valor por defecto | — |
| T0.3 | Definir tipos compartidos (`ai/shared/types.py`) y esquemas Pydantic | Contratos de [01](01-arquitectura.md#contratos-entre-módulos) codificados; revisados por los 5 streams | T0.1 |
| T0.4 | Cargar parámetros en `data/parameters/` (Anexo A, Anexo C, conjuntos difusos) | JSON cargable y validado por un test | — |
| T0.5 | Preparar entorno: `numpy` en `requirements.txt`, estructura de carpetas, limpiar docstrings inconsistentes (SA, VaR, "universo de inversión") | `pytest` en verde; docstrings alineados con el informe | — |
| T0.6 | Conseguir series históricas (D3, ver [análisis 09](../analisis/09-fuentes-de-datos.md)): `scripts/fetch_market_data.py` para EPU + PEN=X; descarga manual del BCRP (BTP, depósito); SMV/AAFMP si se consigue | CSV en `data/market/` + `SOURCES.md` con fuente, fecha y transformación; categorías sin datos marcadas como "Anexo A" | T0.1 |

## F1 · Lógica difusa — `ai/uncertainty/fuzzy`

| ID | Tarea | Criterio de aceptación | Depende de |
|---|---|---|---|
| T1.1 | Funciones `tri(a,b,c)` y `trap(a,b,c,d)` vectorizadas | Casos borde (hombros, picos, fuera de soporte) cubiertos | T0.5 |
| T1.2 | Motor Sugeno de orden cero | Promedio ponderado; activación cero en todas las reglas manejada | T1.1 |
| T1.3 | Motor Mamdani: implicación min, agregación max, centroide numérico | **Ejercicio de la propina** (servicio 3, comida 8) → 15.9 % ± 0.1 | T1.1 |
| T1.4 | Horizonte (RH1–RH3) → `m_H`, `λ_ef`; acepta años o etiqueta | H = 2.5 → m_H ≈ 1.30; con λ_base = 2 → λ_ef ≈ 2.6 | T1.2 |
| T1.5 | Absorción (RA1–RA6) en Mamdani → `μ_CA` (malla) + centroide | r se recorta a [0, 1] y E a [0, 12]; si falta ahorro o cobertura se usa "Media" y se registra el supuesto | T1.3 |

## F2 · Reglas de contexto — `ai/context`

| ID | Tarea | Criterio de aceptación | Depende de |
|---|---|---|---|
| T2.1 | Motor de reglas RC1–RC7 (condición → efecto) con trazas | Cada regla activada queda listada con su efecto numérico | T0.4 |
| T2.2 | Ajuste `μ'`, `σ'`, `Σ'` preservando ρ y aplicando el tope `c_max` | Reproduce la tabla 4.6.4 de la v1.1 (panorama adverso) | T2.1 |
| T2.3 | Interruptor: contexto desactivado → `c = 0`, `σ' = σ` | Test de identidad | T2.2 |

## F3 · Algoritmo genético extendido — `ai/heuristic`

| ID | Tarea | Criterio de aceptación | Depende de |
|---|---|---|---|
| T3.1 | Cromosoma `[w1..w5 \| c]`: inicialización (Dirichlet + uniforme) y reparación (no negatividad, Σ = 1, tope D2, `c ∈ [0,1]`) | Propiedades verificadas en 10 000 individuos aleatorios | T0.3 |
| T3.2 | Fitness ampliado con desglose e interruptores (difuso, contexto) | Con ambos interruptores apagados coincide con `E − λσ` | T3.1 |
| T3.3 | Operadores: torneo, cruce aritmético (`c` incluido), mutación gaussiana, elitismo | Hijos siempre válidos tras la reparación | T3.1 |
| T3.4 | Bucle con término por convergencia (sin mejora en N generaciones) o máximo de generaciones; historial; semilla | Misma semilla → mismo resultado; mejor fitness no decreciente | T3.2, T3.3 |
| T3.5 | Test de regresión contra portafolios degenerados | Ningún peso supera el tope; perfiles distintos producen portafolios distintos | T3.4 |
| T3.6 | (Opcional) Cruce de un punto + renormalización, para comparar con lo visto en clase | Disponible como opción configurable | T3.3 |

## F4 · Módulo bayesiano y datos — `ai/uncertainty/bayesian`

| ID | Tarea | Criterio de aceptación | Depende de |
|---|---|---|---|
| T4.1 | Estimación de μ, σ, ρ desde series (retornos anualizados) | Matriz de covarianza simétrica y semidefinida positiva | T0.6 |
| T4.2 | Actualización normal conjugada con prior del Anexo A | Casos analíticos conocidos; con varianza de dato infinita, el posterior es igual al prior | T4.1 |
| T4.3 | Indicador `s_tend = clip((r_12m − μ)/σ, −1, 1)`; 0 si no hay datos | Tests de recorte y de ausencia de datos | T4.1 |
| T4.4 | Precálculo y caché de las estimaciones | `/api/market/estimates` responde sin recalcular | T4.1–T4.3 |

## F5 · Orquestación y API — `backend/app`

| ID | Tarea | Criterio de aceptación | Depende de |
|---|---|---|---|
| T5.1 | Caso de uso `recommend_portfolio` (etapas 3–7) | Devuelve el contrato completo, incluidas las trazas | F1–F4 |
| T5.2 | Endpoints `/api/interpret`, `/api/recommend`, `/api/context/defaults`, `/api/market/estimates` | Esquemas validados; errores 422 claros | T5.1 |
| T5.3 | Tests de integración en modo offline | Texto → recomendación completa sin red | T5.2, T6.1 |

## F6 · IA generativa — `ai/generative`

| ID | Tarea | Criterio de aceptación | Depende de |
|---|---|---|---|
| T6.1 | Puerto `LanguageModel` + adaptador compatible con OpenAI + adaptador offline | Se cambia de uno a otro solo por configuración (`.env`) | T0.3 |
| T6.2 | **(F6a)** Interpretación: prompt, salida JSON validada contra esquema, `perfil_riesgo` como enum | JSON inválido → reintento acotado y luego error controlado | T6.1 |
| T6.3 | **(F6a)** Loop de clarificación: campo crítico faltante → pregunta específica; nunca supone en silencio | Ver golden set (T6.5) | T6.2 |
| T6.4 | **(F6b)** Explicación con las reglas de la sección 6 de la v1.1; recibe solo cifras calculadas | Validación posterior: toda cifra del texto existe en el resultado; aviso educativo siempre presente | T5.1 |
| T6.5 | Golden set de 15–20 textos (completos, ambiguos, contradictorios) con salida esperada | ≥ 90 % de extracciones correctas; 100 % de los ambiguos generan pregunta | T6.3 |

## F7 · Interfaz gráfica — `frontend`

> **Reemplazada** por las tareas T7.0–T7.8 de [06-frontend.md](06-frontend.md#5-tareas-reemplazan-f7-de-02), basadas en el design system. La tabla siguiente queda como referencia funcional.

| ID | Tarea | Criterio de aceptación | Depende de |
|---|---|---|---|
| T7.1 | **(mínima)** Chat: texto libre + preguntas de aclaración | Flujo de aclaración completo en la UI | T5.2 |
| T7.2 | **(mínima)** Resultado: gráfico del portafolio con montos en S/ + explicación | Montos suman el total invertido | T5.2 |
| T7.3 | Gráfico de convergencia por generación | Usa `historial` del AG | T7.2 |
| T7.4 | Panel de contexto: selector Adverso / Neutral / Favorable por factor; recalcula | Neutral al inicio; el cambio se refleja en el resultado | T7.2 |
| T7.5 | Detalle técnico colapsable: μ, σ, λ_base, λ_ef, pertenencias, gráficos de las funciones de pertenencia, `μ_CA` con `c` y centroide marcados, reglas activadas, desglose del fitness | Todos los campos del contrato visibles | T7.2 |
| T7.6 | Aviso permanente de herramienta educativa | Visible en todas las vistas | — |

## F8 · Experimentos — `experiments/`

| ID | Tarea | Criterio de aceptación | Depende de |
|---|---|---|---|
| T8.1 | Ablación: base / solo difuso / solo contexto / completo × 3 perfiles × 10 semillas | CSV + figuras; media ± desviación estándar | T3.4 |
| T8.2 | Escenarios de contexto (adverso, neutral, favorable) | Muestra el desplazamiento de peso esperado | T8.1 |
| T8.3 | Calibración de κ, φ y tope | Valores elegidos justificados con datos | T8.1 |
| T8.4 | Comparación `c` evolucionado frente al centroide de `μ_CA` | Tabla para el informe | T8.1 |
| T8.5 | (Opcional) Cruce aritmético frente a cruce de un punto | Convergencia comparada | T3.6 |

## F9 · Entregables

Ver [04-entregables.md](04-entregables.md).

| ID | Tarea | Depende de |
|---|---|---|
| T9.1 | Manual de instalación | F5, F7 |
| T9.2 | Manual de usuario (con capturas) | F7 |
| T9.3 | Informe técnico final (v2.0) | F8 |
| T9.4 | Corregir y adjuntar el notebook | — |
| T9.5 | Guion de la demo y ensayo de la exposición | Todo |
