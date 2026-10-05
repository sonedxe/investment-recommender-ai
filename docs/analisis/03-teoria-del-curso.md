# 03 · Alineación con la teoría del curso

Fuentes: `docs/clases/`.

## 1. Lógica difusa

`TEO-Logica Difusa.pdf` (40 diapositivas) y `TEO-Logica Difusa (1).pdf` (36; misma base, con el ejercicio de la propina más desarrollado).

### Contenido del docente

- Distinción entre **incertidumbre** (falta de información), **probabilidad** (frecuencia verificable por experimentación) e **imprecisión/ambigüedad** (vaguedad del lenguaje; "incertidumbre determinista").
- Conjunto difuso: función de membresía `A(x) ∈ [0, 1]`.
- Funciones de membresía: singleton, triangular `Tri(a,b,c)`, trapezoidal `Trap(a,b,c,d)`, gaussiana, campana, sigmoide, forma S.
- Operadores de Zadeh: intersección = `min`, unión = `max`, negación = `1 − μ`; propiedades (conmutativa, asociativa, distributiva, idempotencia, involución, transitiva, De Morgan).
- FIS en 5 pasos: (1) fuzzificar, (2) operador difuso (AND = min, OR = max), (3) implicación (Mamdani: recorte por mínimo), (4) agregación (máximo), (5) desfuzzificación (centroide `x* = ∫x·μ(x)dx / ∫μ(x)dx`; alternativa: centros promediados).
- **Mamdani** ("el más comúnmente utilizado", salidas como conjuntos difusos) frente a **Sugeno** (salidas lineales o constantes; `y = Σwᵢyᵢ / Σwᵢ`).
- Ejercicio resuelto a mano (propina): servicio = 3, comida = 8 → Mamdani completo con integrales por tramos → **P\* = 15.9 %**.

### Implicaciones

| Aspecto | v1.1 | Recomendación |
|---|---|---|
| Justificar el módulo de incertidumbre | Bayes + difuso sin distinguir roles | Usar la distinción del docente: **Bayes** trata la incertidumbre/probabilidad de los retornos; **lógica difusa** trata la ambigüedad del lenguaje del usuario ("unos años", "no quiero perder mucho"). |
| Tipo de FIS | Sugeno-0 en ambos | **Mamdani** en al menos uno para evidenciar los 5 pasos enseñados; Sugeno en el otro demuestra dominio de ambos tipos. |
| Notación | Funciones a tramos | Notación del docente (tabla siguiente). |
| Validación | — | Usar el ejercicio de la propina como test de referencia del motor Mamdani. |

### Conjuntos de la v1.1 en notación del docente

Verificados contra las funciones a tramos del informe; no hay zonas del universo con pertenencia total cero.

| Variable | Conjunto | Notación |
|---|---|---|
| Horizonte H ∈ [0, 30] | Corto | `Trap(0, 0, 1, 3)` |
| | Mediano | `Tri(2, 5, 8)` |
| | Largo | `Trap(6, 10, 30, 30)` |
| Proporción r ∈ [0, 1] | Bajo | `Trap(0, 0, 0.2, 0.4)` |
| | Medio | `Tri(0.2, 0.5, 0.8)` |
| | Alto | `Trap(0.6, 0.9, 1, 1)` |
| Cobertura E ∈ [0, 12] | Insuficiente | `Trap(0, 0, 1, 4)` |
| | Adecuada | `Trap(2, 6, 12, 12)` |

## 2. Algoritmos genéticos

`TEO-Algoritmo Genéticos.pdf` y `TEO-Algoritmo Genéticos Binario.pdf`.

### Contenido del docente

- Fases: población inicial → fitness → selección → cruce → mutación → reemplazo → test de término.
- Selección: **ruleta** (`fᵢ / Σf`), **torneo**, ranking.
- Cruce de **un punto**, presentado como la fase más significativa.
- Mutación con probabilidad baja; cantidad = `tasa × genes × población`.
- Término por **convergencia** (la descendencia ya no difiere significativamente) o por fitness objetivo.
- Limitaciones: mala representación, **función de aptitud mal escrita** ("puede acabar resolviendo el problema equivocado"), convergencia prematura en poblaciones pequeñas.
- Aplicaciones listadas: incluye **"Aprendizaje de reglas de lógica difusa"**, lo que respalda combinar AG y lógica difusa en el cromosoma.

### Implicaciones

| Aspecto | Diseño actual | Recomendación |
|---|---|---|
| Selección | Torneo ✅ | Mantener. **No usar ruleta**: el fitness puede ser negativo. Justificarlo en el informe. |
| Cruce | Aritmético + normalización | Válido para genes reales; justificar por qué no es el de un punto (rompe Σ = 1). Opcional: implementar ambos y compararlos. |
| Término | 100 generaciones fijas | Añadir criterio de convergencia (sin mejora en N generaciones). |
| Elitismo | Sí (prototipo) | Mantener y documentar. |
| Fitness mal planteada | — | El hallazgo de portafolios degenerados ([05 §1](05-hallazgos-tecnicos.md#1--portafolios-degenerados-verificado)) es esa limitación; presentarlo como problema detectado y corregido. |

## 3. Proyectos de Software Inteligente

- Ciclos de vida CRISP-DM / KDD, SDLC, Scrum, DevOps/MLOps (automatización, testing, reproducibilidad), AIOps.
- **CommonKADS**: modelos de organización, tarea, agente, comunicación, conocimiento y diseño.
- Implicación: el informe final puede describir la arquitectura con los modelos de CommonKADS (sobre todo el **modelo de conocimiento**: reglas difusas + reglas de contexto) y respaldar la calidad con tests automatizados y CI.

## 4. Otras clases

| Clase | Relevancia |
|---|---|
| Conjunto de datos | Fuentes de datos abiertos: base para elegir la fuente de series del módulo bayesiano. |
| ML supervisado, Redes neuronales, RN multicapa | No requeridas por el enunciado; fuera de alcance. |
| Sistemas multiagente | Opcional: el flujo podría describirse como agentes cooperativos; no aporta a la evaluación. |
| Evolución humana | Contexto conceptual del AG. |
