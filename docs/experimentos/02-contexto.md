# 02 · Escenarios de contexto

## Método

- Arquetipo moderado (λ_base 1.0, H = 5 años, r = 0.25, 4 meses de emergencia), modelo completo (difuso y contexto activos).
- Factor político ∈ {−1, 0, +1} × factor macroeconómico ∈ {−1, 0, +1}; tendencia de mercado según los datos.
- 10 semillas por escenario (90 corridas). Se reporta la media; la desviación de los pesos entre semillas es menor que 0.01 pp.
- Las columnas Δ comparan con el escenario neutral (0, 0). Como acciones y mixtos se sustituyen entre sí, se reporta también Δ renta variable (acciones + mixtos).
- Datos: `experiments/results/context_runs.csv` y `context_summary.csv`.

## Resultados

Pesos, E y σ en %.

| Político | Macro | Acciones | Mixtos | Deuda | Bonos | Plazo fijo | Δ acciones (pp) | Δ renta variable (pp) | E | σ | c |
|---|---|---|---|---|---|---|---|---|---|---|---|
| −1 | −1 | 0.0 | 1.6 | 40.0 | 18.4 | 40.0 | −3.0 | −1.4 | 3.9 | 1.9 | 0.888 |
| 0 | −1 | 1.9 | 0.0 | 40.0 | 18.1 | 40.0 | −1.1 | −1.1 | 4.4 | 1.7 | 0.884 |
| +1 | −1 | 2.2 | 0.0 | 40.0 | 17.8 | 40.0 | −0.8 | −0.8 | 4.8 | 1.7 | 0.901 |
| −1 | 0 | 0.0 | 2.1 | 40.0 | 17.9 | 40.0 | −3.0 | −0.9 | 4.3 | 1.7 | 0.874 |
| 0 | 0 | 3.0 | 0.0 | 40.0 | 17.0 | 40.0 | 0.0 | 0.0 | 4.9 | 1.6 | 0.907 |
| +1 | 0 | 3.0 | 0.0 | 40.0 | 17.0 | 40.0 | 0.0 | 0.0 | 5.3 | 1.6 | 0.894 |
| −1 | +1 | 0.0 | 2.4 | 40.0 | 17.6 | 40.0 | −3.0 | −0.6 | 4.7 | 1.7 | 0.893 |
| 0 | +1 | 3.2 | 0.0 | 40.0 | 16.8 | 40.0 | +0.2 | +0.2 | 5.4 | 1.6 | 0.904 |
| +1 | +1 | 2.8 | 0.0 | 40.0 | 17.2 | 40.0 | −0.2 | −0.2 | 5.7 | 1.6 | 0.902 |

![Pesos del perfil moderado según el contexto](../../experiments/results/fig_context_shift.png)

## Interpretación (para el informe, sección 9.x)

El contexto actúa como se diseñó en la base de reglas: un panorama adverso reduce la renta variable y uno favorable la mantiene o la aumenta levemente. En el moderado, con datos reales, la renta variable es pequeña (3.0 % en el escenario neutral) y deuda y plazo fijo están en el tope. Con político −1 las acciones desaparecen en los tres valores de macro y en su lugar entra algo de fondos mixtos (1.6 % a 2.4 %): la penalización política de acciones (β_pol = 3 pp, γ_pol = 0.5) es el doble que la de mixtos (1.5 pp, 0.25), así que la renta variable baja 0.6 a 1.4 pp y se desplaza hacia la forma más diversificada. El retorno esperado va de 3.9 % a 5.7 %, con volatilidad entre 1.6 % y 1.9 %. El factor político pesa más que el macroeconómico, consistente con sus coeficientes.

Los escenarios favorables casi no suben la renta variable (+0.2 pp como máximo; (+1, +1) incluso baja 0.2 pp): el ajuste favorable también sube el μ de bonos, que compiten por el mismo 20 % libre.

## Qué cambió con datos reales (W14)

- Antes (Anexo A + EPU) las acciones iban de 0 % a 3.5 % y la deuda absorbía los cambios (de 19.9 % a 5.2 %), con bonos y plazo fijo fijos en 40 %. Ahora deuda y plazo fijo están fijos en 40 % y los cambios se reparten entre acciones, mixtos y bonos.
- El rango de retorno esperado es menor (3.9 % a 5.7 %, antes 3.9 % a 6.8 %) y la volatilidad también (1.6 % a 1.9 %, antes 2.0 % a 2.4 %).

## Limitaciones observadas

- **Magnitud acotada en el moderado.** Los cambios se concentran en el 20 % que queda libre después del tope: deuda y plazo fijo están en 40 % en los nueve escenarios. Para este perfil, el contexto redistribuye entre acciones, mixtos y bonos, pero no puede tocar el núcleo del portafolio. En el agresivo el efecto es mayor (ver [01 · Ablación](01-ablacion.md): acciones de 40.0 % a 7.7 % con político −0.5).
- **Poca renta variable en el moderado.** Con λ_ef = 1, la volatilidad de acciones (21.7 %) y de mixtos (12.3 %, correlación 0.97 con acciones) pesa demasiado frente a deuda y plazo fijo con σ menor a 1 %.
