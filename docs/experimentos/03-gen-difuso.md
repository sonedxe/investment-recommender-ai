# 03 · Gen difuso `c`

## Qué se quiere mostrar

El cromosoma es `[w₁…w₅ | c]`. El gen `c` es la capacidad de absorber pérdidas que el AG "elige" dentro del conjunto difuso μ_CA del usuario (salida Mamdani sin desfuzzificar). El fitness lo usa dos veces:

- **Recompensa:** `+κ·μ_CA(c)`, que empuja `c` hacia donde μ_CA es máxima.
- **Restricción blanda:** `−φ·max(0, σ − σ_max(c))²` con `σ_max(c) = 0.03 + 0.13·c`, que permite más volatilidad cuanto mayor es `c`.

`c` solo "negocia" cuando el portafolio que el perfil desea tiene una volatilidad mayor que la que permite la zona de máxima pertenencia. Este experimento busca esos casos.

## Método

- Tres situaciones de absorción (monto S/ 10,000):

| Absorción | Ahorro total | Emergencia | r | Regla activa | Meseta de μ_CA máxima | Moda | Centroide |
|---|---|---|---|---|---|---|---|
| Baja | S/ 12,000 | 1 mes | 0.83 | RA5 → Baja (0.778) | [0, 0.206] | 0.103 | 0.157 |
| Media | S/ 20,000 | 4 meses | 0.50 | RA4 → Media (0.5) | [0.375, 0.625] | 0.500 | 0.500 |
| Alta | S/ 100,000 | 8 meses | 0.10 | RA2 → Alta (1.0) | [0.85, 1] | 0.925 | 0.853 |

- λ_base ∈ {0.2, 0.5, 1, 2} con H = 5 años (m_H = 1, así λ_ef = λ_base) y contexto neutral (0, 0). Modelo completo, 10 semillas: 120 corridas.
- Para cada caso se corre además el AG sin penalización ni recompensa (mismo λ_ef): "σ sin penalización" es la volatilidad que el perfil elegiría si la absorción no existiera.
- "Moda" es el centro de la meseta de máxima pertenencia. "Penalización activa" es el porcentaje de semillas con término de penalización distinto de 0; "Restricción activa", el porcentaje con σ ≥ σ_max(c) − 0.2 pp.
- Datos: `experiments/results/gene_runs.csv` y `gene_summary.csv`.

## Resultados

| Absorción | λ_base | c | μ_CA(c) | σ % | σ_max(c) % | σ sin penalización % | Penalización activa | Restricción activa |
|---|---|---|---|---|---|---|---|---|
| Baja | 0.2 | 0.205 ± 0.000 | 0.778 | 6.0 | 5.7 | 10.1 | 100 % | 100 % |
| Baja | 0.5 | 0.203 ± 0.002 | 0.778 | 5.6 | 5.6 | 8.5 | 70 % | 100 % |
| Baja | 1 | 0.082 ± 0.035 | 0.778 | 2.1 | 4.1 | 2.1 | 0 % | 0 % |
| Baja | 2 | 0.086 ± 0.054 | 0.778 | 1.6 | 4.1 | 1.6 | 0 % | 0 % |
| Media | 0.2 | 0.569 ± 0.015 | 0.500 | 10.1 | 10.4 | 10.1 | 0 % | 30 % |
| Media | 0.5 | 0.523 ± 0.038 | 0.500 | 8.5 | 9.8 | 8.5 | 0 % | 0 % |
| Media | 1 | 0.502 ± 0.026 | 0.500 | 2.1 | 9.5 | 2.1 | 0 % | 0 % |
| Media | 2 | 0.501 ± 0.055 | 0.500 | 1.6 | 9.5 | 1.6 | 0 % | 0 % |
| Alta | 0.2 | 0.947 ± 0.028 | 1.000 | 10.1 | 15.3 | 10.1 | 0 % | 0 % |
| Alta | 0.5 | 0.947 ± 0.030 | 1.000 | 8.5 | 15.3 | 8.5 | 0 % | 0 % |
| Alta | 1 | 0.947 ± 0.039 | 1.000 | 2.1 | 15.3 | 2.1 | 0 % | 0 % |
| Alta | 2 | 0.941 ± 0.044 | 1.000 | 1.6 | 15.2 | 1.6 | 0 % | 0 % |

![c evolucionado frente a moda y centroide (arriba) y volatilidades (abajo)](../../experiments/results/fig_gene_c.png)

## Interpretación (para el informe, sección 9.x)

**Cuándo `c` se separa de la moda y del centroide.** La agregación Mamdani recorta cada conjunto de salida a la fuerza de su regla, así que μ_CA tiene una meseta de pertenencia máxima. Dentro de ella la recompensa κ·μ_CA(c) es constante y `c` puede moverse sin costo. Por eso:

- Cuando la volatilidad deseada cabe con holgura (λ_base ≥ 1 en todos los niveles, y cualquier λ con absorción alta), `c` queda en cualquier punto de la meseta: su media cae cerca de la moda (0.08–0.09 en baja, 0.50 en media, 0.94–0.95 en alta) con dispersión de 0.03 a 0.06 entre semillas, y no coincide con el centroide (que pondera también los bordes inclinados del conjunto).
- Cuando el perfil quiere más volatilidad, `c` sube hasta donde haga falta **dentro** de la meseta: con absorción media y λ = 0.2 se desplaza a 0.569 (σ_max 10.4 % frente a σ 10.1 %) sin perder pertenencia.

**Cuándo el gen negocia (trade-off real).** Solo ocurre cuando la volatilidad que el perfil elegiría sin restricción supera σ_max en el borde derecho de la meseta. Con absorción baja ese borde es c = 0.206, es decir σ_max = 5.7 %. Los perfiles agresivos (λ 0.2 y 0.5) querrían 10.1 % y 8.5 %:

- `c` se queda en el borde de la meseta (0.205 y 0.203), sin bajar μ_CA(c) de 0.778. Más allá, cada unidad de `c` cuesta κ·4 = 0.12 de recompensa (la pendiente del conjunto Baja es 4) y solo ahorra 2·φ·0.13·(σ − σ_max) ≈ 13·(σ − σ_max) de penalización; con un exceso de 0.3 pp el ahorro (≈ 0.04) es menor que el costo.
- Lo que cede es el portafolio: σ baja de 10.1 % a 6.0 % (λ 0.2) y de 8.5 % a 5.6 % (λ 0.5). Con λ 0.2 el AG acepta un pequeño exceso sobre σ_max (6.0 % frente a 5.7 %) porque el retorno adicional compensa la penalización cuadrática.

En palabras simples: la capacidad de absorber pérdidas actúa como un límite flexible a la volatilidad. Si la persona puede asumir pérdidas, el límite no molesta. Si no puede, pero su perfil le pide arriesgar, el algoritmo busca el punto más alto de capacidad que sus datos todavía respaldan y recorta el riesgo hasta ese nivel, en lugar de suponer una capacidad que no tiene.

## Limitaciones observadas

- El efecto del gen depende de los parámetros de σ_max(c) (0.03 y 0.13): con ellos, absorción media o alta nunca restringe portafolios del universo actual (la σ máxima alcanzable con tope 40 % es ≈ 10.7 %, calculada sobre una rejilla de pesos con paso 5 %, frente a σ_max = 11.1 % en el borde de la meseta media). Solo la absorción baja es restrictiva.
- La meseta hace que `c` no esté determinado de forma única cuando la restricción no actúa (dispersión 0.03–0.06). Para la explicación al usuario conviene seguir mostrando el centroide junto al `c` evolucionado.
