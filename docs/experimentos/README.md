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
| Mercado | μ (acciones, mixtos, deuda, bonos, plazo fijo) = 12.8, 6.1, 2.4, 6.5, 4.5 %; σ = 22.0, 9.0, 2.5, 3.5, 0.5 % |

| Arquetipo | λ_base | Horizonte | Ahorro total | Fondo de emergencia | r | Absorción |
|---|---|---|---|---|---|---|
| Conservador | 2.0 | 2 años | S/ 12,000 | 1 mes | 0.83 | Baja (centroide 0.157) |
| Moderado | 1.0 | 5 años | S/ 40,000 | 4 meses | 0.25 | Media-alta (centroide 0.731) |
| Agresivo | 0.5 | 12 años | S/ 100,000 | 8 meses | 0.10 | Alta (centroide 0.853) |

## Hallazgos principales

1. **El horizonte difuso es el componente que más mueve los pesos.** En el agresivo (H = 12, m_H = 0.7) lleva acciones de 9.9 % a 40.0 %; en el conservador (H = 2, m_H = 1.5) pasa peso de bonos (−8.1 pp) a deuda (+8.4 pp). En el moderado (H = 5, m_H = 1) no cambia nada, como corresponde.
2. **El contexto adverso reduce la exposición a acciones** (agresivo completo: de 40.0 % a 16.0 % con político −0.5) y en el moderado, con ambos factores en −1, quita 2.9 pp a acciones y 5.7 pp a mixtos, que pasan a deuda (+8.6 pp).
3. **El gen `c` solo negocia contra la volatilidad cuando la absorción es baja y el perfil busca riesgo** (λ_base ≤ 0.5). Ahí la penalización baja σ de 10.1 % a 6.0 % (λ 0.2) y de 8.5 % a 5.6 % (λ 0.5). En el resto de casos `c` se queda en la meseta de máxima pertenencia y no afecta los pesos.
4. **κ y φ son poco sensibles en el rango probado; el tope sí importa.** Con tope 0.50 aparecen portafolios de dos categorías (agresivo 50/50, HHI 0.500). Se mantienen los valores por defecto.
5. **Debilidades** (detalladas en cada documento): el tope de 40 % se alcanza casi siempre en bonos y plazo fijo; la penalización difusa no actúa en los tres arquetipos estándar. En la primera versión, 2 de 60 corridas dejaban `c` en una zona con μ_CA = 0 (conservador, semilla 7); se corrigió muestreando los `c` iniciales de μ_CA y ampliando su mutación (σ 0.15), y ya no ocurre en ninguna de las 600 corridas.
