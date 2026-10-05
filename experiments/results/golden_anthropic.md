# Golden set de interpretación — proveedor `anthropic`

Casos: 23 · Generado por `scripts/eval_golden_set.py`.

| Métrica | Valor |
|---|---|
| Exactitud global por campo | 98.3 % |
| `complete` correcto | 100.0 % |
| Campo preguntado correcto | 100.0 % |
| Ambiguos/contradictorios con pregunta (objetivo 100 %) | 100.0 % |
| JSON válido (solo LLM) | 100.0 % |
| Latencia media / máxima | 2674.2 ms / 3187.9 ms |

## Exactitud por campo

| Campo | Exactitud |
|---|---|
| `ahorro_total` | 100.0 % |
| `cobertura_emergencia_meses` | 100.0 % |
| `horizonte_anios` | 100.0 % |
| `horizonte_etiqueta` | 100.0 % |
| `monto_invertir` | 100.0 % |
| `perfil_riesgo` | 91.3 % |
| `rechazos` | 100.0 % |

## Detalle por caso

| Caso | Campos fallados | `complete` | Pregunta | Fuente |
|---|---|---|---|---|
| completo-conservador | — | ok | — (ok) | llm |
| completo-moderado | `perfil_riesgo` | ok | — (ok) | llm |
| completo-agresivo | — | ok | — (ok) | llm |
| edad-no-es-horizonte | — | ok | — (ok) | llm |
| horizonte-vago-anitos | — | ok | horizonte (ok) | llm |
| horizonte-etiqueta-largo | — | ok | ahorro_total (ok) | llm |
| horizonte-en-meses | — | ok | ahorro_total (ok) | llm |
| falta-monto | — | ok | monto_invertir (ok) | llm |
| falta-monto-y-plazo | — | ok | monto_invertir (ok) | llm |
| contradictorio-max-sin-perder | — | ok | perfil_riesgo (ok) | llm |
| contradictorio-arriesgar-seguro | — | ok | perfil_riesgo (ok) | llm |
| monto-en-palabras | — | ok | ahorro_total (ok) | llm |
| monto-mil-con-palabras | — | ok | cobertura_emergencia_meses (ok) | llm |
| dolares-texto | — | ok | monto_invertir (ok) | llm |
| dolares-simbolo | — | ok | monto_invertir (ok) | llm |
| rechaza-ahorros | — | ok | — (ok) | llm |
| multi-turno-monto | — | ok | ahorro_total (ok) | llm |
| multi-turno-horizonte | — | ok | ahorro_total (ok) | llm |
| multi-turno-completo | — | ok | — (ok) | llm |
| multi-turno-resuelve-contradiccion | — | ok | ahorro_total (ok) | llm |
| horizonte-vago-en-unos-anos | — | ok | horizonte (ok) | llm |
| horizonte-vago-mas-adelante | `perfil_riesgo` | ok | horizonte (ok) | llm |
| horizonte-etiqueta-jubilacion | — | ok | ahorro_total (ok) | llm |
