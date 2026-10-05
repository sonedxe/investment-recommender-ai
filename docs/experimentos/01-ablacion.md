# 01 · Ablación

## Método

- Cuatro configuraciones del modelo, con los interruptores de `recommend` (`Switches`):

| Configuración | Difuso | Contexto | Qué se apaga |
|---|---|---|---|
| Base | Off | Off | m_H = 1 (λ_ef = λ_base), sin penalización de volatilidad ni recompensa κ; sin ajuste de contexto |
| Solo difuso | On | Off | Sin ajuste de contexto (c_ctx = 0, σ' = σ) |
| Solo contexto | Off | On | Igual que la base en lo difuso |
| Completo | On | On | Nada |

- Tres arquetipos (conservador, moderado, agresivo; ver el [índice](README.md#configuración-común)) × 10 semillas = 120 corridas.
- Las configuraciones con contexto usan un panorama levemente adverso (político −0.5, macro 0) para que su efecto sea visible; la tendencia de mercado es la de los datos (acciones +1, mixtos +1, deuda +0.87, bonos −0.46, plazo fijo −0.18; desde W15 los mixtos son el valor cuota del Fondo 2 de las AFP, SBS).
- Métricas: pesos por categoría, retorno esperado E (incluye el ajuste de contexto), volatilidad σ, fitness, índice de Herfindahl (HHI = Σwᵢ²; 0.2 es reparto uniforme, 1 es una sola categoría), `c`, μ_CA(c), centroide, λ_ef y generaciones hasta converger.
- Datos: `experiments/results/ablation_runs.csv` y `ablation_summary.csv`.

## Resultados

Media ± desviación estándar entre semillas. Pesos, E y σ en %. Con el difuso apagado `c` no interviene en el fitness (su valor es aleatorio) y μ_CA(c) no aplica (n/d).

| Arquetipo | Configuración | Acciones | Mixtos | Deuda | Bonos | Plazo fijo | E | σ | Fitness | HHI | c | μ_CA(c) | Centroide | λ_ef | Gen. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Conservador | Base | 0.0 | 8.7 | 40.0 | 11.3 | 40.0 | 4.5 | 1.3 | 0.0188 | 0.340 | 0.508 ± 0.242 | n/d | 0.157 | 2.000 | 50.2 ± 8.2 |
| Conservador | Solo difuso | 0.0 | 8.6 | 40.0 | 11.4 | 40.0 | 4.5 | 1.3 | 0.0291 | 0.340 | 0.072 ± 0.059 | 0.778 | 0.157 | 3.000 | 57.6 ± 11.3 |
| Conservador | Solo contexto | 0.0 | 10.3 | 40.0 | 9.7 | 40.0 | 4.7 | 1.5 | 0.0181 | 0.340 | 0.375 ± 0.190 | n/d | 0.157 | 2.000 | 51.7 ± 12.3 |
| Conservador | Completo | 0.0 | 9.4 | 40.0 | 10.6 | 40.0 | 4.7 | 1.4 | 0.0269 | 0.340 | 0.068 ± 0.047 | 0.778 | 0.157 | 3.000 | 56.9 ± 14.7 |
| Moderado | Base | 0.0 | 9.2 | 40.0 | 10.8 | 40.0 | 4.5 | 1.3 | 0.0319 | 0.340 | 0.496 ± 0.231 | n/d | 0.731 | 1.000 | 47.2 ± 3.6 |
| Moderado | Solo difuso | 0.0 | 9.2 | 40.0 | 10.8 | 40.0 | 4.5 | 1.3 | 0.0469 | 0.340 | 0.898 ± 0.059 | 0.500 | 0.731 | 1.000 | 53.2 ± 8.3 |
| Moderado | Solo contexto | 0.0 | 12.9 | 40.0 | 7.1 | 40.0 | 4.8 | 1.5 | 0.0327 | 0.342 | 0.491 ± 0.220 | n/d | 0.731 | 1.000 | 52.8 ± 9.3 |
| Moderado | Completo | 0.0 | 12.9 | 40.0 | 7.1 | 40.0 | 4.8 | 1.5 | 0.0477 | 0.342 | 0.899 ± 0.054 | 0.500 | 0.731 | 1.000 | 51.8 ± 9.1 |
| Agresivo | Base | 3.7 | 8.3 | 30.9 | 17.0 | 40.0 | 4.9 | 2.1 | 0.0387 | 0.293 | 0.436 ± 0.241 | n/d | 0.853 | 0.500 | 145.6 ± 41.2 |
| Agresivo | Solo difuso | 40.0 | 20.0 | 0.0 | 40.0 | 0.0 | 8.6 | 11.0 | 0.0772 | 0.360 | 0.948 ± 0.041 | 1.000 | 0.853 | 0.350 | 45.9 ± 8.8 |
| Agresivo | Solo contexto | 0.0 | 19.9 | 40.0 | 0.1 | 40.0 | 4.9 | 1.8 | 0.0406 | 0.360 | 0.385 ± 0.200 | n/d | 0.853 | 0.500 | 48.0 ± 5.5 |
| Agresivo | Completo | 9.7 | 40.0 | 40.0 | 10.3 | 0.0 | 6.7 | 6.0 | 0.0762 | 0.340 | 0.941 ± 0.034 | 1.000 | 0.853 | 0.350 | 45.7 ± 6.4 |

Los pesos, E, σ, fitness y HHI tienen desviación prácticamente nula entre semillas: en los pesos es menor que 0.01 pp en 11 de las 12 celdas y 0.11 pp en el agresivo base; en el fitness, menor que 10⁻⁷. El AG converge al mismo portafolio con las 10 semillas, por eso se omite el ± en esas columnas. 118 de las 120 corridas terminaron por convergencia (25 generaciones sin mejora); las otras 2 (agresivo base, semillas 2 y 8) llegaron al máximo de 200 generaciones con el mismo portafolio que las demás.

![Pesos medios por configuración y arquetipo](../../experiments/results/fig_ablation_weights.png)

![Convergencia del AG, modelo completo, semilla 0](../../experiments/results/fig_convergence.png)

## Interpretación (para el informe, sección 9.x)

**Horizonte difuso.** Es el componente con mayor efecto sobre los pesos, y solo se ve en el agresivo. El horizonte largo (H = 12 años, m_H = 0.7) baja la aversión efectiva de 0.5 a 0.35 y el portafolio pasa de 3.7 % a 40.0 % en acciones y de 8.3 % a 20.0 % en mixtos, con deuda de 30.9 % a 0 % y plazo fijo de 40.0 % a 0 % (E de 4.9 % a 8.6 %, σ de 2.1 % a 11.0 %). En el conservador, el horizonte corto (H = 2, m_H = 1.5) sube λ_ef de 2 a 3, pero el portafolio ya está en su forma más prudente (deuda y plazo fijo en el tope): los pesos casi no cambian (mixtos 8.7 % → 8.6 %, bonos 11.3 % → 11.4 %). En el moderado (H = 5, pertenencia total a "mediano", m_H = 1) el difuso no cambia los pesos, que es el comportamiento esperado.

**Absorción en el cromosoma.** En los tres arquetipos la penalización de volatilidad nunca se activa: σ del portafolio (1.3 % a 11.0 %) queda por debajo de σ_max(c) (3.9 % a 15.3 %). La absorción solo aporta la recompensa κ·μ_CA(c), que eleva el fitness pero no cambia los pesos; el gen `c` se ubica en la meseta de máxima pertenencia de μ_CA (0.898 a 0.948 en moderado y agresivo; 0.068 a 0.072 en el conservador, por debajo de su centroide 0.157). El caso en que la absorción sí recorta el riesgo se analiza en [03 · Gen difuso](03-gen-difuso.md).

**Contexto.** El ajuste de contexto suma dos efectos: el panorama (político −0.5) y la tendencia de los datos (RC6, β_tend = 1.5 pp por unidad de `s_tend`). La tendencia favorece a los mixtos (`s_tend` = +1) y castiga a los bonos (−0.46), y con el panorama adverso las acciones pierden atractivo frente a los mixtos. En el agresivo completo las acciones bajan de 40.0 % (solo difuso) a 9.7 %, los mixtos suben de 20.0 % a 40.0 % y la deuda de 0 % a 40.0 % (E de 8.6 % a 6.7 %, σ de 11.0 % a 6.0 %). En los perfiles prudentes el contexto desplaza peso de bonos a mixtos: de 9.2 % a 12.9 % de mixtos en el moderado y de 8.7 % a 10.3 % en el conservador (base frente a solo contexto). El retorno esperado incluye esta corrección.

**Convergencia y estabilidad.** El AG converge en 46 a 146 generaciones de media y produce el mismo portafolio con las 10 semillas, lo que indica que el óptimo es estable para estos casos. El agresivo base es el más lento (145.6 ± 41.2; 2 semillas llegan al máximo de 200).

## Qué cambió con datos reales (W14)

| Arquetipo · configuración | Antes: acciones / mixtos / deuda / bonos / plazo fijo (%) | Con series del BCRP (%) |
|---|---|---|
| Conservador · base | 0.0 / 0.3 / 19.7 / 40.0 / 40.0 | 1.0 / 0.0 / 40.0 / 19.0 / 40.0 |
| Conservador · completo | 0.0 / 0.0 / 31.7 / 28.3 / 40.0 | 0.0 / 0.8 / 40.0 / 19.2 / 40.0 |
| Moderado · base | 1.7 / 4.8 / 13.5 / 40.0 / 40.0 | 2.0 / 0.0 / 40.0 / 18.0 / 40.0 |
| Moderado · completo | 0.8 / 2.8 / 16.4 / 40.0 / 40.0 | 1.5 / 0.0 / 40.0 / 18.5 / 40.0 |
| Agresivo · base | 9.9 / 10.1 / 0.0 / 40.0 / 40.0 | 4.6 / 0.0 / 40.0 / 15.4 / 40.0 |
| Agresivo · solo difuso | 40.0 / 20.0 / 0.0 / 40.0 / 0.0 | 40.0 / 0.0 / 0.0 / 40.0 / 20.0 |
| Agresivo · completo | 16.0 / 4.0 / 0.0 / 40.0 / 40.0 | 7.7 / 0.0 / 40.0 / 12.3 / 40.0 |

- **Deuda reemplaza a bonos en el tope.** Con datos, la deuda de corto plazo tiene μ 3.7 % y σ 0.6 % (Anexo A: 2.4 % y 2.5 %) y los bonos σ 6.5 % (Anexo A: 3.5 %). La deuda pasa a dominar la relación retorno/riesgo de los perfiles prudentes.
- **Menos retorno esperado y menos σ** en conservador y moderado (E 4.5–4.6 % frente a 4.1–5.2 %; σ 1.5–1.6 % frente a 1.6–1.9 %).
- **Los mixtos casi desaparecen** (antes hasta 20 %; ahora a lo sumo 0.8 %): el compuesto 0.5 × acciones + 0.5 × bonos es una combinación de dos categorías que el AG ya elige por separado.
- **Las conclusiones cualitativas se mantienen:** el horizonte domina en el agresivo, el contexto adverso reduce acciones, la absorción no actúa en los arquetipos estándar y el tope impone la diversificación.

## Qué cambió con el Fondo 2 de las AFP (W15)

Los mixtos dejaron de ser el compuesto 0.5 × acciones + 0.5 × bonos (μ 6.8 %, σ 12.3 %, correlación 0.97 con acciones) y pasaron a ser el valor cuota del Fondo 2 de las AFP publicado por la SBS (μ posterior 6.6 %, σ 7.6 %, correlación 0.72 con acciones y 0.44 con bonos).

| Arquetipo · configuración | W14 (compuesto): acciones / mixtos / deuda / bonos / plazo fijo (%) | W15 (Fondo 2 AFP) (%) |
|---|---|---|
| Conservador · base | 1.0 / 0.0 / 40.0 / 19.0 / 40.0 | 0.0 / 8.7 / 40.0 / 11.3 / 40.0 |
| Conservador · solo difuso | 0.6 / 0.0 / 40.0 / 19.4 / 40.0 | 0.0 / 8.6 / 40.0 / 11.4 / 40.0 |
| Conservador · solo contexto | 0.6 / 0.0 / 40.0 / 19.4 / 40.0 | 0.0 / 10.3 / 40.0 / 9.7 / 40.0 |
| Conservador · completo | 0.0 / 0.8 / 40.0 / 19.2 / 40.0 | 0.0 / 9.4 / 40.0 / 10.6 / 40.0 |
| Moderado · base | 2.0 / 0.0 / 40.0 / 18.0 / 40.0 | 0.0 / 9.2 / 40.0 / 10.8 / 40.0 |
| Moderado · solo difuso | 2.0 / 0.0 / 40.0 / 18.0 / 40.0 | 0.0 / 9.2 / 40.0 / 10.8 / 40.0 |
| Moderado · solo contexto | 1.5 / 0.0 / 40.0 / 18.5 / 40.0 | 0.0 / 12.9 / 40.0 / 7.1 / 40.0 |
| Moderado · completo | 1.5 / 0.0 / 40.0 / 18.5 / 40.0 | 0.0 / 12.9 / 40.0 / 7.1 / 40.0 |
| Agresivo · base | 4.6 / 0.0 / 40.0 / 15.4 / 40.0 | 3.7 / 8.3 / 30.9 / 17.0 / 40.0 |
| Agresivo · solo difuso | 40.0 / 0.0 / 0.0 / 40.0 / 20.0 | 40.0 / 20.0 / 0.0 / 40.0 / 0.0 |
| Agresivo · solo contexto | 3.8 / 0.0 / 40.0 / 16.2 / 40.0 | 0.0 / 19.9 / 40.0 / 0.1 / 40.0 |
| Agresivo · completo | 7.7 / 0.0 / 40.0 / 12.3 / 40.0 | 9.7 / 40.0 / 40.0 / 10.3 / 0.0 |

- **Los mixtos se eligen en las 12 celdas** (8.3 % a 40.0 %; antes a lo sumo 0.8 %). Con una correlación de 0.72 con acciones aportan diversificación propia y, con σ 7.6 %, son la forma más barata de tomar renta variable para los perfiles prudentes: sustituyen a las acciones (que quedan en 0 % en conservador y moderado) y a parte de los bonos.
- **El retorno esperado sube levemente y σ baja** en conservador y moderado (E 4.5–4.8 % frente a 4.5–4.6 %; σ 1.3–1.5 % frente a 1.5–1.6 %).
- **El agresivo completo cambia más**: con el contexto adverso pasa de 7.7 % acciones y 40.0 % plazo fijo a 9.7 % acciones, 40.0 % mixtos y 0 % plazo fijo (E de 5.0 % a 6.7 %, σ de 2.6 % a 6.0 %).
- **Las conclusiones cualitativas se mantienen:** el horizonte domina en el agresivo, el contexto adverso reduce acciones, la absorción no actúa en los arquetipos estándar y el tope impone la diversificación.

## Limitaciones observadas

- **Concentración por el tope.** En 8 de las 12 celdas (conservador, moderado y agresivo con solo contexto) deuda y plazo fijo quedan exactamente en el tope de 40 %; en el agresivo lo alcanzan acciones y bonos (solo difuso), mixtos y deuda (completo) o solo plazo fijo (base). El HHI se mantiene entre 0.293 y 0.360. La diversificación la impone el tope (decisión D2), no el modelo de riesgo: deuda (σ 0.6 %) y plazo fijo (σ 0.4 %) dominan la relación retorno/riesgo de los datos. Su σ es baja porque ambas series son tasas (la variación medida es la del nivel de tasa, no un riesgo de pérdida).
- **Mixtos aproximados por un fondo de pensiones.** Desde W15 la serie es el Fondo 2 de las AFP (SBS), no un fondo mutuo minorista: incluye cerca de 40–50 % de activos del exterior (su retorno en soles incluye el tipo de cambio) y no descuenta la comisión de la AFP (no verificado). Ver [análisis 09](../analisis/09-fuentes-de-datos.md).
- **El componente de absorción no mueve los pesos en estos arquetipos**: su efecto queda en `c` y en el fitness. Es un resultado honesto del diseño: la restricción difusa solo actúa cuando el perfil pide más volatilidad de la que la capacidad permite.
- **`c` atascado en una zona sin pertenencia (corregido).** En la primera versión del experimento, en el conservador con semilla 7 (solo difuso y completo), el AG terminó con c = 0.759 y μ_CA(c) = 0: μ_CA de absorción baja es 0 en todo [0.4, 1], esa región es plana para el fitness y la mutación de `c` (σ 0.10) no sacaba al gen de ahí antes de agotar la paciencia. Los pesos no cambiaban, pero el `c` mostrado no era representativo (desviación 0.246 en μ_CA(c) y 0.0074 en el fitness). Se corrigió de dos formas: con el difuso activo, los `c` iniciales se muestrean del conjunto de absorción (probabilidad proporcional a μ_CA en la rejilla) y la mutación de `c` usa su propio σ (`c_mutation_sigma` = 0.15 en `data/parameters/optimization.json`). Tras la corrección ninguna de las 600 corridas de los cuatro experimentos termina con μ_CA(c) = 0 (mínimo 0.5) y el conservador queda con μ_CA(c) = 0.778 en las 10 semillas; hay pruebas de regresión en `tests/unit/test_ga_algorithm.py`.
