# 01 · Trazabilidad y cumplimiento del enunciado

## Evolución del proyecto

| Momento | Documento | Aporte principal |
|---|---|---|
| Enunciado | `docs/Enunciado Trabajo Parcial.pdf` | GUI + 3 módulos: IA generativa (API), heurístico, razonamiento bajo incertidumbre. Entregables: manuales, informe técnico, código. Hitos: S4 10 %, S5 30 %, S6 60 %, S7 final y exposición. |
| Semana 3 | `docs/Guia_Equipo_Proyecto.md.pdf`, `docs/Software_Inteligente_Propuesta4_Semana3.pdf`, `docs/PropuestaAG_GCEL.ipynb` | Problema de portafolio, AG con `Fitness = E(P) − λ·σ(P)`, 5 activos, módulo bayesiano como incertidumbre. |
| Semana 5 (v1.0) | `docs/Informe_Tecnico_Avance_Semana5.pdf` | Alcance Perú, 5 categorías representativas (AAFMP), contratos entre módulos, loop de clarificación, capa de explicación en lenguaje simple. |
| Feedback S5 | Clase | "Un conjunto difuso en la evaluación/fitness y otro como componente de la cadena genética" + reglas de contexto que influyan directamente en el fitness. |
| v1.1 | `docs/Informe_Tecnico_InvestWise_v1.1.pdf` | Módulo difuso (horizonte → λ_ef; absorción → σ_max), reglas de contexto, fitness ampliado, Anexo C con parámetros. |
| Repositorio | commit `acfc7eb` | Esqueleto: FastAPI + React/Vite/TS + paquetes `ai/{generative,heuristic,uncertainty}` con solo `ping()`. |

## Requisitos del enunciado

| Requisito | Diseño | Código |
|---|---|---|
| Interfaz gráfica única | ✅ Especificada (tabla, gráfico, panel de contexto, detalle técnico) | ⚪ Esqueleto React |
| IA generativa vía API (interpretar, generar entrada, explicar) | ✅ Con loop de clarificación | ❌ Solo `ping()` |
| Módulo heurístico **diseñado e implementado** | ✅ AG; prototipo en Colab | ❌ No migrado |
| Módulo de incertidumbre **programado** | ✅ Bayesiano + lógica difusa | ❌ No implementado |
| Integración coordinada de los tres | ✅ Flujo de 8 etapas y contratos | ❌ |
| Manual de instalación y de usuario | ❌ | ❌ |
| Informe técnico (funcionalidades, arquitectura, población, ventajas) | ✅ v1.1 cubre los cuatro puntos | — |
| Código fuente completo | — | ❌ |

> **Nota sobre "programado" e "implementado":** el enunciado exige que los módulos heurístico y de incertidumbre sean diseñados y programados por el equipo. Usar librerías que resuelven el problema completo (p. ej. `scikit-fuzzy`, `DEAP`, `PyPortfolioOpt`) debilitaría la evaluación. Se recomienda implementar con NumPy puro.
