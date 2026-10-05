# 02 · Escenarios de contexto

## Método

- Arquetipo moderado (λ_base 1.0, H = 5 años, r = 0.25, 4 meses de emergencia), modelo completo (difuso y contexto activos).
- Factor político ∈ {−1, 0, +1} × factor macroeconómico ∈ {−1, 0, +1}; tendencia de mercado según los datos.
- 10 semillas por escenario (90 corridas). Se reporta la media; la desviación de los pesos entre semillas es a lo sumo 0.1 pp.
- La columna Δ acciones compara con el escenario neutral (0, 0).
- Datos: `experiments/results/context_runs.csv` y `context_summary.csv`.

## Resultados

Pesos, E y σ en %.

| Político | Macro | Acciones | Mixtos | Deuda | Bonos | Plazo fijo | Δ acciones (pp) | E | σ | c |
|---|---|---|---|---|---|---|---|---|---|---|
| −1 | −1 | 0.0 | 0.1 | 19.9 | 40.0 | 40.0 | −2.9 | 3.9 | 2.1 | 0.892 |
| 0 | −1 | 1.2 | 3.6 | 15.2 | 40.0 | 40.0 | −1.7 | 4.7 | 2.0 | 0.922 |
| +1 | −1 | 1.8 | 6.5 | 11.7 | 40.0 | 40.0 | −1.1 | 5.5 | 2.2 | 0.898 |
| −1 | 0 | 0.0 | 1.1 | 18.9 | 40.0 | 40.0 | −2.9 | 4.4 | 2.0 | 0.897 |
| 0 | 0 | 2.9 | 5.8 | 11.3 | 40.0 | 40.0 | 0.0 | 5.4 | 2.1 | 0.913 |
| +1 | 0 | 3.5 | 10.2 | 6.3 | 40.0 | 40.0 | +0.6 | 6.3 | 2.4 | 0.926 |
| −1 | +1 | 0.0 | 1.6 | 18.4 | 40.0 | 40.0 | −2.9 | 4.8 | 2.0 | 0.897 |
| 0 | +1 | 3.3 | 7.0 | 9.6 | 40.0 | 40.0 | +0.4 | 6.0 | 2.2 | 0.912 |
| +1 | +1 | 3.2 | 11.6 | 5.2 | 40.0 | 40.0 | +0.3 | 6.8 | 2.4 | 0.917 |

![Pesos del perfil moderado según el contexto](../../experiments/results/fig_context_shift.png)

## Interpretación (para el informe, sección 9.x)

El contexto actúa como se diseñó en la base de reglas: un panorama adverso traslada peso de renta variable (acciones y fondos mixtos) a deuda de corto plazo, y uno favorable hace lo contrario. Del escenario más adverso (−1, −1) al más favorable (+1, +1), los fondos mixtos pasan de 0.1 % a 11.6 %, la deuda de 19.9 % a 5.2 % y el retorno esperado de 3.9 % a 6.8 %, mientras la volatilidad se mantiene entre 2.0 % y 2.4 %. El factor político pesa más que el macroeconómico, consistente con sus coeficientes (en acciones β_pol = 3 pp frente a β_mac = 1 pp, y γ_pol = 0.5 frente a γ_mac = 0.2): con político −1 las acciones desaparecen en los tres valores de macro.

## Limitaciones observadas

- **Magnitud acotada en el moderado.** Los cambios se concentran en el 20 % que queda libre después del tope: bonos y plazo fijo están en 40 % en los nueve escenarios. Para este perfil, el contexto redistribuye entre acciones, mixtos y deuda, pero no puede tocar el núcleo del portafolio. En el agresivo el efecto es mayor (ver [01 · Ablación](01-ablacion.md): acciones de 40.0 % a 16.0 % con político −0.5).
- **Asimetría.** Los escenarios favorables suben poco las acciones (+0.3 a +0.6 pp), porque el riesgo del moderado (λ_ef = 1) ya penaliza la volatilidad de acciones (22 %); el aumento va a fondos mixtos.
