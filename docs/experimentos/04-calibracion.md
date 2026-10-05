# 04 · Calibración de κ, φ y tope

## Método

- Modelo completo con contexto neutral (0, 0). Se varía un parámetro a la vez y los demás quedan en su valor por defecto (κ = 0.03, φ = 50, tope = 0.40):

| Parámetro | Valores | Papel |
|---|---|---|
| κ | 0.01, 0.03, 0.05 | Peso de la recompensa κ·μ_CA(c) |
| φ | 10, 50, 200 | Dureza de la penalización por exceder σ_max(c) |
| Tope | 0.35, 0.40, 0.50 | Peso máximo por categoría (decisión D2) |

- Arquetipos moderado y agresivo, como pide el plan. Se agregó un tercer caso, **estrés de baja absorción** (λ_base 0.5, H = 5 años, ahorro S/ 12,000, 1 mes de emergencia), porque en los dos arquetipos pedidos la penalización nunca se activa (ver [01 · Ablación](01-ablacion.md)) y κ y φ no podrían evaluarse. Con datos reales tampoco se activa en este caso con los valores por defecto; solo con tope 0.35 (ver abajo).
- 10 semillas por valor: 270 corridas. Datos: `experiments/results/calibration_runs.csv` y `calibration_summary.csv`.

## Resultados

Medias entre semillas; pesos, E y σ en %. "En el tope" es el número medio de categorías con peso igual al tope.

| Caso | Parámetro | Valor | Acciones | Mixtos | Deuda | Bonos | Plazo fijo | E | σ | HHI | En el tope | c | \|c − centroide\| | μ_CA(c) | Penalización activa |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Moderado | κ | 0.01 | 0.0 | 14.8 | 40.0 | 5.2 | 40.0 | 5.1 | 1.4 | 0.345 | 2.0 | 0.892 | 0.161 | 0.500 | 0 % |
| Moderado | κ | 0.03 | 0.0 | 14.8 | 40.0 | 5.2 | 40.0 | 5.1 | 1.4 | 0.345 | 2.0 | 0.883 | 0.152 | 0.500 | 0 % |
| Moderado | κ | 0.05 | 0.0 | 14.8 | 40.0 | 5.2 | 40.0 | 5.1 | 1.4 | 0.345 | 2.0 | 0.886 | 0.156 | 0.500 | 0 % |
| Moderado | φ | 10 | 0.0 | 14.8 | 40.0 | 5.2 | 40.0 | 5.1 | 1.4 | 0.345 | 2.0 | 0.883 | 0.152 | 0.500 | 0 % |
| Moderado | φ | 200 | 0.0 | 14.8 | 40.0 | 5.2 | 40.0 | 5.1 | 1.4 | 0.345 | 2.0 | 0.883 | 0.152 | 0.500 | 0 % |
| Moderado | Tope | 0.35 | 0.0 | 21.2 | 35.0 | 8.8 | 35.0 | 5.4 | 2.0 | 0.298 | 2.0 | 0.878 | 0.147 | 0.500 | 0 % |
| Moderado | Tope | 0.50 | 0.0 | 5.0 | 50.0 | 0.0 | 45.0 | 4.6 | 0.6 | 0.455 | 1.0 | 0.900 | 0.170 | 0.500 | 0 % |
| Agresivo | κ | 0.01 | 40.0 | 40.0 | 20.0 | 0.0 | 0.0 | 9.9 | 11.1 | 0.360 | 2.0 | 0.937 | 0.084 | 1.000 | 0 % |
| Agresivo | κ | 0.03 | 40.0 | 40.0 | 20.0 | 0.0 | 0.0 | 9.9 | 11.1 | 0.360 | 2.0 | 0.956 | 0.103 | 1.000 | 0 % |
| Agresivo | κ | 0.05 | 40.0 | 40.0 | 20.0 | 0.0 | 0.0 | 9.9 | 11.1 | 0.360 | 2.0 | 0.947 | 0.094 | 1.000 | 0 % |
| Agresivo | φ | 10 | 40.0 | 40.0 | 20.0 | 0.0 | 0.0 | 9.9 | 11.1 | 0.360 | 2.0 | 0.956 | 0.103 | 1.000 | 0 % |
| Agresivo | φ | 200 | 40.0 | 40.0 | 20.0 | 0.0 | 0.0 | 9.9 | 11.1 | 0.360 | 2.0 | 0.956 | 0.103 | 1.000 | 0 % |
| Agresivo | Tope | 0.35 | 35.0 | 35.0 | 30.0 | 0.0 | 0.0 | 9.3 | 9.7 | 0.335 | 2.0 | 0.953 | 0.100 | 1.000 | 0 % |
| Agresivo | Tope | 0.50 | 50.0 | 50.0 | 0.0 | 0.0 | 0.0 | 11.2 | 13.8 | 0.500 | 2.0 | 0.944 | 0.091 | 1.000 | 0 % |
| Estrés | κ | 0.01 | 11.7 | 40.0 | 40.0 | 8.3 | 0.0 | 7.5 | 5.4 | 0.341 | 2.0 | 0.190 | 0.033 | 0.778 | 0 % |
| Estrés | κ | 0.03 | 11.7 | 40.0 | 40.0 | 8.3 | 0.0 | 7.5 | 5.4 | 0.341 | 2.0 | 0.192 | 0.035 | 0.778 | 0 % |
| Estrés | κ | 0.05 | 11.7 | 40.0 | 40.0 | 8.3 | 0.0 | 7.5 | 5.4 | 0.341 | 2.0 | 0.192 | 0.035 | 0.778 | 0 % |
| Estrés | φ | 10 | 11.7 | 40.0 | 40.0 | 8.3 | 0.0 | 7.5 | 5.4 | 0.341 | 2.0 | 0.191 | 0.034 | 0.778 | 0 % |
| Estrés | φ | 200 | 11.7 | 40.0 | 40.0 | 8.3 | 0.0 | 7.5 | 5.4 | 0.341 | 2.0 | 0.190 | 0.033 | 0.778 | 0 % |
| Estrés | Tope | 0.35 | 13.1 | 35.0 | 35.0 | 16.9 | 0.0 | 7.5 | 5.7 | 0.291 | 2.0 | 0.203 | 0.046 | 0.778 | 100 % |
| Estrés | Tope | 0.50 | 5.9 | 44.1 | 50.0 | 0.0 | 0.0 | 7.0 | 4.4 | 0.448 | 1.0 | 0.145 | 0.011 | 0.778 | 0 % |

Las filas φ = 50 y tope = 0.40 coinciden con κ = 0.03 (los tres son la configuración por defecto) y se omiten. La tabla completa está en `experiments/results/README.md`.

![Efecto de κ, φ y tope sobre σ y c](../../experiments/results/fig_calibration.png)

## Interpretación (para el informe, sección 9.x)

**κ (recompensa difusa).** En el rango 0.01–0.05 no cambia ningún peso en los tres casos; solo mueve `c` dentro de la meseta de μ_CA (por ejemplo, moderado 0.883 a 0.892). Todas las semillas quedan en la meseta también con κ = 0.01, gracias al muestreo de los `c` iniciales desde μ_CA y a su mutación más amplia (ver [01 · Ablación](01-ablacion.md#limitaciones-observadas)). κ = 0.03 da una recompensa (≤ 0.03) del mismo orden que las diferencias de fitness entre portafolios cercanos sin dominar el término de retorno y riesgo. **Se mantiene κ = 0.03.**

**φ (dureza de la penalización).** Con los valores por defecto no actúa en ninguno de los tres casos: el caso de estrés (λ_base 0.5, absorción baja) elige σ = 5.4 %, justo por debajo de σ_max(c) = 5.5 % (con `c` ≈ 0.19, cerca del borde de la meseta), y la penalización queda en 0 % de las semillas. Solo con tope 0.35 el estrés la activa en las 10 semillas (σ 5.7 % frente a σ_max 5.6 %). El efecto de φ aparece sobre todo con λ_base = 0.2 (ver [03 · Gen difuso](03-gen-difuso.md): absorción baja, σ 5.9 % frente a σ_max 5.7 %, y media, 11.2 % frente a 11.1 %), donde la restricción ya se comporta casi como un límite duro con φ = 50. **Se mantiene φ = 50**, sin evidencia nueva a favor de cambiarlo.

**Tope por categoría.** Es el parámetro con mayor efecto:

- Con 0.50 el moderado queda prácticamente en tres categorías con dos dominantes (deuda 50.0 %, plazo fijo 45.0 %, mixtos 5.0 %; HHI 0.455, σ 0.6 %) y el agresivo en dos (acciones 50 %, mixtos 50 %; HHI 0.500, σ 13.8 %): reaparece el portafolio concentrado que motivó la decisión D2.
- Con 0.35 el HHI baja (0.298 en moderado, 0.335 en agresivo). En el moderado el retorno esperado sube de 5.1 % a 5.4 % (con σ de 1.4 % a 2.0 %), porque el tope obliga a sacar peso de deuda y plazo fijo hacia mixtos y bonos; en el agresivo baja de 9.9 % a 9.3 %.
- 0.40 está en medio: el moderado conserva cuatro categorías y el agresivo tres (40/40/20), sin portafolios de dos categorías. **Se mantiene el tope de 0.40.** Si el equipo quisiera más diversificación, 0.35 es una alternativa defendible; no se cambia `data/parameters`.

## Qué cambió con datos reales (W14)

- Antes el caso de estrés activaba la penalización en 70 % a 100 % de las semillas (σ 5.6–5.7 %, con 21 % en acciones); ahora elige 11.6 % en acciones y σ 3.0 %, sin penalización. φ ya no se puede evaluar en este caso; el experimento del gen difuso lo cubre con λ_base = 0.2.
- En el agresivo la deuda reemplaza a los mixtos y a parte de los bonos (antes 40/20/0/40/0; ahora 40/0/40/20/0) y en el moderado deuda y plazo fijo quedan en el tope en lugar de bonos y plazo fijo. Los mixtos (compuesto 0.5 × acciones + 0.5 × bonos) quedan en 0 % en todas las filas.
- Las decisiones sobre κ, φ y tope no cambian.

## Qué cambió con el Fondo 2 de las AFP (W15)

- Los mixtos pasan de 0 % en todas las filas a 5.0 %–50.0 %: en el moderado reemplazan a las acciones (3.0 % → 0 %) y a parte de los bonos (17.0 % → 5.2 %); en el agresivo reemplazan a la deuda y a los bonos (40/0/40/20/0 → 40/40/20/0/0, E de 8.7 % a 9.9 %, σ de 9.2 % a 11.1 %).
- El caso de estrés pide más riesgo (σ 5.4 %, antes 3.0 %; 40 % en mixtos) y queda al borde de σ_max(c): la penalización se activa con tope 0.35, de modo que φ vuelve a ser observable en este caso, aunque solo en esa fila.
- Convergencia: 3 de las 270 corridas (estrés con tope 0.35, semillas 1, 3 y 6) llegan al máximo de 200 generaciones; el resto converge.
- Las decisiones sobre κ, φ y tope no cambian.

## Limitaciones observadas

- κ y φ son poco sensibles en el rango probado. Esto es una buena noticia para la robustez, pero también significa que el experimento no los "calibra" en sentido estricto: confirma que los valores por defecto están en una zona estable.
- La penalización solo es relevante con absorción baja o media y perfiles muy arriesgados (λ_base = 0.2); para la mayoría de usuarios el resultado depende de λ_ef, del contexto y del tope.
