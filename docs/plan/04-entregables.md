# 04 · Entregables

Exigidos por el enunciado: manual de instalación, manual de usuario, informe técnico y código fuente completo, más la exposición en la semana 7.

## Manual de instalación — `docs/manuales/instalacion.md`

- Requisitos (Python, Node, versiones).
- Backend: entorno virtual, dependencias, `.env` (API key opcional, modo offline).
- Frontend: `npm install`, `npm run dev`.
- Verificación: `/health`, `pytest`, primera recomendación de prueba.
- Problemas frecuentes (puertos, CORS, API key inválida).

## Manual de usuario — `docs/manuales/usuario.md`

- Qué hace y qué **no** hace la aplicación (aviso educativo).
- Cómo describir la situación en texto libre, con ejemplos.
- Cómo responder las preguntas de aclaración.
- Cómo leer el resultado: montos, escenarios, explicación.
- Panel de contexto: qué significa cada factor.
- Detalle técnico: para quién es y qué muestra.
- Capturas de cada pantalla.

## Informe técnico final (v2.0)

Partir de la v1.1 y cambiar:

| Sección | Cambio |
|---|---|
| Resumen de cambios | Nueva versión 2.0 |
| 4.4 AG | Cromosoma `[w \| c]`, término por convergencia, justificación del torneo (fitness negativo) y del cruce aritmético |
| 4.5 Lógica difusa | Horizonte → fitness (Sugeno); absorción → cromosoma (Mamdani sin desfuzzificar); notación `Tri`/`Trap`; los 5 pasos del FIS |
| 4.6 Contexto | Presentación como base de reglas; parámetros calibrados con fuentes |
| 4.7 Contratos | Actualizados ([plan 01](01-arquitectura.md#contratos-entre-módulos)) |
| 5.2 Modelo ampliado | Nuevo fitness con `κ·μ_CA(c)` y corrección contra portafolios degenerados |
| 5.x (nueva) | Problema de portafolios degenerados: detección y corrección |
| 9 Estado | Todo implementado |
| 9.x (nueva) | Resultados de ablación y calibración (tablas y figuras de F8) |
| Arquitectura | Opcional: modelos de CommonKADS (conocimiento, tarea, agentes) |
| Glosario | Mamdani, centroide, gen difuso, Bellman–Zadeh |
| Anexo C | Parámetros finales (κ, tope, consecuentes Mamdani) |
| Anexo D (nuevo) | Manual de instalación y de usuario o enlaces a ellos |

## Código fuente

- Repositorio con README actualizado (estructura real, cómo correr, cómo probar).
- Notebook corregido (orden de celdas) en `docs/`.
- Resultados de los experimentos versionados.

## Exposición y demo

**Guion sugerido (≈ 10 min):**

1. Problema y población objetivo (1 min).
2. Arquitectura: los módulos y su integración (2 min).
3. Demo en vivo con tres personas (4 min):
   - Conservador con horizonte corto y poco ahorro.
   - Moderado con horizonte medio.
   - Agresivo con horizonte largo y buen colchón; cambiar el panorama político a "Adverso" y mostrar el recálculo.
4. Dónde está el difuso: en el fitness (horizonte) y en el cromosoma (absorción), mostrando `μ_CA` y el `c` evolucionado (1.5 min).
5. Ablación: qué aporta cada componente (1 min).
6. Limitaciones y trabajo futuro (0.5 min).

**Plan B:** modo offline y capturas, por si falla la red o la API.
