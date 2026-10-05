# 02 · Feedback del docente y brecha de la v1.1

## Qué pidió el docente (semana 5)

1. **Un conjunto difuso en la evaluación (fitness).**
2. **Otro conjunto difuso como componente de la cadena genética (cromosoma).**
3. Reglas de contexto (factores ambientales: panorama político, tendencia o precedente por categoría con un valor por defecto) que influyan **directamente** en la función de aptitud.

## Qué hace la v1.1

| Concepto difuso | Salida | Dónde actúa |
|---|---|---|
| Horizonte temporal | `λ_ef = λ_base · m_H` | Parámetro del fitness |
| Capacidad de absorción | `σ_max = σ_piso + a · CA` | Parámetro del fitness (penalización) |

El cromosoma sigue siendo `[w1, w2, w3, w4, w5]`, igual que en la semana 3. **Ningún elemento difuso forma parte de la cadena genética**: el punto 2 no está cubierto.

## Inconsistencia en el discurso del equipo

El resumen del equipo dice que ambos conceptos "influyen en el valor de λ". El informe dice que el horizonte modula λ y la absorción modula σ_max. Hay que unificarlo antes de la exposición.

## Estado del punto 3

Las reglas de contexto ya están **diseñadas** en la v1.1 (RC1–RC7, sección 4.6 y Anexo C); no quedan "por definir". Falta calibrarlas, implementarlas y presentarlas como reglas explícitas (ver [05 §6](05-hallazgos-tecnicos.md#6-reglas-de-contexto)).

## Solución propuesta

Ver [04-propuesta-difusa-cromosoma.md](04-propuesta-difusa-cromosoma.md).
