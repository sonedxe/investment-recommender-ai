# 04 · Calibración de κ, φ y tope

## Método

- Modelo completo con contexto neutral (0, 0). Se varía un parámetro a la vez y los demás quedan en su valor por defecto (κ = 0.03, φ = 50, tope = 0.40):

| Parámetro | Valores | Papel |
|---|---|---|
| κ | 0.01, 0.03, 0.05 | Peso de la recompensa κ·μ_CA(c) |
| φ | 10, 50, 200 | Dureza de la penalización por exceder σ_max(c) |
| Tope | 0.35, 0.40, 0.50 | Peso máximo por categoría (decisión D2) |

- Arquetipos moderado y agresivo, como pide el plan. Se agregó un tercer caso, **estrés de baja absorción** (λ_base 0.5, H = 5 años, ahorro S/ 12,000, 1 mes de emergencia), porque en los dos arquetipos pedidos la penalización nunca se activa (ver [01 · Ablación](01-ablacion.md)) y κ y φ no podrían evaluarse. Con datos reales (W14) tampoco se activa en este caso (ver abajo).
- 10 semillas por valor: 270 corridas. Datos: `experiments/results/calibration_runs.csv` y `calibration_summary.csv`.

## Resultados

Medias entre semillas; pesos, E y σ en %. "En el tope" es el número medio de categorías con peso igual al tope.

| Caso | Parámetro | Valor | Acciones | Mixtos | Deuda | Bonos | Plazo fijo | E | σ | HHI | En el tope | c | \|c − centroide\| | μ_CA(c) | Penalización activa |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Moderado | κ | 0.01 | 3.0 | 0.0 | 40.0 | 17.0 | 40.0 | 4.9 | 1.6 | 0.350 | 2.0 | 0.895 | 0.165 | 0.500 | 0 % |
| Moderado | κ | 0.03 | 3.0 | 0.0 | 40.0 | 17.0 | 40.0 | 4.9 | 1.6 | 0.350 | 2.0 | 0.907 | 0.176 | 0.500 | 0 % |
| Moderado | κ | 0.05 | 3.0 | 0.0 | 40.0 | 17.0 | 40.0 | 4.9 | 1.6 | 0.350 | 2.0 | 0.903 | 0.172 | 0.500 | 0 % |
| Moderado | φ | 10 | 3.0 | 0.0 | 40.0 | 17.0 | 40.0 | 4.9 | 1.6 | 0.350 | 2.0 | 0.907 | 0.176 | 0.500 | 0 % |
| Moderado | φ | 200 | 3.0 | 0.0 | 40.0 | 17.0 | 40.0 | 4.9 | 1.6 | 0.350 | 2.0 | 0.907 | 0.176 | 0.500 | 0 % |
| Moderado | Tope | 0.35 | 4.3 | 0.0 | 35.0 | 25.7 | 35.0 | 5.1 | 2.3 | 0.313 | 2.0 | 0.914 | 0.184 | 0.500 | 0 % |
| Moderado | Tope | 0.50 | 1.1 | 0.0 | 50.0 | 0.0 | 48.8 | 4.5 | 0.5 | 0.489 | 1.0 | 0.890 | 0.159 | 0.500 | 0 % |
| Agresivo | κ | 0.01 | 40.0 | 0.0 | 40.0 | 20.0 | 0.0 | 8.7 | 9.2 | 0.360 | 2.0 | 0.953 | 0.100 | 1.000 | 0 % |
| Agresivo | κ | 0.03 | 40.0 | 0.0 | 40.0 | 20.0 | 0.0 | 8.7 | 9.2 | 0.360 | 2.0 | 0.949 | 0.096 | 1.000 | 0 % |
| Agresivo | κ | 0.05 | 40.0 | 0.0 | 40.0 | 20.0 | 0.0 | 8.7 | 9.2 | 0.360 | 2.0 | 0.961 | 0.108 | 1.000 | 0 % |
| Agresivo | φ | 10 | 40.0 | 0.0 | 40.0 | 20.0 | 0.0 | 8.7 | 9.2 | 0.360 | 2.0 | 0.949 | 0.096 | 1.000 | 0 % |
| Agresivo | φ | 200 | 40.0 | 0.0 | 40.0 | 20.0 | 0.0 | 8.7 | 9.2 | 0.360 | 2.0 | 0.949 | 0.096 | 1.000 | 0 % |
| Agresivo | Tope | 0.35 | 35.0 | 0.0 | 35.0 | 30.0 | 0.0 | 8.3 | 8.4 | 0.335 | 2.0 | 0.945 | 0.092 | 1.000 | 0 % |
| Agresivo | Tope | 0.50 | 50.0 | 0.0 | 46.2 | 3.8 | 0.0 | 9.5 | 10.9 | 0.465 | 1.0 | 0.970 | 0.117 | 1.000 | 0 % |
| Estrés | κ | 0.01 | 11.6 | 0.0 | 40.0 | 15.0 | 33.4 | 5.7 | 3.0 | 0.307 | 1.0 | 0.105 | 0.051 | 0.778 | 0 % |
| Estrés | κ | 0.03 | 11.6 | 0.0 | 40.0 | 15.0 | 33.4 | 5.7 | 3.0 | 0.308 | 1.0 | 0.093 | 0.064 | 0.778 | 0 % |
| Estrés | κ | 0.05 | 11.6 | 0.0 | 40.0 | 15.0 | 33.4 | 5.7 | 3.0 | 0.308 | 1.0 | 0.075 | 0.082 | 0.778 | 0 % |
| Estrés | φ | 10 | 11.6 | 0.0 | 40.0 | 15.0 | 33.4 | 5.7 | 3.0 | 0.308 | 1.0 | 0.071 | 0.086 | 0.778 | 0 % |
| Estrés | φ | 200 | 11.6 | 0.0 | 40.0 | 15.0 | 33.4 | 5.7 | 3.0 | 0.308 | 1.0 | 0.083 | 0.073 | 0.778 | 0 % |
| Estrés | Tope | 0.35 | 12.9 | 0.0 | 35.0 | 17.1 | 35.0 | 5.8 | 3.4 | 0.291 | 1.8 | 0.119 | 0.038 | 0.778 | 0 % |
| Estrés | Tope | 0.50 | 12.1 | 0.0 | 50.0 | 15.8 | 22.1 | 5.9 | 3.2 | 0.338 | 1.0 | 0.103 | 0.053 | 0.778 | 0 % |

Las filas φ = 50 y tope = 0.40 coinciden con κ = 0.03 (los tres son la configuración por defecto) y se omiten. La tabla completa está en `experiments/results/README.md`.

![Efecto de κ, φ y tope sobre σ y c](../../experiments/results/fig_calibration.png)

## Interpretación (para el informe, sección 9.x)

**κ (recompensa difusa).** En el rango 0.01–0.05 no cambia ningún peso en los tres casos; solo mueve `c` dentro de la meseta de μ_CA (por ejemplo, moderado 0.895 a 0.907). Todas las semillas quedan en la meseta también con κ = 0.01, gracias al muestreo de los `c` iniciales desde μ_CA y a su mutación más amplia (ver [01 · Ablación](01-ablacion.md#limitaciones-observadas)). κ = 0.03 da una recompensa (≤ 0.03) del mismo orden que las diferencias de fitness entre portafolios cercanos sin dominar el término de retorno y riesgo. **Se mantiene κ = 0.03.**

**φ (dureza de la penalización).** Con datos reales no actúa en ninguno de los tres casos: el caso de estrés (λ_base 0.5, absorción baja) elige σ = 3.0 %, por debajo de σ_max(c) (3.9 % a 4.5 % según la semilla y el valor), y la penalización queda en 0 % de las semillas. El efecto de φ solo aparece con λ_base = 0.2 (ver [03 · Gen difuso](03-gen-difuso.md): absorción baja, σ 6.0 % frente a σ_max 5.7 %, y media, 11.2 % frente a 11.1 %), donde la restricción ya se comporta casi como un límite duro con φ = 50. **Se mantiene φ = 50**, sin evidencia nueva a favor de cambiarlo.

**Tope por categoría.** Es el parámetro con mayor efecto:

- Con 0.50 el moderado queda prácticamente en dos categorías (deuda 50.0 %, plazo fijo 48.8 %, acciones 1.1 %; HHI 0.489, σ 0.5 %) y el agresivo en tres con HHI 0.465 (acciones 50 %, deuda 46.2 %, bonos 3.8 %): reaparece el portafolio concentrado que motivó la decisión D2.
- Con 0.35 el HHI baja (0.313 en moderado, 0.335 en agresivo). En el moderado el retorno esperado sube de 4.9 % a 5.1 % (con σ de 1.6 % a 2.3 %), porque el tope obliga a sacar peso de deuda y plazo fijo hacia acciones y bonos; en el agresivo baja de 8.7 % a 8.3 %.
- 0.40 está en medio: el moderado conserva cuatro categorías y el agresivo tres (40/40/20), sin portafolios de dos categorías. **Se mantiene el tope de 0.40.** Si el equipo quisiera más diversificación, 0.35 es una alternativa defendible; no se cambia `data/parameters`.

## Qué cambió con datos reales (W14)

- Antes el caso de estrés activaba la penalización en 70 % a 100 % de las semillas (σ 5.6–5.7 %, con 21 % en acciones); ahora elige 11.6 % en acciones y σ 3.0 %, sin penalización. φ ya no se puede evaluar en este caso; el experimento del gen difuso lo cubre con λ_base = 0.2.
- En el agresivo la deuda reemplaza a los mixtos y a parte de los bonos (antes 40/20/0/40/0; ahora 40/0/40/20/0) y en el moderado deuda y plazo fijo quedan en el tope en lugar de bonos y plazo fijo. Los mixtos (compuesto 0.5 × acciones + 0.5 × bonos) quedan en 0 % en todas las filas.
- Las decisiones sobre κ, φ y tope no cambian.

## Limitaciones observadas

- κ y φ son poco sensibles en el rango probado. Esto es una buena noticia para la robustez, pero también significa que el experimento no los "calibra" en sentido estricto: confirma que los valores por defecto están en una zona estable.
- La penalización solo es relevante con absorción baja o media y perfiles muy arriesgados (λ_base = 0.2); para la mayoría de usuarios el resultado depende de λ_ef, del contexto y del tope.
