# 02 · Escenarios de contexto

## Método

- Arquetipo moderado (λ_base 1.0, H = 5 años, r = 0.25, 4 meses de emergencia), modelo completo (difuso y contexto activos).
- Pesos con el piso del 5 % y el tope del 40 % por categoría (D2, W16).
- Factor político ∈ {−1, 0, +1} × factor macroeconómico ∈ {−1, 0, +1}; tendencia de mercado según los datos.
- 10 semillas por escenario (90 corridas). Se reporta la media; la desviación de los pesos entre semillas es menor que 0.01 pp.
- Las columnas Δ comparan con el escenario neutral (0, 0). Como acciones y mixtos se sustituyen entre sí, se reporta también Δ renta variable (acciones + mixtos).
- Datos: `experiments/results/context_runs.csv` y `context_summary.csv`.

## Resultados

Pesos, E y σ en %.

| Político | Macro | Acciones | Mixtos | Deuda | Bonos | Plazo fijo | Δ acciones (pp) | Δ renta variable (pp) | E | σ | c |
|---|---|---|---|---|---|---|---|---|---|---|---|
| −1 | −1 | 5.0 | 5.0 | 40.0 | 10.0 | 40.0 | 0.0 | −3.9 | 4.2 | 2.7 | 0.858 |
| 0 | −1 | 5.0 | 6.7 | 40.0 | 8.3 | 40.0 | 0.0 | −2.3 | 4.8 | 2.1 | 0.900 |
| +1 | −1 | 5.0 | 8.4 | 40.0 | 6.6 | 40.0 | 0.0 | −0.5 | 5.3 | 2.2 | 0.894 |
| −1 | 0 | 5.0 | 5.0 | 40.0 | 10.0 | 40.0 | 0.0 | −3.9 | 4.7 | 2.5 | 0.884 |
| 0 | 0 | 5.0 | 8.9 | 40.0 | 6.1 | 40.0 | 0.0 | 0.0 | 5.3 | 1.9 | 0.908 |
| +1 | 0 | 5.0 | 9.7 | 40.0 | 5.3 | 40.0 | 0.0 | +0.8 | 5.7 | 1.9 | 0.874 |
| −1 | +1 | 5.0 | 5.0 | 40.0 | 10.0 | 40.0 | 0.0 | −3.9 | 5.1 | 2.5 | 0.895 |
| 0 | +1 | 5.0 | 10.0 | 40.0 | 5.0 | 40.0 | 0.0 | +1.1 | 5.8 | 1.9 | 0.881 |
| +1 | +1 | 5.0 | 7.8 | 40.0 | 7.2 | 40.0 | 0.0 | −1.1 | 6.0 | 1.9 | 0.894 |

![Pesos del perfil moderado según el contexto](../../experiments/results/fig_context_shift.png)

## Interpretación (para el informe, sección 9.x)

El contexto actúa como se diseñó en la base de reglas: un panorama adverso reduce la renta variable y uno favorable la mantiene o la aumenta levemente. En el moderado, con el Fondo 2 de las AFP como serie de mixtos (W15) y el piso del 5 % (W16), las acciones quedan en el piso en los nueve escenarios, deuda y plazo fijo en el tope, y el contexto mueve los mixtos (8.9 % en el escenario neutral; renta variable 13.9 %). Con político −1 los mixtos bajan al piso (5.0 %) con cualquier factor macro (renta variable −3.9 pp) y su lugar lo toman los bonos. Con macro −1 la renta variable baja 0.5 a 3.9 pp según el factor político. El retorno esperado va de 4.2 % a 6.0 %, con volatilidad entre 1.9 % y 2.7 %. El factor político pesa más que el macroeconómico, consistente con sus coeficientes.

Los escenarios favorables suben poco la renta variable (+1.1 pp como máximo; (+1, +1) incluso baja 1.1 pp): el ajuste favorable también sube el μ de bonos, que compiten por el mismo 15 % libre (20 % que deja el tope, menos el 5 % fijo de acciones).

## Qué cambió con datos reales (W14)

- Antes (Anexo A + EPU) las acciones iban de 0 % a 3.5 % y la deuda absorbía los cambios (de 19.9 % a 5.2 %), con bonos y plazo fijo fijos en 40 %. Ahora deuda y plazo fijo están fijos en 40 % y los cambios se reparten entre acciones, mixtos y bonos.
- El rango de retorno esperado es menor (3.9 % a 5.7 %, antes 3.9 % a 6.8 %) y la volatilidad también (1.6 % a 1.9 %, antes 2.0 % a 2.4 %).

## Qué cambió con el Fondo 2 de las AFP (W15)

- Con el compuesto de W14 (correlación 0.97 con acciones) la renta variable del moderado era 1.6 % a 3.2 %, repartida entre acciones y algo de mixtos solo con político −1. Con el Fondo 2 (σ 7.6 %, correlación 0.72 con acciones) la renta variable es 10.6 % a 15.7 %, toda en mixtos, y los bonos bajan de 16.8–18.4 % a 4.3–9.4 %.
- El efecto del contexto es más visible: la diferencia entre el peor y el mejor escenario en renta variable es 5.1 pp (antes 1.6 pp). El retorno esperado sube (4.0 % a 5.8 %, antes 3.9 % a 5.7 %) y la volatilidad baja (1.4 % a 1.7 %, antes 1.6 % a 1.9 %).

## Qué cambió con el piso del 5 % (W16)

- Las acciones pasan de 0 % a 5.0 % en los nueve escenarios, y los mixtos y los bonos se reparten el 15 % que queda libre (antes 20 %). La renta variable (acciones + mixtos) es 10.0 % a 15.0 % (antes 10.6 % a 15.7 %).
- Con político −1 el piso de los mixtos se activa: el portafolio es el mismo con los tres factores macro (5 / 5 / 40 / 10 / 40) y el factor macro solo cambia E (4.2 % a 5.1 %). Antes los mixtos todavía variaban entre 10.6 % y 12.1 %.
- La diferencia entre el peor y el mejor escenario en renta variable se mantiene (5.0 pp, antes 5.1 pp). E sube 0.1 a 0.3 pp (4.2 % a 6.0 %, antes 4.0 % a 5.8 %) y σ sube 0.5 a 1.0 pp (1.9 % a 2.7 %, antes 1.4 % a 1.7 %) por el 5 % obligatorio en acciones.

## Limitaciones observadas

- **Magnitud acotada en el moderado.** Los cambios se concentran en el 15 % que queda libre después del tope y el piso: deuda y plazo fijo están en 40 % y acciones en 5 % en los nueve escenarios. Para este perfil, el contexto redistribuye entre mixtos y bonos, pero no puede tocar el núcleo del portafolio. En el agresivo el efecto es mayor (ver [01 · Ablación](01-ablacion.md): acciones de 39.2 % a 8.4 % con político −0.5).
- **Renta variable casi solo por mixtos en el moderado.** Con λ_ef = 1, la volatilidad de acciones (21.7 %) pesa demasiado frente a deuda y plazo fijo con σ menor a 1 %; la renta variable entra por mixtos (σ 7.6 %) y por el 5 % mínimo de acciones. Las acciones por encima del piso aparecen en el agresivo.
