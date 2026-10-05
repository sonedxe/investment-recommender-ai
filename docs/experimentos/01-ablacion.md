# 01 · Ablación

## Método

- Cuatro configuraciones del modelo, con los interruptores de `recommend` (`Switches`):

| Configuración | Difuso | Contexto | Qué se apaga |
|---|---|---|---|
| Base | Off | Off | m_H = 1 (λ_ef = λ_base), sin penalización de volatilidad ni recompensa κ; sin ajuste de contexto |
| Solo difuso | On | Off | Sin ajuste de contexto (c_ctx = 0, σ' = σ) |
| Solo contexto | Off | On | Igual que la base en lo difuso |
| Completo | On | On | Nada |

- Pesos con el piso del 5 % y el tope del 40 % por categoría (decisión D2, W16).
- Tres arquetipos (conservador, moderado, agresivo; ver el [índice](README.md#configuración-común)) × 10 semillas = 120 corridas.
- Las configuraciones con contexto usan un panorama levemente adverso (político −0.5, macro 0) para que su efecto sea visible; la tendencia de mercado es la de los datos (acciones +1, mixtos +1, deuda +0.87, bonos −0.46, plazo fijo −0.18; desde W15 los mixtos son el valor cuota del Fondo 2 de las AFP, SBS).
- Métricas: pesos por categoría, retorno esperado E (incluye el ajuste de contexto), volatilidad σ, fitness, índice de Herfindahl (HHI = Σwᵢ²; 0.2 es reparto uniforme, 1 es una sola categoría), `c`, μ_CA(c), centroide, λ_ef y generaciones hasta converger.
- Datos: `experiments/results/ablation_runs.csv` y `ablation_summary.csv`.

## Resultados

Media ± desviación estándar entre semillas. Pesos, E y σ en %. Con el difuso apagado `c` no interviene en el fitness (su valor es aleatorio) y μ_CA(c) no aplica (n/d).

| Arquetipo | Configuración | Acciones | Mixtos | Deuda | Bonos | Plazo fijo | E | σ | Fitness | HHI | c | μ_CA(c) | Centroide | λ_ef | Gen. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Conservador | Base | 5.0 | 5.0 | 40.0 | 10.0 | 40.0 | 4.8 | 1.8 | 0.0113 | 0.335 | 0.512 ± 0.323 | n/d | 0.157 | 2.000 | 36.4 ± 2.5 |
| Conservador | Solo difuso | 5.0 | 5.0 | 40.0 | 10.0 | 40.0 | 4.8 | 1.8 | 0.0164 | 0.335 | 0.098 ± 0.060 | 0.778 | 0.157 | 3.000 | 37.7 ± 3.9 |
| Conservador | Solo contexto | 5.0 | 5.0 | 40.0 | 10.0 | 40.0 | 4.9 | 2.1 | 0.0065 | 0.335 | 0.480 ± 0.241 | n/d | 0.157 | 2.000 | 36.5 ± 2.8 |
| Conservador | Completo | 5.0 | 5.0 | 40.0 | 10.0 | 40.0 | 4.9 | 2.1 | 0.0084 | 0.335 | 0.109 ± 0.074 | 0.778 | 0.157 | 3.000 | 38.3 ± 4.5 |
| Moderado | Base | 5.0 | 5.0 | 40.0 | 10.0 | 40.0 | 4.8 | 1.8 | 0.0294 | 0.335 | 0.514 ± 0.283 | n/d | 0.731 | 1.000 | 36.5 ± 2.7 |
| Moderado | Solo difuso | 5.0 | 5.0 | 40.0 | 10.0 | 40.0 | 4.8 | 1.8 | 0.0444 | 0.335 | 0.846 ± 0.079 | 0.500 | 0.731 | 1.000 | 38.3 ± 3.6 |
| Moderado | Solo contexto | 5.0 | 6.1 | 40.0 | 8.9 | 40.0 | 5.0 | 2.2 | 0.0279 | 0.334 | 0.464 ± 0.252 | n/d | 0.731 | 1.000 | 45.8 ± 2.0 |
| Moderado | Completo | 5.0 | 6.1 | 40.0 | 8.9 | 40.0 | 5.0 | 2.2 | 0.0429 | 0.334 | 0.877 ± 0.052 | 0.500 | 0.731 | 1.000 | 45.2 ± 4.5 |
| Agresivo | Base | 5.0 | 8.8 | 25.5 | 20.7 | 40.0 | 5.1 | 2.6 | 0.0387 | 0.278 | 0.474 ± 0.242 | n/d | 0.853 | 0.500 | 86.5 ± 27.8 |
| Agresivo | Solo difuso | 39.2 | 10.8 | 5.0 | 40.0 | 5.0 | 8.3 | 10.3 | 0.0767 | 0.330 | 0.943 ± 0.031 | 1.000 | 0.853 | 0.350 | 53.3 ± 9.0 |
| Agresivo | Solo contexto | 5.0 | 17.3 | 40.0 | 5.0 | 32.7 | 5.3 | 2.8 | 0.0392 | 0.302 | 0.487 ± 0.195 | n/d | 0.853 | 0.500 | 61.5 ± 19.6 |
| Agresivo | Completo | 8.4 | 40.0 | 40.0 | 6.6 | 5.0 | 6.5 | 5.5 | 0.0761 | 0.334 | 0.923 ± 0.043 | 1.000 | 0.853 | 0.350 | 44.0 ± 3.1 |

Los pesos, E, σ, fitness y HHI tienen desviación prácticamente nula entre semillas: en los pesos es menor que 0.01 pp en 10 de las 12 celdas, 0.04 pp en el agresivo base y 0.05 pp en el agresivo con solo contexto; en el fitness, menor que 10⁻⁸. El AG converge al mismo portafolio con las 10 semillas, por eso se omite el ± en esas columnas. Las 120 corridas terminaron por convergencia (25 generaciones sin mejora).

![Pesos medios por configuración y arquetipo](../../experiments/results/fig_ablation_weights.png)

![Convergencia del AG, modelo completo, semilla 0](../../experiments/results/fig_convergence.png)

## Interpretación (para el informe, sección 9.x)

**Horizonte difuso.** Es el componente con mayor efecto sobre los pesos, y solo se ve en el agresivo. El horizonte largo (H = 12 años, m_H = 0.7) baja la aversión efectiva de 0.5 a 0.35 y el portafolio pasa de 5.0 % a 39.2 % en acciones y de 8.8 % a 10.8 % en mixtos, con deuda de 25.5 % a 5.0 % y plazo fijo de 40.0 % a 5.0 % (los dos quedan en el piso; E de 5.1 % a 8.3 %, σ de 2.6 % a 10.3 %). En el conservador, el horizonte corto (H = 2, m_H = 1.5) sube λ_ef de 2 a 3, pero el portafolio ya está en su forma más prudente (acciones y mixtos en el piso, deuda y plazo fijo en el tope): los pesos no cambian. En el moderado (H = 5, pertenencia total a "mediano", m_H = 1) el difuso no cambia los pesos, que es el comportamiento esperado.

**Absorción en el cromosoma.** En los tres arquetipos la penalización de volatilidad nunca se activa: σ del portafolio (1.8 % a 10.3 %) queda por debajo de σ_max(c) (4.3 % a 15.3 %). La absorción solo aporta la recompensa κ·μ_CA(c), que eleva el fitness pero no cambia los pesos; el gen `c` se ubica en la meseta de máxima pertenencia de μ_CA (0.846 a 0.943 en moderado y agresivo; 0.098 a 0.109 en el conservador, por debajo de su centroide 0.157). El caso en que la absorción sí recorta el riesgo se analiza en [03 · Gen difuso](03-gen-difuso.md).

**Contexto.** El ajuste de contexto suma dos efectos: el panorama (político −0.5) y la tendencia de los datos (RC6, β_tend = 1.5 pp por unidad de `s_tend`). La tendencia favorece a los mixtos (`s_tend` = +1) y castiga a los bonos (−0.46), y con el panorama adverso las acciones pierden atractivo frente a los mixtos. En el agresivo completo las acciones bajan de 39.2 % (solo difuso) a 8.4 %, los mixtos suben de 10.8 % a 40.0 % y la deuda de 5.0 % a 40.0 % (E de 8.3 % a 6.5 %, σ de 10.3 % a 5.5 %). En el moderado el contexto desplaza peso de bonos a mixtos (de 5.0 % a 6.1 % de mixtos, base frente a solo contexto); en el conservador los pesos no cambian, porque acciones y mixtos ya están en el piso y deuda y plazo fijo en el tope. El retorno esperado incluye esta corrección.

**Convergencia y estabilidad.** El AG converge en 36 a 87 generaciones de media y produce el mismo portafolio con las 10 semillas, lo que indica que el óptimo es estable para estos casos. El agresivo base es el más lento (86.5 ± 27.8), sin llegar al máximo de 200.

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

## Qué cambió con el piso del 5 % (W16)

Desde W16 cada categoría recibe entre 5 % y 40 % (decisión D2 ampliada). La tabla compara con los resultados de W15 (solo tope).

| Arquetipo · configuración | W15 (solo tope): acciones / mixtos / deuda / bonos / plazo fijo (%) | W16 (piso 5 % y tope 40 %) (%) | E (%) W15 → W16 | σ (%) W15 → W16 |
|---|---|---|---|---|
| Conservador · base | 0.0 / 8.7 / 40.0 / 11.3 / 40.0 | 5.0 / 5.0 / 40.0 / 10.0 / 40.0 | 4.5 → 4.8 | 1.3 → 1.8 |
| Conservador · completo | 0.0 / 9.4 / 40.0 / 10.6 / 40.0 | 5.0 / 5.0 / 40.0 / 10.0 / 40.0 | 4.7 → 4.9 | 1.4 → 2.1 |
| Moderado · base | 0.0 / 9.2 / 40.0 / 10.8 / 40.0 | 5.0 / 5.0 / 40.0 / 10.0 / 40.0 | 4.5 → 4.8 | 1.3 → 1.8 |
| Moderado · completo | 0.0 / 12.9 / 40.0 / 7.1 / 40.0 | 5.0 / 6.1 / 40.0 / 8.9 / 40.0 | 4.8 → 5.0 | 1.5 → 2.2 |
| Agresivo · base | 3.7 / 8.3 / 30.9 / 17.0 / 40.0 | 5.0 / 8.8 / 25.5 / 20.7 / 40.0 | 4.9 → 5.1 | 2.1 → 2.6 |
| Agresivo · solo difuso | 40.0 / 20.0 / 0.0 / 40.0 / 0.0 | 39.2 / 10.8 / 5.0 / 40.0 / 5.0 | 8.6 → 8.3 | 11.0 → 10.3 |
| Agresivo · solo contexto | 0.0 / 19.9 / 40.0 / 0.1 / 40.0 | 5.0 / 17.3 / 40.0 / 5.0 / 32.7 | 4.9 → 5.3 | 1.8 → 2.8 |
| Agresivo · completo | 9.7 / 40.0 / 40.0 / 10.3 / 0.0 | 8.4 / 40.0 / 40.0 / 6.6 / 5.0 | 6.7 → 6.5 | 6.0 → 5.5 |

- **Ninguna celda tiene categorías en 0 %** (antes, 11 de las 12 tenían al menos una). Todas tienen al menos una categoría en el piso: en los perfiles prudentes, acciones (y mixtos en conservador y moderado sin contexto); en el agresivo con horizonte largo, deuda y plazo fijo.
- **En los perfiles prudentes el piso agrega riesgo**: el 5 % obligatorio en acciones (σ 21.7 %) sube σ de 1.3–1.5 % a 1.8–2.2 % y, con él, el retorno esperado (+0.2 a +0.3 pp). En el agresivo con horizonte largo pasa lo contrario: el piso en deuda y plazo fijo baja σ (11.0 % → 10.3 %) y E (8.6 % → 8.3 %).
- **El fitness siempre baja** (el óptimo sin piso ya no es alcanzable): de 0.0188 a 0.0113 en el conservador base, de 0.0477 a 0.0429 en el moderado completo y de 0.0772 a 0.0767 en el agresivo solo difuso. El costo se mide aparte en [04 · Calibración](04-calibracion.md#qué-cambió-con-el-piso-del-5--w16).
- **El conservador y el moderado sin contexto quedan con el mismo portafolio** (5 / 5 / 40 / 10 / 40): con piso y tope activos en cuatro de las cinco categorías, solo los bonos quedan libres y absorben el resto. Los dos perfiles se distinguen en E y σ solo por el contexto, por λ_ef en el fitness y por `c`, no en los pesos.
- **Las conclusiones cualitativas se mantienen:** el horizonte domina en el agresivo, el contexto adverso reduce acciones, la absorción no actúa en los arquetipos estándar y la diversificación la imponen el tope y ahora también el piso.

## Limitaciones observadas

- **Concentración por el tope y el piso.** En 8 de las 12 celdas (conservador y moderado) deuda y plazo fijo quedan exactamente en el tope de 40 %; en el agresivo lo alcanzan bonos (solo difuso), mixtos y deuda (completo), solo deuda (solo contexto) o solo plazo fijo (base). Las 12 celdas tienen al menos una categoría en el piso del 5 %. El HHI se mantiene entre 0.278 y 0.335. La diversificación la imponen el tope y el piso (decisión D2), no el modelo de riesgo: deuda (σ 0.6 %) y plazo fijo (σ 0.4 %) dominan la relación retorno/riesgo de los datos. Su σ es baja porque ambas series son tasas (la variación medida es la del nivel de tasa, no un riesgo de pérdida).
- **Mixtos aproximados por un fondo de pensiones.** Desde W15 la serie es el Fondo 2 de las AFP (SBS), no un fondo mutuo minorista: incluye cerca de 40–50 % de activos del exterior (su retorno en soles incluye el tipo de cambio) y no descuenta la comisión de la AFP (no verificado). Ver [análisis 09](../analisis/09-fuentes-de-datos.md).
- **El componente de absorción no mueve los pesos en estos arquetipos**: su efecto queda en `c` y en el fitness. Es un resultado honesto del diseño: la restricción difusa solo actúa cuando el perfil pide más volatilidad de la que la capacidad permite.
- **`c` atascado en una zona sin pertenencia (corregido).** En la primera versión del experimento, en el conservador con semilla 7 (solo difuso y completo), el AG terminó con c = 0.759 y μ_CA(c) = 0: μ_CA de absorción baja es 0 en todo [0.4, 1], esa región es plana para el fitness y la mutación de `c` (σ 0.10) no sacaba al gen de ahí antes de agotar la paciencia. Los pesos no cambiaban, pero el `c` mostrado no era representativo (desviación 0.246 en μ_CA(c) y 0.0074 en el fitness). Se corrigió de dos formas: con el difuso activo, los `c` iniciales se muestrean del conjunto de absorción (probabilidad proporcional a μ_CA en la rejilla) y la mutación de `c` usa su propio σ (`c_mutation_sigma` = 0.15 en `data/parameters/optimization.json`). Tras la corrección ninguna de las corridas de los cuatro experimentos (660 desde W16) termina con μ_CA(c) = 0 (mínimo 0.5) y el conservador queda con μ_CA(c) = 0.778 en las 10 semillas; hay pruebas de regresión en `tests/unit/test_ga_algorithm.py`.
