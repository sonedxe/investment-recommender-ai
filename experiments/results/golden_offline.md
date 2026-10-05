# Golden set de interpretación — proveedor `offline`

Casos: 20 · Generado por `scripts/eval_golden_set.py`.

| Métrica | Valor |
|---|---|
| Exactitud global por campo | 97.1 % |
| `complete` correcto | 100.0 % |
| Campo preguntado correcto | 90.0 % |
| Ambiguos/contradictorios con pregunta (objetivo 100 %) | 100.0 % |
| JSON válido (solo LLM) | n/a |
| Latencia media / máxima | 0.9 ms / 1.6 ms |

## Exactitud por campo

| Campo | Exactitud |
|---|---|
| `ahorro_total` | 95.0 % |
| `cobertura_emergencia_meses` | 100.0 % |
| `horizonte_anios` | 100.0 % |
| `horizonte_etiqueta` | 100.0 % |
| `monto_invertir` | 90.0 % |
| `perfil_riesgo` | 100.0 % |
| `rechazos` | 100.0 % |

## Detalle por caso

| Caso | Campos fallados | `complete` | Pregunta | Fuente |
|---|---|---|---|---|
| completo-conservador | — | ok | — (ok) | offline |
| completo-moderado | — | ok | — (ok) | offline |
| completo-agresivo | — | ok | — (ok) | offline |
| edad-no-es-horizonte | — | ok | — (ok) | offline |
| horizonte-vago-anitos | — | ok | horizonte (ok) | offline |
| horizonte-etiqueta-largo | — | ok | ahorro_total (ok) | offline |
| horizonte-en-meses | — | ok | ahorro_total (ok) | offline |
| falta-monto | — | ok | monto_invertir (ok) | offline |
| falta-monto-y-plazo | — | ok | monto_invertir (ok) | offline |
| contradictorio-max-sin-perder | — | ok | perfil_riesgo (ok) | offline |
| contradictorio-arriesgar-seguro | — | ok | perfil_riesgo (ok) | offline |
| monto-en-palabras | `monto_invertir` | ok | monto_invertir (FALLA) | offline |
| monto-mil-con-palabras | `monto_invertir`, `ahorro_total` | ok | monto_invertir (FALLA) | offline |
| dolares-texto | — | ok | monto_invertir (ok) | offline |
| dolares-simbolo | — | ok | monto_invertir (ok) | offline |
| rechaza-ahorros | — | ok | — (ok) | offline |
| multi-turno-monto | — | ok | ahorro_total (ok) | offline |
| multi-turno-horizonte | — | ok | ahorro_total (ok) | offline |
| multi-turno-completo | — | ok | — (ok) | offline |
| multi-turno-resuelve-contradiccion | — | ok | ahorro_total (ok) | offline |
