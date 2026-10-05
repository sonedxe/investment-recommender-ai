# 04 · Calibración de κ, φ y tope

## Método

- Modelo completo con contexto neutral (0, 0). Se varía un parámetro a la vez y los demás quedan en su valor por defecto (κ = 0.03, φ = 50, tope = 0.40):

| Parámetro | Valores | Papel |
|---|---|---|
| κ | 0.01, 0.03, 0.05 | Peso de la recompensa κ·μ_CA(c) |
| φ | 10, 50, 200 | Dureza de la penalización por exceder σ_max(c) |
| Tope | 0.35, 0.40, 0.50 | Peso máximo por categoría (decisión D2) |

- Arquetipos moderado y agresivo, como pide el plan. Se agregó un tercer caso, **estrés de baja absorción** (λ_base 0.5, H = 5 años, ahorro S/ 12,000, 1 mes de emergencia), porque en los dos arquetipos pedidos la penalización nunca se activa (ver [01 · Ablación](01-ablacion.md)) y κ y φ no podrían evaluarse.
- 10 semillas por valor: 270 corridas. Datos: `experiments/results/calibration_runs.csv` y `calibration_summary.csv`.

## Resultados

Medias entre semillas; pesos, E y σ en %. "En el tope" es el número medio de categorías con peso igual al tope.

| Caso | Parámetro | Valor | Acciones | Mixtos | Deuda | Bonos | Plazo fijo | E | σ | HHI | En el tope | c | \|c − centroide\| | μ_CA(c) | Penalización activa |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Moderado | κ | 0.01 | 2.9 | 5.8 | 11.3 | 40.0 | 40.0 | 5.4 | 2.1 | 0.337 | 2.0 | 0.904 | 0.174 | 0.500 | 0 % |
| Moderado | κ | 0.03 | 2.9 | 5.8 | 11.3 | 40.0 | 40.0 | 5.4 | 2.1 | 0.337 | 2.0 | 0.913 | 0.182 | 0.500 | 0 % |
| Moderado | κ | 0.05 | 2.9 | 5.8 | 11.3 | 40.0 | 40.0 | 5.4 | 2.1 | 0.337 | 2.0 | 0.920 | 0.189 | 0.500 | 0 % |
| Moderado | φ | 10 | 2.9 | 5.8 | 11.3 | 40.0 | 40.0 | 5.4 | 2.1 | 0.337 | 2.0 | 0.913 | 0.182 | 0.500 | 0 % |
| Moderado | φ | 200 | 2.9 | 5.8 | 11.3 | 40.0 | 40.0 | 5.4 | 2.1 | 0.337 | 2.0 | 0.913 | 0.182 | 0.500 | 0 % |
| Moderado | Tope | 0.35 | 2.9 | 6.2 | 20.9 | 35.0 | 35.0 | 5.1 | 2.1 | 0.293 | 2.0 | 0.900 | 0.169 | 0.500 | 0 % |
| Moderado | Tope | 0.50 | 2.2 | 0.0 | 0.0 | 47.8 | 50.0 | 5.6 | 1.9 | 0.479 | 1.0 | 0.916 | 0.185 | 0.500 | 0 % |
| Agresivo | κ | 0.01 | 40.0 | 20.0 | 0.0 | 40.0 | 0.0 | 9.9 | 10.1 | 0.360 | 2.0 | 0.931 | 0.078 | 1.000 | 0 % |
| Agresivo | κ | 0.03 | 40.0 | 20.0 | 0.0 | 40.0 | 0.0 | 9.9 | 10.1 | 0.360 | 2.0 | 0.952 | 0.099 | 1.000 | 0 % |
| Agresivo | κ | 0.05 | 40.0 | 20.0 | 0.0 | 40.0 | 0.0 | 9.9 | 10.1 | 0.360 | 2.0 | 0.948 | 0.095 | 1.000 | 0 % |
| Agresivo | φ | 10 | 40.0 | 20.0 | 0.0 | 40.0 | 0.0 | 9.9 | 10.1 | 0.360 | 2.0 | 0.952 | 0.099 | 1.000 | 0 % |
| Agresivo | φ | 200 | 40.0 | 20.0 | 0.0 | 40.0 | 0.0 | 9.9 | 10.1 | 0.360 | 2.0 | 0.952 | 0.099 | 1.000 | 0 % |
| Agresivo | Tope | 0.35 | 35.0 | 30.0 | 0.0 | 35.0 | 0.0 | 9.5 | 9.4 | 0.335 | 2.0 | 0.932 | 0.079 | 1.000 | 0 % |
| Agresivo | Tope | 0.50 | 50.0 | 0.0 | 0.0 | 50.0 | 0.0 | 10.8 | 11.6 | 0.500 | 2.0 | 0.943 | 0.089 | 1.000 | 0 % |
| Estrés | κ | 0.01 | 21.3 | 9.8 | 0.0 | 40.0 | 29.0 | 7.7 | 5.6 | 0.299 | 1.0 | 0.202 | 0.046 | 0.778 | 90 % |
| Estrés | κ | 0.03 | 21.3 | 9.7 | 0.0 | 40.0 | 29.0 | 7.7 | 5.6 | 0.299 | 1.0 | 0.203 | 0.046 | 0.778 | 70 % |
| Estrés | κ | 0.05 | 21.2 | 9.7 | 0.0 | 40.0 | 29.1 | 7.7 | 5.6 | 0.299 | 1.0 | 0.202 | 0.046 | 0.778 | 70 % |
| Estrés | φ | 10 | 21.5 | 10.0 | 0.0 | 40.0 | 28.5 | 7.7 | 5.7 | 0.297 | 1.0 | 0.204 | 0.047 | 0.778 | 100 % |
| Estrés | φ | 200 | 21.2 | 9.7 | 0.0 | 40.0 | 29.2 | 7.7 | 5.6 | 0.299 | 1.0 | 0.201 | 0.045 | 0.778 | 80 % |
| Estrés | Tope | 0.35 | 21.5 | 10.4 | 0.0 | 35.0 | 33.1 | 7.6 | 5.6 | 0.289 | 1.0 | 0.202 | 0.045 | 0.778 | 70 % |
| Estrés | Tope | 0.50 | 20.7 | 8.6 | 0.0 | 50.0 | 20.7 | 7.8 | 5.7 | 0.343 | 1.0 | 0.204 | 0.047 | 0.778 | 90 % |

Las filas φ = 50 y tope = 0.40 coinciden con κ = 0.03 (los tres son la configuración por defecto) y se omiten. La tabla completa está en `experiments/results/README.md`.

![Efecto de κ, φ y tope sobre σ y c](../../experiments/results/fig_calibration.png)

## Interpretación (para el informe, sección 9.x)

**κ (recompensa difusa).** En el rango 0.01–0.05 no cambia ningún peso en los tres casos; solo mueve `c` dentro de la meseta de μ_CA (por ejemplo, moderado 0.904 a 0.920). En la primera versión del experimento, con κ = 0.01 una parte de las semillas del moderado terminaba con `c` fuera de la meseta (μ_CA(c) medio 0.467 frente a 0.500); desde que los `c` iniciales se muestrean de μ_CA y su mutación es más amplia (ver [01 · Ablación](01-ablacion.md#limitaciones-observadas)), todas las semillas quedan en la meseta también con κ = 0.01. κ = 0.03 da una recompensa (≤ 0.03) del mismo orden que las diferencias de fitness entre portafolios cercanos sin dominar el término de retorno y riesgo. **Se mantiene κ = 0.03.**

**φ (dureza de la penalización).** Solo actúa en el caso de estrés y su efecto es pequeño: σ pasa de 5.7 % (φ 10) a 5.6 % (φ 50 y 200), y los pesos varían menos de 1 pp. A partir de φ ≈ 50 la restricción ya se comporta casi como un límite duro (σ queda a 0.1 pp o menos de σ_max(c) = 5.6 %). φ = 10 deja pasar algo más de exceso; φ = 200 no aporta diferencia medible y vuelve más abrupta la superficie de fitness. **Se mantiene φ = 50.**

**Tope por categoría.** Es el parámetro con mayor efecto:

- Con 0.50 el moderado queda en tres categorías con HHI 0.479 (bonos 47.8 % y plazo fijo 50.0 %) y el agresivo en dos (acciones y bonos al 50 %, HHI 0.500): reaparece el portafolio degenerado que motivó la decisión D2.
- Con 0.35 el HHI baja (0.293 en moderado, 0.335 en agresivo) a costa de 0.3 a 0.4 pp de retorno esperado.
- 0.40 está en medio: el moderado conserva cinco categorías y el agresivo tres (40/20/40), sin portafolios de dos categorías. **Se mantiene el tope de 0.40.** Si el equipo quisiera más diversificación, 0.35 es una alternativa defendible con este costo de retorno; no se cambia `data/parameters`.

## Limitaciones observadas

- κ y φ son poco sensibles en el rango probado. Esto es una buena noticia para la robustez, pero también significa que el experimento no los "calibra" en sentido estricto: confirma que los valores por defecto están en una zona estable.
- La penalización solo es relevante con absorción baja y perfiles que buscan riesgo; para la mayoría de usuarios el resultado depende de λ_ef, del contexto y del tope.
- La columna "Penalización activa" del caso de estrés (70 % a 100 %) cuenta penalizaciones de cualquier tamaño, incluso excesos de centésimas de punto porcentual; no indica un exceso relevante de volatilidad.
