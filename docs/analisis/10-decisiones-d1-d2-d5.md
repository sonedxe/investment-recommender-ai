# 10 · Detalle de las decisiones D1, D2 y D5

Desarrolla tres decisiones de [06-decisiones-pendientes.md](06-decisiones-pendientes.md): la validación con el docente del gen difuso (D1), la corrección de portafolios degenerados (D2) y la escala de λ_base (D5).

---

## D1 · Validar con el docente el gen difuso del cromosoma

### Por qué hace falta

La propuesta ([04](04-propuesta-difusa-cromosoma.md)) es una **interpretación** de una frase del feedback. Si el docente esperaba otra cosa, conviene saberlo antes de implementar el algoritmo genético y no en la exposición.

### Qué mostrarle (máximo 2 minutos)

1. **Diagrama del cromosoma:**

   ```
   P = [ w1, w2, w3, w4, w5 | c ]
         pesos (Σ = 1)        gen difuso: nivel de absorción asumido
   ```

2. **La idea en una frase:** "La capacidad de absorción se calcula con un Mamdani sin desfuzzificar. El conjunto de salida queda vivo y el algoritmo genético elige un punto `c` de ese conjunto; el fitness premia que `c` sea compatible con el usuario."
3. **El fitness, señalando dónde está cada conjunto:**

   ```
   Fitness = Σ wᵢ·μ'ᵢ − λ_ef·σ'  − φ·max(0, σ' − σ_max(c))²  + κ·μ_CA(c)
                        └ horizonte            └──── absorción (en el cromosoma) ────┘
                          (en el fitness)
   ```

4. **Un gráfico** de `μ_CA` con `c` y el centroide marcados (el `AbsorptionChart` del design system sirve como boceto).

### Preguntas para el docente

| # | Pregunta | Por qué importa |
|---|---|---|
| P1 | ¿Es válido que el gen difuso sea un punto `c` del universo de un conjunto difuso de salida, evaluado con `μ_CA(c)` en el fitness? | Confirma la interpretación central |
| P2 | ¿Prefiere que el conjunto en el cromosoma sea la absorción o el horizonte? | Ambos son posibles; la absorción encaja mejor porque ya produce un conjunto con varias reglas |
| P3 | ¿Acepta Sugeno para el horizonte y Mamdani para la absorción? | Demuestra ambos tipos de inferencia vistos en clase |
| P4 | Las reglas de contexto ajustan μ y σ, que entran al fitness. ¿Eso cuenta como influencia "directa", o espera un término propio en la fórmula? | Hoy ya existe `C(P) = Σ wᵢ·cᵢ` como término; se puede mostrar separado |

### Respuestas posibles y qué hacer

| Respuesta | Acción | Impacto en el código |
|---|---|---|
| Acepta la propuesta | Implementar tal cual | Ninguno |
| Prefiere el horizonte en el cromosoma | Intercambiar: horizonte → gen `h` evaluado con `μ_H(h)`; absorción → `σ_max` nítido en el fitness | Bajo: el AG recibe la función de pertenencia como parámetro |
| Espera genes como etiquetas lingüísticas (Bajo/Medio/Alto) | Gen entero `{0,1,2}` por etiqueta, desfuzzificado al evaluar | Medio: cambia la reparación y la mutación del gen extra |
| Espera que los propios pesos sean números difusos | Pesos como triangulares `(a, b, c)` y fitness sobre su centroide | Alto: replantear el cromosoma; consultar el alcance antes de aceptarlo |
| Pide un término de contexto separado | Mostrar `C(P)` como término propio en el fitness y en el desglose | Ninguno: ya está en el contrato |

### Si no hay respuesta a tiempo

Se implementa la propuesta. El diseño ya aísla el AG de los módulos difusos, así que cualquier cambio posterior queda acotado.

---

## D2 · Corrección de los portafolios degenerados

### El problema (resumen)

Con los datos del Anexo A, `E − λσ` lleva a soluciones extremas: 100 % acciones (λ = 0.2) o ~90 % depósito (λ ≥ 1); los fondos de deuda y mixtos quedan casi siempre en 0 %. Detalle en [05 §1](05-hallazgos-tecnicos.md#1--portafolios-degenerados-verificado).

### Comparación de correcciones (verificada)

Muestreo de 120 000 portafolios, ρ = 0.3 entre categorías y el depósito sin correlación. Pesos en %.

| λ | Corrección | Acc. | Mixt. | Deuda | BTP | Dep. | E | σ |
|---|---|---|---|---|---|---|---|---|
| 0.2 | Sin corrección | 99 | 0 | 0 | 1 | 0 | 12.1 % | 18.8 % |
| | Tope 50 % | 49 | 1 | 0 | 49 | 0 | 9.3 % | 10.0 % |
| | **Tope 40 %** | **40** | **19** | **0** | **40** | **1** | **8.7 %** | **8.8 %** |
| | Término de diversificación (δ = 0.02) | 74 | 4 | 0 | 22 | 0 | 10.7 % | 14.4 % |
| 0.5 | Sin corrección | 13 | 0 | 0 | 87 | 0 | 7.2 % | 4.5 % |
| | Tope 50 % | 10 | 2 | 0 | 50 | 38 | 6.3 % | 3.1 % |
| | **Tope 40 %** | **15** | **5** | **1** | **40** | **39** | **6.5 %** | **3.8 %** |
| | Término de diversificación | 14 | 9 | 0 | 50 | 28 | 6.7 % | 3.9 % |
| 1.0 | Sin corrección | 1 | 1 | 0 | 11 | 87 | 4.8 % | 0.7 % |
| | Tope 50 % | 1 | 1 | 0 | 48 | 49 | 5.6 % | 1.8 % |
| | **Tope 40 %** | **2** | **4** | **16** | **39** | **40** | **5.2 %** | **1.9 %** |
| | Término de diversificación | 2 | 3 | 0 | 34 | 61 | 5.4 % | 1.5 % |
| 2.0 | Sin corrección | 0 | 0 | 0 | 4 | 95 | 4.6 % | 0.5 % |
| | Tope 50 % | 0 | 1 | 12 | 38 | 50 | 5.0 % | 1.5 % |
| | **Tope 40 %** | **0** | **1** | **22** | **37** | **40** | **4.8 %** | **1.6 %** |
| | Término de diversificación | 0 | 0 | 4 | 14 | 82 | 4.7 % | 0.7 % |

Combinar el tope de 40 % con el término de diversificación (δ = 0.01) dio los mismos resultados que el tope solo: el término no aporta cuando ya hay tope.

### Lectura

- **El término de diversificación solo no alcanza:** con λ alto sigue dejando ~80 % en depósito.
- **El tope de 50 % mejora, pero deja portafolios de dos activos** (acciones + BTP, BTP + depósito).
- **El tope de 40 % produce un gradiente razonable** entre perfiles:
  - agresivo (λ 0.2): 40 / 19 / 0 / 40 / 1;
  - moderado (λ 0.5): 15 / 5 / 1 / 40 / 39;
  - conservador (λ 1–2): casi nada en acciones; deuda, BTP y depósito.
- Los fondos mixtos siguen con poco peso: están dominados en retorno/riesgo. Es un resultado honesto de los datos y conviene comentarlo en la explicación, no forzarlo.

### Decisión recomendada

**Tope duro `wᵢ ≤ 0.40`**, aplicado en la reparación del cromosoma (después de cruce y mutación: recortar al tope y redistribuir el excedente proporcionalmente entre las categorías por debajo del tope).

- **Justificación para el informe:** es un límite de concentración, una práctica habitual en la regulación de carteras (los fondos y las AFP tienen límites por tipo de instrumento). Evita que el portafolio dependa de un solo activo.
- **Parámetro configurable** (`max_weight` en el Anexo C) y verificado en las pruebas de ablación (tope 0.4 frente a 0.5 frente a sin tope).
- **Advertencias:** los valores salen de un muestreo, no del AG; el AG puede encontrar soluciones algo mejores. Con los datos reales de [09](09-fuentes-de-datos.md) hay que repetir la comparación.

---

## D5 · Escala de λ_base

### El problema

El informe no define cómo la IA generativa convierte "no me gusta arriesgar" en un número. Si el LLM devuelve un número libre, el mismo texto puede dar λ = 1.8 una vez y 2.3 la siguiente: no es reproducible ni auditable.

### Decisión recomendada

El LLM **clasifica** en una etiqueta cerrada; el **código** la convierte en número.

| Etiqueta (enum) | λ_base | Lenguaje típico del usuario | Portafolio resultante (con tope 40 %, H = mediano) |
|---|---|---|---|
| `muy_agresivo` | 0.2 | "quiero la máxima ganancia, aguanto pérdidas" | Acciones + BTP + mixtos |
| `agresivo` | 0.5 | "acepto riesgo si gano más" | Mezcla con base en BTP y depósito, algo de acciones |
| `moderado` | 1.0 | "algo de riesgo, pero no mucho" | BTP + depósito + deuda |
| `conservador` | 2.0 | "no me gusta arriesgar" | Depósito + BTP + deuda |
| `muy_conservador` | 3.0 | "no quiero perder nada" | Igual que conservador, más concentrado en depósito |

### Reglas

- El LLM devuelve la etiqueta, la **frase del usuario que la justifica** (evidencia) y si está seguro.
- Sin evidencia clara, o con señales contradictorias ("máxima ganancia pero no puedo perder nada"), no se elige etiqueta: se genera una **pregunta de aclaración**.
- La tabla etiqueta → λ vive en `data/parameters/` (configurable) y se muestra en el detalle técnico.
- λ_ef = λ_base · m_H queda entre 0.14 (muy agresivo, horizonte largo) y 4.5 (muy conservador, horizonte corto).

### Por qué estos valores

- 0.2, 0.5, 1.0 y 2.0 son los del notebook y el informe: se mantiene la continuidad.
- Con el tope de 40 %, cada escalón produce un portafolio visiblemente distinto (tabla D2): los perfiles se distinguen en la demo.
- 3.0 agrega un extremo conservador sin cambiar el resto.
