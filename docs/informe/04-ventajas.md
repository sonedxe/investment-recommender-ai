# 4. Ventajas del software inteligente frente a otros softwares existentes

Este capítulo compara InvestWise con cinco tipos de software que abordan el mismo problema de forma parcial y resume, para cada ventaja, la evidencia del proyecto que la respalda. La comparación se hace por tipo de software y no con productos comerciales concretos.

## 4.1. Comparación por tipo de software

Tabla: {#tab:ventajas} Limitaciones de los tipos de software existentes y respuesta de InvestWise

| Software existente | Limitación | Respuesta de InvestWise |
|---|---|---|
| Calculadoras de perfil de riesgo (cuestionarios estáticos) | Formularios rígidos de opción múltiple; no interpretan lenguaje natural ni piden aclaraciones cuando la información es ambigua; suelen asignar un perfil, no un reparto | Interpretación del texto libre con evidencia por dato, una pregunta específica cuando falta o es vago un dato, y un reparto concreto en soles |
| Robo-advisors comerciales | Optimizan portafolios, pero no explican el razonamiento en lenguaje accesible y asumen que el usuario entiende términos financieros; sus parámetros y reglas no son visibles | Explicación en lenguaje simple con escenarios en soles y detalle técnico completo: parámetros, reglas activadas con su grado de activación, desglose de la aptitud y convergencia |
| Simuladores de portafolio académicos | Implementan solo la optimización (media-varianza o una heurística) con parámetros fijos, sin un componente de incertidumbre actualizable ni una capa conversacional | Estimación bayesiana con series oficiales, lógica difusa sobre el perfil, reglas de contexto y una interfaz conversacional integradas en un mismo flujo |
| Chatbots financieros basados solo en un modelo de lenguaje | Generan texto plausible, pero no ejecutan una optimización matemática ni un modelo probabilístico explícito; pueden inventar cifras y su respuesta no es reproducible | El modelo de lenguaje solo interpreta y redacta; el cálculo lo hacen módulos deterministas y cada número del texto se valida contra las cifras calculadas |
| Perfilamiento con umbrales rígidos y sin contexto | Reglas del tipo «si el plazo es menor a 3 años, perfil conservador», con saltos bruscos en los bordes y sin considerar el entorno | Transiciones graduales con conjuntos difusos y ajustes de contexto acotados, visibles y configurables |

## 4.2. Ventajas respaldadas por la evidencia del proyecto

**Transiciones graduales en lugar de umbrales.** El horizonte se modela con conjuntos difusos: un plazo de 2,5 años pertenece en 0,25 a Corto y en 0,17 a Mediano y produce m_H = 1,30, un valor intermedio entre 1,5 y 1,0. Dos personas con 2,9 y 3,1 años reciben aversiones efectivas cercanas, no perfiles distintos. En los experimentos de ablación, el horizonte es el componente que más mueve el portafolio del perfil agresivo (acciones de 5,0 % a 39,2 % con horizonte largo), lo que muestra que la modulación difusa tiene efecto real y no solo descriptivo.

**Capacidad de absorción integrada en la búsqueda.** El conjunto difuso de la capacidad de absorber pérdidas no se reduce a un número antes de optimizar: el algoritmo genético elige un punto c de ese conjunto y la función de aptitud lo equilibra con la volatilidad. Cuando el perfil pide más riesgo del que la capacidad permite, la volatilidad se recorta (de 11,3 % a 5,9 % con absorción baja y λ_base = 0,2); cuando la capacidad lo permite, el límite no interviene. Un cuestionario estático o un simulador con parámetros fijos no distinguen estos casos.

**Datos reales con procedencia verificable.** Las cinco categorías se estiman con series mensuales oficiales del BCRP y de la SBS de 2010 a 2026, combinadas con valores de referencia mediante inferencia bayesiana. La conciliación con las fuentes coincide en 48 de 48 valores del BCRP y en 36 de 36 valores de la SBS revisados. Los simuladores académicos suelen trabajar con valores supuestos.

**Contexto explícito y acotado.** Siete reglas legibles ajustan el retorno y la volatilidad según el panorama político, la estabilidad macroeconómica y la tendencia. El efecto está limitado a 3 puntos porcentuales y es asimétrico (un contexto favorable no reduce el riesgo). En el perfil moderado, un panorama político adverso reduce la renta variable en 3,9 puntos porcentuales; en el agresivo, las acciones bajan de 39,2 % a 8,4 % con un panorama levemente adverso. El usuario ve qué reglas se activaron y con qué efecto.

**Explicación sin cifras inventadas.** La explicación la redacta un modelo de lenguaje, pero solo puede citar cifras calculadas por el sistema: un validador revisa cada número, el formato de los montos y que cada porcentaje vaya acompañado de su monto en soles; si falla, se reintenta y, en último caso, se usa una plantilla determinista. Esto elimina el principal riesgo de un asistente basado solo en un modelo de lenguaje.

**Aclaración en lugar de supuestos.** El código, no el modelo, decide qué falta y qué se pregunta. En el conjunto de prueba de 23 casos, el 100 % de los casos ambiguos o contradictorios produjo una pregunta y ninguno una suposición, tanto con el modelo real como sin conexión. La segunda versión del prompt de interpretación se introdujo precisamente para que expresiones vagas como «en unos años» no se conviertan en un horizonte largo.

**Transparencia, ablación y reproducibilidad.** El detalle técnico expone todos los valores intermedios y dos interruptores permiten apagar la lógica difusa o el contexto y recalcular con la misma semilla para observar qué aporta cada componente. Con la misma semilla el resultado es idéntico; los parámetros están en archivos JSON y los experimentos se reproducen byte a byte.

**Funcionamiento sin conexión.** Si no hay clave de API o el proveedor falla, un extractor en español y una plantilla de explicación sustituyen al modelo de lenguaje con el mismo contrato, de modo que la aplicación sigue operativa sin costo. Un chatbot que depende solo del modelo deja de funcionar en esa situación.

## 4.3. Ventaja central

La ventaja central de InvestWise no es una técnica aislada, sino su integración: la IA generativa traduce el lenguaje del usuario y explica el resultado; la lógica difusa convierte la imprecisión del perfil en parámetros del cálculo; la inferencia bayesiana y las reglas de contexto aportan estimaciones de mercado fundamentadas y ajustables; y el algoritmo genético encuentra el reparto que equilibra retorno y riesgo para esa persona. Cada componente entrega su resultado al siguiente mediante contratos explícitos, y todo el proceso queda visible para el usuario y verificable mediante pruebas.
