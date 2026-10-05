# 04 · Propuesta: un conjunto difuso en el fitness y otro en el cromosoma

> Estado: **propuesta**, pendiente de confirmación por el equipo y, si es posible, por el docente (decisión D1 en [06](06-decisiones-pendientes.md)).

## Asignación

| Concepto | Ubicación | FIS | Salida |
|---|---|---|---|
| **Horizonte temporal** | **Evaluación (fitness)** | Sugeno-0 (se mantiene la v1.1) | `λ_ef = λ_base · m_H` (valor nítido) |
| **Capacidad de absorción** | **Cromosoma** | **Mamdani sin desfuzzificar** | Conjunto difuso agregado `μ_CA(x)`, x ∈ [0, 1] |

## Cromosoma extendido

```
P = [ w1, w2, w3, w4, w5 | c ]
      └─ pesos (Σ = 1) ─┘  └─ gen difuso: nivel de absorción asumido, c ∈ [0, 1]
```

- El sistema Mamdani de absorción (reglas RA1–RA6) produce el conjunto agregado `μ_CA` (pasos 1–4 del FIS), **sin el paso 5**.
- El gen `c` es un punto del universo de ese conjunto: el nivel de absorción que el portafolio asume.
- Cada individuo trae su propio `c`; selección, cruce y mutación lo evolucionan junto con los pesos.

### Consecuentes de salida (Mamdani)

Los consecuentes singleton de la v1.1 (0.20 / 0.50 / 0.85) se convierten en conjuntos difusos sobre CA ∈ [0, 1]. Propuesta inicial, a calibrar:

| Conjunto | Notación |
|---|---|
| Baja | `Trap(0, 0, 0.15, 0.4)` |
| Media | `Tri(0.25, 0.5, 0.75)` |
| Alta | `Trap(0.6, 0.85, 1, 1)` |

## Fitness propuesto

```
Fitness(P) = Σ wᵢ·μ'ᵢ − λ_ef·σ'(P) − φ·max(0, σ'(P) − σ_max(c))² + κ·μ_CA(c)

σ_max(c) = σ_piso + a·c
```

| Término | Origen |
|---|---|
| `Σ wᵢ·μ'ᵢ` | Retorno ajustado por las reglas de contexto |
| `λ_ef·σ'(P)` | **Conjunto difuso en la evaluación** (horizonte) |
| `φ·max(0, σ' − σ_max(c))²` | Penalización por volatilidad, ahora dependiente del gen |
| `κ·μ_CA(c)` | **Conjunto difuso en el cromosoma**: premia que `c` sea compatible con la capacidad real del usuario |

A esta fórmula se le suma la corrección elegida en D2 contra los portafolios degenerados (tope o diversificación).

### Por qué funciona

Un `c` alto relaja la penalización (permite más volatilidad y retorno), pero si el usuario tiene poca capacidad, `μ_CA(c)` cae y el fitness lo castiga. El AG busca el equilibrio. Es el enfoque de decisión difusa de Bellman–Zadeh: optimizar el objetivo y la restricción difusa a la vez. La desfuzzificación por centroide se sigue calculando, pero solo para la explicación y para compararla con el `c` evolucionado.

### Variante

Combinar objetivo y restricción con `min` (Bellman–Zadeh estricto) en vez de suma ponderada: más fiel a la teoría, más difícil de calibrar.

## Alternativas descartadas

| Alternativa | Motivo |
|---|---|
| Genes como etiquetas lingüísticas por categoría, desfuzzificadas a pesos | Pierde precisión y complica la restricción Σ = 1. |
| Genes que codifican parámetros de las funciones de membresía (sistema genético-difuso clásico) | Requiere datos de referencia para ajustar las funciones, y no los hay. |

## Parámetros nuevos

| Parámetro | Valor inicial | Nota |
|---|---|---|
| `κ` | 0.03 | Escala comparable a los retornos; calibrar entre 0.01 y 0.05 |
| Rango del gen `c` | [0, 1] | Mutación gaussiana con recorte |
