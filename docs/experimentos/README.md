# Experimentos

Resultados de la fase F8: qué aporta cada componente del modelo y cómo se eligieron sus parámetros. Cada documento trae el método, la tabla, la figura y una interpretación lista para la sección 9.x del informe técnico.

| Documento | Pregunta que responde |
|---|---|
| [01 · Ablación](01-ablacion.md) | ¿Qué cambia al apagar el componente difuso, el de contexto o ambos? |
| [02 · Escenarios de contexto](02-contexto.md) | ¿Cuánto se mueve el portafolio con el panorama político y macroeconómico? |
| [03 · Gen difuso `c`](03-gen-difuso.md) | ¿Cuándo se separa `c` de la moda y del centroide, y cuándo negocia contra la volatilidad? |
| [04 · Calibración](04-calibracion.md) | ¿Son razonables κ = 0.03, φ = 50 y tope = 0.40? |

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
| Fitness | κ = 0.03, φ = 50, tope wᵢ ≤ 0.40, σ_max(c) = 0.03 + 0.13·c |
| Mercado (W14, series reales del BCRP) | μ posterior (acciones, mixtos, deuda, bonos, plazo fijo) = 11.9, 6.8, 3.7, 6.2, 4.4 %; σ = 21.7, 12.3, 0.6, 6.5, 0.4 %; `s_tend` = +1, +1, +0.87, −0.46, −0.18; mixtos = 0.5 × acciones + 0.5 × bonos; correlaciones estimadas (ver [análisis 09](../analisis/09-fuentes-de-datos.md) y `data/market/SOURCES.md`) |

| Arquetipo | λ_base | Horizonte | Ahorro total | Fondo de emergencia | r | Absorción |
|---|---|---|---|---|---|---|
| Conservador | 2.0 | 2 años | S/ 12,000 | 1 mes | 0.83 | Baja (centroide 0.157) |
| Moderado | 1.0 | 5 años | S/ 40,000 | 4 meses | 0.25 | Media-alta (centroide 0.731) |
| Agresivo | 0.5 | 12 años | S/ 100,000 | 8 meses | 0.10 | Alta (centroide 0.853) |

## Hallazgos principales

Resultados con datos reales del BCRP para las cinco categorías (W14, 2026-10-05). Antes de W14 solo acciones tenía datos (EPU en soles) y el resto usaba los valores del Anexo A con correlación supuesta 0.3; la sección [Qué cambió con datos reales](#qué-cambió-con-datos-reales-w14) resume la diferencia.

1. **El horizonte difuso sigue siendo el componente que más mueve los pesos, pero solo en el agresivo.** Con H = 12 (m_H = 0.7) lleva acciones de 4.6 % a 40.0 % (E de 4.7 % a 8.1 %, σ de 1.7 % a 9.8 %). En el conservador (m_H = 1.5) el efecto es casi nulo (acciones 1.0 % → 0.6 %), porque deuda y plazo fijo ya están en el tope; en el moderado (m_H = 1) no cambia nada, como corresponde.
2. **El contexto adverso reduce la exposición a renta variable.** En el agresivo, acciones bajan de 40.0 % (solo difuso) a 7.7 % en el modelo completo con político −0.5. En el moderado la exposición (acciones + mixtos) es 3.0 % en el escenario neutral y baja 0.6 a 1.4 pp con político −1, donde las acciones desaparecen y queda algo de mixtos.
3. **El gen `c` negocia contra la volatilidad cuando λ_base = 0.2 y la absorción es baja o media.** Con absorción baja σ baja de 14.1 % a 6.0 %; con absorción media, de 14.1 % a 11.2 %. Con λ_base ≥ 0.5 el perfil ya no pide más volatilidad de la permitida y `c` queda en la meseta.
4. **κ y φ no cambian ningún peso en los casos de calibración; el tope sí importa.** Con tope 0.50 el moderado queda prácticamente en dos categorías (deuda 50 %, plazo fijo 48.8 %, HHI 0.489). Se mantienen los valores por defecto.
5. **Debilidades** (detalladas en cada documento): deuda (σ 0.6 %) y plazo fijo (σ 0.4 %) quedan en el tope de 40 % en 11 de las 12 celdas de la ablación. Los fondos mixtos casi no se eligen (a lo sumo 2.4 %): al ser una mezcla fija de dos categorías que el AG ya puede combinar directamente (acciones y bonos), no aportan diversificación propia; solo entran cuando el ajuste de contexto los trata distinto. Ninguna de las 600 corridas termina con μ_CA(c) = 0 (mínimo 0.5).

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
