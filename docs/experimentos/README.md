# Experimentos

Resultados de la fase F8: qué aporta cada componente del modelo y cómo se eligieron sus parámetros. Cada documento trae el método, la tabla, la figura y una interpretación lista para la sección 9.x del informe técnico.

| Documento | Pregunta que responde |
|---|---|
| [01 · Ablación](01-ablacion.md) | ¿Qué cambia al apagar el componente difuso, el de contexto o ambos? |
| [02 · Escenarios de contexto](02-contexto.md) | ¿Cuánto se mueve el portafolio con el panorama político y macroeconómico? |
| [03 · Gen difuso `c`](03-gen-difuso.md) | ¿Cuándo se separa `c` de la moda y del centroide, y cuándo negocia contra la volatilidad? |
| [04 · Calibración](04-calibracion.md) | ¿Son razonables κ = 0.03, φ = 50, tope = 0.40 y piso = 0.05? ¿Cuánto cuesta el piso? |

## Cómo reproducir

```bash
pip install -r requirements-experiments.txt   # matplotlib, solo para las figuras
python experiments/ablation.py                  # ~25 s; escribe en experiments/results/
python experiments/ablation.py --no-plots       # sin matplotlib
```

- El script ejecuta las etapas 3 a 6 del flujo real (estimaciones bayesianas → horizonte → absorción → contexto → AG) con los módulos de `ai/` y los parámetros de `data/parameters/`. No llama al modelo de lenguaje.
- Cada corrida usa semillas 0 a 9; los CSV son idénticos entre ejecuciones (verificado comparando dos corridas byte a byte).
- Tablas completas, CSV por corrida y figuras: [`experiments/results/`](../../experiments/results/README.md).

## Configuración común

| Elemento | Valor |
|---|---|
| Monto | S/ 10,000 |
| AG | población 80, máximo 200 generaciones, paciencia 25, torneo 3, cruce 0.9, mutación 0.1 (σ 0.05 en los pesos, 0.15 en `c`), elitismo 1; con el difuso activo, `c` inicial muestreado de μ_CA |
| Fitness | κ = 0.03, φ = 50, piso y tope 0.05 ≤ wᵢ ≤ 0.40 (desde W16), σ_max(c) = 0.03 + 0.13·c |
| Mercado (W14 series reales del BCRP; W15 mixtos de la SBS) | μ posterior (acciones, mixtos, deuda, bonos, plazo fijo) = 11.9, 6.6, 3.7, 6.2, 4.4 %; σ = 21.7, 7.6, 0.6, 6.5, 0.4 %; `s_tend` = +1, +1, +0.87, −0.46, −0.18; mixtos = valor cuota del Fondo 2 de las AFP (promedio Integra, Prima, Profuturo); correlaciones estimadas (ver [análisis 09](../analisis/09-fuentes-de-datos.md) y `data/market/SOURCES.md`) |

| Arquetipo | λ_base | Horizonte | Ahorro total | Fondo de emergencia | r | Absorción |
|---|---|---|---|---|---|---|
| Conservador | 2.0 | 2 años | S/ 12,000 | 1 mes | 0.83 | Baja (centroide 0.157) |
| Moderado | 1.0 | 5 años | S/ 40,000 | 4 meses | 0.25 | Media-alta (centroide 0.731) |
| Agresivo | 0.5 | 12 años | S/ 100,000 | 8 meses | 0.10 | Alta (centroide 0.853) |

## Hallazgos principales

Resultados con datos reales para las cinco categorías: series del BCRP (W14) y, para los fondos mixtos, el valor cuota del Fondo 2 de las AFP publicado por la SBS (W15, 2026-10-05). Antes de W14 solo acciones tenía datos (EPU en soles) y el resto usaba los valores del Anexo A con correlación supuesta 0.3; las secciones [Qué cambió con datos reales](#qué-cambió-con-datos-reales-w14) y [Qué cambió con el Fondo 2 de las AFP](#qué-cambió-con-el-fondo-2-de-las-afp-w15) resumen las diferencias.

1. **El horizonte difuso sigue siendo el componente que más mueve los pesos, pero solo en el agresivo.** Con H = 12 (m_H = 0.7) lleva acciones de 5.0 % a 39.2 % y deja deuda y plazo fijo en el piso (E de 5.1 % a 8.3 %, σ de 2.6 % a 10.3 %). En el conservador (m_H = 1.5) los pesos no cambian, porque acciones y mixtos ya están en el piso y deuda y plazo fijo en el tope; en el moderado (m_H = 1) no cambia nada, como corresponde.
2. **El contexto adverso reduce la exposición a acciones.** En el agresivo, acciones bajan de 39.2 % (solo difuso) a 8.4 % en el modelo completo con político −0.5, y los mixtos suben a 40.0 %. En el moderado las acciones quedan en el piso y la renta variable se mueve por los mixtos (8.9 % en el escenario neutral); con político −1 los mixtos bajan al piso (renta variable −3.9 pp).
3. **El gen `c` negocia contra la volatilidad cuando el perfil pide más riesgo del que la absorción permite.** Con λ_base = 0.2 y absorción baja σ baja de 11.3 % a 5.9 %; con absorción media, de 11.3 % a 11.2 %. Con λ_base = 0.5 y absorción baja `c` se mueve cerca del borde de la meseta (0.169) para admitir σ 5.0 % sin penalización. Con λ_base ≥ 1 `c` queda en cualquier punto de la meseta.
4. **κ y φ no cambian ningún peso en los casos de calibración; el tope sí importa y el piso cuesta poco.** Con tope 0.50 el moderado concentra 85 % en deuda y plazo fijo (HHI 0.380) y el agresivo 85 % en acciones y mixtos (HHI 0.380). El piso del 5 % baja el fitness entre 0.0002 y 0.0026 y cambia E entre −0.23 y +0.24 pp. Se mantienen los valores por defecto.
5. **Debilidades** (detalladas en cada documento): deuda (σ 0.6 %) y plazo fijo (σ 0.4 %) quedan en el tope de 40 % en 8 de las 12 celdas de la ablación, y con el piso el conservador y el moderado sin contexto reciben el mismo portafolio (5 / 5 / 40 / 10 / 40). Los fondos mixtos se aproximan con un fondo de pensiones (Fondo 2 de las AFP), no con un fondo mutuo minorista: su retorno en soles incluye el efecto del tipo de cambio y no descuenta la comisión de la AFP (no verificado). Ninguna de las 660 corridas termina con μ_CA(c) = 0 (mínimo 0.5).

## Qué cambió con datos reales (W14)

| Elemento | Antes (Anexo A + EPU) | Con series del BCRP |
|---|---|---|
| Deuda: μ / σ | 2.4 % / 2.5 % (Anexo A) | 3.7 % / 0.6 % (saldo CD BCRP) |
| Bonos: μ / σ | 6.5 % / 3.5 % (Anexo A) | 6.2 % / 6.5 % (BTP 10 años, D = 7) |
| Mixtos: μ / σ | 6.1 % / 9.0 % (Anexo A) | 6.8 % / 12.3 % (compuesto 0.5 acciones + 0.5 bonos) |
| Plazo fijo: μ / σ | 4.5 % / 0.5 % (Anexo A) | 4.4 % / 0.4 % (tasa pasiva 181–360 días) |
| Acciones: μ / σ | 12.8 % / 22.0 % (EPU en soles) | 11.9 % / 21.7 % (Índice General BVL) |
| Correlaciones | 0.3 supuesta (0 con plazo fijo) | Estimadas con los meses comunes de cada par: acciones–mixtos 0.97, deuda–plazo fijo 0.88, mixtos–bonos 0.54, acciones–bonos 0.31, bonos–plazo fijo 0.24, deuda–bonos 0.22, mixtos–plazo fijo 0.10, resto ≤ 0.08 (reparación PSD mínima: autovalor −1.5·10⁻⁷) |
| Categoría en el tope | Bonos y plazo fijo | Deuda y plazo fijo |
| Bonos en la ablación | 28.3 % a 40.0 % | 12.3 % a 40.0 % (40.0 % solo en agresivo con solo difuso) |

Con σ real del BTP (6.5 % frente a 3.5 % supuesto) los bonos dejan de dominar la relación retorno/riesgo, y la deuda de corto plazo, con más retorno y menos riesgo que en el Anexo A, ocupa su lugar en el tope.

Composición de los mixtos: una primera versión de W14 usaba 0.5 × acciones + 0.5 × deuda, que resultó una copia escalada de acciones (correlación 0.9996). Se cambió a acciones + bonos porque los fondos mixtos peruanos combinan renta variable y bonos; la correlación con acciones baja a 0.97 (la σ de acciones domina la mezcla) y la correlación con bonos sube a 0.54.

## Qué cambió con el Fondo 2 de las AFP (W15)

| Elemento | W14 (compuesto 0.5 acciones + 0.5 bonos) | W15 (Fondo 2 de las AFP, SBS) |
|---|---|---|
| Mixtos: μ posterior / σ | 6.8 % / 12.3 % | 6.6 % / 7.6 % (dato: μ 7.1 %, 199 retornos 2010-02 a 2026-08) |
| Correlación mixtos–acciones | 0.97 | 0.72 |
| Correlación mixtos–bonos | 0.54 | 0.44 |
| Correlación mixtos–deuda / plazo fijo | 0.08 / 0.10 | 0.03 / 0.02 |
| Reparación PSD | Mínima (autovalor −1.5·10⁻⁷) | No hace falta |
| Mixtos en la ablación | 0 % a 0.8 % | 8.3 % a 40.0 % |
| Acciones en conservador y moderado | 0.0 % a 2.0 % | 0 % |

El compuesto era casi redundante con acciones y bonos, así que el AG no lo elegía. El Fondo 2 es una serie independiente con correlación moderada con acciones y menos σ que el compuesto: pasa a ser la vía principal de renta variable en los perfiles prudentes y comparte el tope con acciones en el agresivo. Las conclusiones cualitativas (horizonte, contexto, gen `c`, calibración) se mantienen.

## Qué cambió con el piso del 5 % (W16)

Desde W16 cada categoría recibe entre 5 % y 40 % (decisión D2 ampliada, [análisis 10](../analisis/10-decisiones-d1-d2-d5.md#ampliación-w16-tope-40--y-piso-5-)). El piso fija 25 % del portafolio y el AG decide el 75 % restante.

| Elemento | W15 (solo tope) | W16 (piso 5 % y tope 40 %) |
|---|---|---|
| Celdas de la ablación con alguna categoría en 0 % | 11 de 12 | 0 de 12 |
| Acciones en conservador y moderado | 0 % | 5 % (en el piso) |
| σ en conservador y moderado (ablación) | 1.3 % a 1.5 % | 1.8 % a 2.2 % |
| σ máxima pedida (λ_base = 0.2) | 11.6 % | 11.3 % |
| Costo del piso en la calibración (fitness) | — | −0.0002 a −0.0026 |
| Corridas | 600 | 660 (barrido del piso) |

El piso agrega riesgo en los perfiles prudentes (5 % obligatorio en acciones) y lo quita en el agresivo con horizonte largo (5 % obligatorio en deuda y plazo fijo). Las conclusiones cualitativas (horizonte, contexto, gen `c`, calibración) se mantienen.
