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
- Las configuraciones con contexto usan un panorama levemente adverso (político −0.5, macro 0) para que su efecto sea visible; la tendencia de mercado es la de los datos (acciones +1, resto 0).
- Métricas: pesos por categoría, retorno esperado E (incluye el ajuste de contexto), volatilidad σ, fitness, índice de Herfindahl (HHI = Σwᵢ²; 0.2 es reparto uniforme, 1 es una sola categoría), `c`, μ_CA(c), centroide, λ_ef y generaciones hasta converger.
- Datos: `experiments/results/ablation_runs.csv` y `ablation_summary.csv`.

## Resultados

Media ± desviación estándar entre semillas. Pesos, E y σ en %. Con el difuso apagado `c` no interviene en el fitness (su valor es aleatorio) y μ_CA(c) no aplica (n/d).

| Arquetipo | Configuración | Acciones | Mixtos | Deuda | Bonos | Plazo fijo | E | σ | Fitness | HHI | c | μ_CA(c) | Centroide | λ_ef | Gen. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Conservador | Base | 0.0 | 0.3 | 19.7 | 40.0 | 40.0 | 4.9 | 1.6 | 0.0161 | 0.359 | 0.474 ± 0.275 | n/d | 0.157 | 2.000 | 60.0 ± 13.9 |
| Conservador | Solo difuso | 0.0 | 0.0 | 28.1 | 31.9 | 40.0 | 4.5 | 1.5 | 0.0215 ± 0.0074 | 0.341 | 0.141 ± 0.223 | 0.700 ± 0.246 | 0.157 | 3.000 | 70.1 ± 12.9 |
| Conservador | Solo contexto | 0.0 | 0.0 | 23.0 | 37.0 | 40.0 | 4.5 | 1.7 | 0.0103 | 0.350 | 0.426 ± 0.252 | n/d | 0.157 | 2.000 | 65.1 ± 11.0 |
| Conservador | Completo | 0.0 | 0.0 | 31.7 | 28.3 | 40.0 | 4.1 | 1.6 | 0.0151 ± 0.0074 | 0.341 | 0.165 ± 0.214 | 0.700 ± 0.246 | 0.157 | 3.000 | 69.9 ± 11.9 |
| Moderado | Base | 1.7 | 4.8 | 13.5 | 40.0 | 40.0 | 5.2 | 1.9 | 0.0332 | 0.341 | 0.447 ± 0.201 | n/d | 0.731 | 1.000 | 87.9 ± 31.7 |
| Moderado | Solo difuso | 1.7 | 4.8 | 13.6 | 40.0 | 40.0 | 5.2 | 1.9 | 0.0482 | 0.341 | 0.904 ± 0.049 | 0.500 | 0.731 | 1.000 | 84.5 ± 23.0 |
| Moderado | Solo contexto | 0.8 | 2.8 | 16.4 | 40.0 | 40.0 | 4.8 | 1.9 | 0.0284 | 0.348 | 0.461 ± 0.172 | n/d | 0.731 | 1.000 | 79.4 ± 29.5 |
| Moderado | Completo | 0.8 | 2.8 | 16.4 | 40.0 | 40.0 | 4.8 | 1.9 | 0.0434 | 0.348 | 0.884 ± 0.066 | 0.500 | 0.731 | 1.000 | 92.5 ± 31.2 |
| Agresivo | Base | 9.9 | 10.1 | 0.0 | 40.0 | 40.0 | 6.3 | 3.4 | 0.0460 | 0.340 | 0.507 ± 0.136 | n/d | 0.853 | 0.500 | 47.6 ± 5.7 |
| Agresivo | Solo difuso | 40.0 | 20.0 | 0.0 | 40.0 | 0.0 | 8.9 | 10.1 | 0.0843 | 0.360 | 0.944 ± 0.032 | 1.000 | 0.853 | 0.350 | 48.0 ± 5.5 |
| Agresivo | Solo contexto | 7.3 | 12.7 | 0.0 | 40.0 | 40.0 | 5.8 | 3.6 | 0.0407 | 0.341 | 0.425 ± 0.104 | n/d | 0.853 | 0.500 | 49.4 ± 6.4 |
| Agresivo | Completo | 16.0 | 4.0 | 0.0 | 40.0 | 40.0 | 6.5 | 5.2 | 0.0768 | 0.347 | 0.961 ± 0.026 | 1.000 | 0.853 | 0.350 | 96.3 ± 15.1 |

Los pesos, E, σ y HHI tienen desviación 0.0 entre semillas en las 12 celdas (el AG converge al mismo portafolio con las 10 semillas); por eso se omite el ± en esas columnas. Todas las corridas terminaron por convergencia (25 generaciones sin mejora), antes del máximo de 200.

![Pesos medios por configuración y arquetipo](../../experiments/results/fig_ablation_weights.png)

![Convergencia del AG, modelo completo, semilla 0](../../experiments/results/fig_convergence.png)

## Interpretación (para el informe, sección 9.x)

**Horizonte difuso.** Es el componente con mayor efecto sobre los pesos. En el perfil agresivo, el horizonte largo (H = 12 años, m_H = 0.7) baja la aversión efectiva de 0.5 a 0.35 y el portafolio pasa de 9.9 % a 40.0 % en acciones (E de 6.3 % a 8.9 %, σ de 3.4 % a 10.1 %). En el conservador, el horizonte corto (H = 2, m_H = 1.5) sube λ_ef de 2 a 3 y desplaza peso de bonos (σ 3.5 %) a deuda (σ 2.5 %): σ baja de 1.6 % a 1.5 % a cambio de 0.4 pp de retorno. En el moderado (H = 5, pertenencia total a "mediano", m_H = 1) el difuso no cambia los pesos, que es el comportamiento esperado.

**Absorción en el cromosoma.** En los tres arquetipos la penalización de volatilidad nunca se activa: σ del portafolio (1.5 % a 10.1 %) queda por debajo de σ_max(c) (4.8 % a 15.5 %). La absorción solo aporta la recompensa κ·μ_CA(c), que eleva el fitness pero no cambia los pesos; el gen `c` se ubica en la meseta de máxima pertenencia de μ_CA (por ejemplo 0.884 a 0.961 en moderado y agresivo, por encima del centroide). El caso en que la absorción sí recorta el riesgo se analiza en [03 · Gen difuso](03-gen-difuso.md).

**Contexto.** Con un panorama político levemente adverso (−0.5), el contexto reduce la renta variable: en el agresivo completo las acciones bajan de 40.0 % a 16.0 % y el plazo fijo sube de 0 % a 40.0 % frente a "solo difuso"; en el conservador, bonos cede peso a deuda (37.0 % y 23.0 % frente a 40.0 % y 19.7 % de la base). El retorno esperado incluye la corrección de contexto, por eso E baja en todas las configuraciones con contexto.

**Convergencia y estabilidad.** El AG converge en 48 a 96 generaciones de media y produce el mismo portafolio con las 10 semillas, lo que indica que el óptimo es estable para estos casos.

## Limitaciones observadas

- **Concentración por el tope.** En 9 de las 12 celdas dos categorías quedan exactamente en el tope de 40 % (bonos y plazo fijo, o acciones y bonos en el agresivo con solo difuso) y en las 3 restantes (conservador con difuso o contexto) lo alcanza el plazo fijo; el HHI se mantiene entre 0.340 y 0.360 en todas las configuraciones. La diversificación la impone el tope (decisión D2), no el modelo de riesgo: el plazo fijo (σ 0.5 %) y los bonos dominan la relación retorno/riesgo de los datos actuales.
- **El componente de absorción no mueve los pesos en estos arquetipos**: su efecto queda en `c` y en el fitness. Es un resultado honesto del diseño: la restricción difusa solo actúa cuando el perfil pide más volatilidad de la que la capacidad permite.
- **`c` atascado en una zona sin pertenencia.** En el conservador, semilla 7 (solo difuso y completo), el AG terminó con c = 0.759 y μ_CA(c) = 0: μ_CA de absorción baja es 0 en todo [0.4, 1], esa región es plana para el fitness y la mutación (σ 0.05) no saca al gen de ahí antes de agotar la paciencia. Los pesos no cambian (la penalización tampoco está activa), pero el `c` que se mostraría al usuario no es representativo. Es la causa de la desviación 0.246 en μ_CA(c) y 0.0074 en el fitness. Mejoras posibles (no aplicadas): inicializar `c` cerca del centroide o usar una mutación más amplia para el gen `c`.
