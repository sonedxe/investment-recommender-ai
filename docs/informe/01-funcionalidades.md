# 1. Descripción de funcionalidades

Este capítulo describe cada funcionalidad de InvestWise desde la perspectiva del usuario y del sistema: qué recibe, qué procesa, qué entrega y qué módulo la resuelve. El flujo completo de una recomendación y el diseño interno de cada módulo se detallan en el capítulo 2.

## 1.1. Resumen de funcionalidades

Tabla: Resumen de las funcionalidades y del módulo que resuelve cada una

| Código | Funcionalidad | Módulo principal |
|---|---|---|
| F01 | Ingreso de la situación en lenguaje natural | Interfaz gráfica |
| F02 | Interpretación del texto del usuario | IA generativa |
| F03 | Aclaración de datos faltantes, vagos o contradictorios | IA generativa |
| F04 | Modelado difuso del horizonte temporal | Razonamiento bajo incertidumbre |
| F05 | Modelado difuso de la capacidad de absorción de pérdidas | Razonamiento bajo incertidumbre |
| F06 | Estimación bayesiana del mercado con datos reales | Razonamiento bajo incertidumbre |
| F07 | Ajuste por reglas de contexto | Reglas de contexto |
| F08 | Optimización del portafolio con algoritmo genético | Algoritmo heurístico |
| F09 | Presentación del portafolio recomendado | Interfaz gráfica |
| F10 | Explicación en lenguaje simple con validación de cifras | IA generativa |
| F11 | Panel de contexto con comparación antes y después | Interfaz gráfica y reglas de contexto |
| F12 | Detalle técnico y transparencia del cálculo | Interfaz gráfica |
| F13 | Interruptores de ablación | Algoritmo heurístico |
| F14 | Funcionamiento sin conexión y tolerancia a fallos | IA generativa |
| F15 | Funciones de uso general (nueva consulta, tema, celular, reproducibilidad) | Interfaz gráfica |

## 1.2. F01. Ingreso de la situación en lenguaje natural

**Descripción.** El usuario describe su situación con sus propias palabras, sin formularios ni términos técnicos. Puede mencionar el monto a invertir, sus ahorros totales, cuándo necesitará el dinero, cuánto riesgo acepta y cuántos meses de gastos tiene cubiertos.

- **Entrada:** texto libre, por ejemplo: «Tengo S/ 5,000 de mis S/ 20,000 de ahorro, no me gusta arriesgar y no los voy a necesitar en unos 3 años».
- **Proceso:** la interfaz valida que el texto no esté vacío y lo envía al servicio de interpretación. Ofrece un texto de ejemplo que puede copiarse con un clic.
- **Salida:** el texto queda registrado como el primer turno de la conversación.

![Pantalla de inicio: cuadro de texto libre y texto de ejemplo](../manuales/img/01-inicio.png)

## 1.3. F02. Interpretación del texto del usuario

**Descripción.** El módulo de IA generativa extrae del texto los cinco datos que necesita el cálculo y, para cada uno, la frase exacta del usuario que lo respalda (evidencia).

- **Entrada:** la conversación completa (texto inicial y respuestas posteriores).
- **Proceso:** se envía al modelo de lenguaje (Claude Haiku 4.5, de Anthropic) con un prompt versionado y un esquema JSON obligatorio. El modelo **solo extrae**: no calcula ni recomienda. El código valida el JSON y descarta cualquier dato que no tenga evidencia textual. La tolerancia al riesgo se clasifica en una escala cerrada de cinco niveles, que el código traduce a la aversión al riesgo λ:

Tabla: Escala cerrada de perfiles de riesgo y aversión al riesgo λ base

| Nivel | λ base |
|---|---|
| Muy agresivo | 0,2 |
| Agresivo | 0,5 |
| Moderado | 1,0 |
| Conservador | 2,0 |
| Muy conservador | 3,0 |

- **Salida:** perfil estructurado (monto, horizonte en años o como etiqueta, perfil de riesgo, ahorro total y meses de fondo de emergencia), con su evidencia.
- **Calidad medida:** en un conjunto de prueba de 23 casos (*golden set*), la interpretación con el modelo real alcanzó 98,3 % de exactitud por campo y 100 % de respuestas en formato JSON válido.

## 1.4. F03. Aclaración de datos faltantes, vagos o contradictorios

**Descripción.** Si falta un dato necesario, el sistema hace **una sola pregunta específica a la vez** en lugar de suponer valores. Es la principal defensa contra recomendaciones basadas en supuestos incorrectos.

- **Entrada:** el perfil parcialmente interpretado.
- **Proceso:** el código, no el modelo, decide qué falta y en qué orden preguntar: primero el monto, luego el horizonte y después la tolerancia al riesgo. Se pregunta también cuando el dato es vago («en unos años», «más adelante») o contradictorio («máxima ganancia sin perder nada»). El ahorro total y el fondo de emergencia se preguntan una sola vez y pueden omitirse con «Prefiero no responder»; en ese caso se asume una capacidad media de absorción y se declara como supuesto.
- **Salida:** una pregunta con opciones o con un campo numérico, y un panel que muestra qué entendió el sistema hasta ese momento y de qué frase lo obtuvo.
- **Calidad medida:** en el 100 % de los casos ambiguos o contradictorios del conjunto de prueba se generó una pregunta, nunca una suposición.

![Pregunta de aclaración ante un horizonte vago, con el panel de lo entendido hasta el momento](../manuales/img/02-aclaracion-horizonte.png)

## 1.5. F04. Modelado difuso del horizonte temporal

**Descripción.** El horizonte («unos 3 años», «a largo plazo») es un concepto impreciso. En lugar de umbrales rígidos, que darían recomendaciones muy distintas a personas con 2,9 y 3,1 años, se modela con conjuntos difusos. Este es el **conjunto difuso de la función de aptitud**.

- **Entrada:** horizonte en años o etiqueta cualitativa, y la λ base del perfil.
- **Proceso:** inferencia difusa de Sugeno de orden cero con tres conjuntos: Corto `Trap(0, 0, 1, 3)`, Mediano `Tri(2, 5, 8)` y Largo `Trap(6, 10, 30, 30)`. Cada conjunto activa una regla que modula la aversión al riesgo (multiplicadores 1,5, 1,0 y 0,7): un plazo corto vuelve al sistema más cauteloso y un plazo largo tolera más variabilidad.
- **Salida:** grados de pertenencia, multiplicador m_H y aversión efectiva λ_ef = λ_base × m_H, que entra directamente en la función de aptitud del algoritmo genético.

## 1.6. F05. Modelado difuso de la capacidad de absorción de pérdidas

**Descripción.** La capacidad de absorber pérdidas depende de qué parte de los ahorros se compromete y de cuántos meses de gastos están cubiertos. Se modela con un sistema difuso de Mamdani cuyo resultado **no se desfuzzifica**: el conjunto difuso resultante se incorpora como un **gen del cromosoma**. Este es el **conjunto difuso de la cadena genética**, solicitado por el docente.

- **Entrada:** proporción comprometida r = monto ÷ ahorro total y meses de fondo de emergencia E.
- **Proceso:** fuzzificación de r (Bajo, Medio, Alto) y de E (Insuficiente, Adecuada), seis reglas con operador Y (mínimo), implicación por mínimo y agregación por máximo, según el método visto en clase. El conjunto agregado μ_CA queda disponible para el algoritmo genético; el centroide se calcula solo como referencia para la explicación.
- **Salida:** conjunto difuso μ_CA sobre la capacidad de absorción, grados de activación de cada regla y centroide.

![Conjunto difuso de capacidad de absorción con el gen c elegido por el algoritmo genético y el centroide](../manuales/img/10-absorcion.png)

## 1.7. F06. Estimación bayesiana del mercado con datos reales

**Descripción.** El retorno esperado, el riesgo y las correlaciones de cada tipo de inversión se estiman a partir de series históricas oficiales, combinadas con valores de referencia mediante inferencia bayesiana.

- **Entrada:** cinco series mensuales de 2010 a 2026, descargadas una sola vez y versionadas en el repositorio: Índice General de la Bolsa de Valores de Lima, rendimiento del bono soberano a 10 años, tasa de los certificados de depósito y tasa pasiva de depósitos a plazo (Banco Central de Reserva del Perú), y valor cuota del Fondo de Pensiones Tipo 2 (Superintendencia de Banca, Seguros y AFP).
- **Proceso:** conversión de cada serie a retornos mensuales según su tipo, actualización conjugada normal del retorno esperado (valor previo del informe más los datos), estimación de la volatilidad, de la matriz de correlaciones y de la tendencia reciente de cada categoría.
- **Salida:** retorno esperado μ, volatilidad σ, correlaciones y tendencia por categoría. La procedencia de cada serie está documentada con capturas de las fuentes oficiales y conciliación valor por valor en el documento de evidencia de fuentes de datos.

## 1.8. F07. Ajuste por reglas de contexto

**Descripción.** El pasado estadístico no basta: un panorama político adverso o una economía inestable cambian las expectativas. Una base de reglas explícita (RC1 a RC7) ajusta directamente los parámetros que usa la función de aptitud.

- **Entrada:** panorama político y estabilidad macroeconómica (Adverso, Neutral o Favorable; Neutral por defecto), el precedente de cada categoría y su tendencia reciente.
- **Proceso:** cada regla suma o resta puntos porcentuales al retorno esperado y, en condiciones adversas, aumenta la volatilidad. El efecto es mayor en renta variable. Un tope de influencia de 3 puntos porcentuales impide que el contexto domine a los datos históricos. Un contexto favorable mejora el retorno pero no reduce el riesgo (asimetría prudente).
- **Salida:** retornos y volatilidades ajustados (μ′, σ′) y la lista de reglas activadas con su efecto numérico.

## 1.9. F08. Optimización del portafolio con algoritmo genético

**Descripción.** Un algoritmo genético busca el reparto que mejor equilibra retorno y riesgo para el perfil y el contexto de la persona.

- **Entrada:** μ′, la matriz de covarianzas ajustada, λ_ef (F04) y el conjunto difuso μ_CA (F05).
- **Representación:** cada individuo es un cromosoma `[w1, w2, w3, w4, w5 | c]`: cinco pesos que suman 100 % y un gen difuso c que representa el nivel de absorción que asume el portafolio.
- **Función de aptitud:** combina el retorno ajustado por el contexto, el riesgo ponderado por la aversión efectiva, una penalización cuando la volatilidad supera la tolerable según el gen c y una recompensa por la compatibilidad de c con la capacidad real del usuario.
- **Proceso:** población de 80 portafolios, selección por torneo, cruce aritmético, mutación gaussiana y elitismo. El algoritmo se detiene al converger (25 generaciones sin mejora) o a las 200 generaciones, y con la misma semilla produce siempre el mismo resultado. Una política de diversificación limita cada categoría **entre 5 % y 40 %**, lo que evita portafolios concentrados en un solo tipo de inversión.
- **Salida:** pesos de las cinco categorías, gen c, desglose de la aptitud en sus componentes y curva de convergencia.

La función de aptitud que maximiza el algoritmo es:

```
Aptitud(P) = Σ wᵢ·μ′ᵢ − λ_ef·σ′(P) − φ·max(0, σ′(P) − σ_max(c))² + κ·μ_CA(c)
```

donde σ_max(c) = 3 % + 13 %·c es la volatilidad máxima tolerable asociada al gen c, φ = 50 y κ = 0,03.

## 1.10. F09. Presentación del portafolio recomendado

**Descripción.** El resultado se muestra en soles y en porcentaje, con una barra que resume la distribución y una fila por tipo de inversión.

- **Entrada:** pesos del algoritmo genético y monto a invertir.
- **Proceso:** los montos se redondean al céntimo y se ajustan para que sumen exactamente el total invertido.
- **Salida:** distribución en soles y porcentaje, supuestos aplicados y acceso al panel de contexto y a una nueva consulta.

![Resultado: distribución del monto entre los cinco tipos de inversión y supuestos aplicados](../manuales/img/05-resultado.png)

## 1.11. F10. Explicación en lenguaje simple con validación de cifras

**Descripción.** El módulo de IA generativa redacta una explicación para personas sin conocimientos financieros, con montos en soles, escenarios y los supuestos aplicados.

- **Entrada:** únicamente cifras ya calculadas por el sistema: reparto, escenarios, efecto del horizonte y de la absorción, y supuestos.
- **Proceso:** el modelo (Claude Sonnet 5.5) recibe reglas obligatorias: traducir cada término técnico, acompañar cada porcentaje de su monto en soles, explicar el riesgo con escenarios y declarar los supuestos. Los escenarios (año malo, normal y bueno) los calcula el código como E ± 1,65·σ. Un validador revisa que **cada número del texto exista entre las cifras calculadas**; si encuentra una cifra inventada, pide una corrección y, si vuelve a fallar, usa una plantilla determinista.
- **Salida:** resumen, párrafos explicativos y escenarios en soles.

![Explicación en lenguaje simple y escenarios estimados para un año](../manuales/img/06-explicacion.png)

## 1.12. F11. Panel de contexto con comparación antes y después

**Descripción.** El usuario puede cambiar los supuestos del entorno y ver de inmediato cómo cambia la recomendación.

- **Entrada:** nivel de panorama político y de estabilidad macroeconómica (Adverso, Neutral o Favorable).
- **Proceso:** se recalcula el portafolio con la misma semilla, de modo que la diferencia se debe solo al contexto.
- **Salida:** comparación de la distribución antes y después del cambio, con la indicación de que se trata de supuestos configurables y no de predicciones.

![Panel de contexto con el panorama político en Adverso y la comparación antes y después](../manuales/img/07-contexto-adverso.png)

## 1.13. F12. Detalle técnico y transparencia del cálculo

**Descripción.** Una sección desplegable, cerrada por defecto, muestra todo lo que el sistema calculó, para usuarios avanzados y para la evaluación académica.

- **Contenido:**
    - parámetros por categoría (μ y σ originales y ajustados, ajuste por contexto y fuente de los datos);
    - cálculo de la aversión al riesgo (λ base × m_H = λ efectiva);
    - gráfico de las funciones de pertenencia del horizonte con el valor del usuario;
    - gráfico del conjunto de absorción con el gen c y el centroide;
    - reglas difusas y de contexto activadas, con su grado de activación α;
    - desglose de la función de aptitud y curva de convergencia del algoritmo genético.
- **Accesibilidad:** cada gráfico incluye una tabla equivalente («Ver los mismos datos en tabla»).

![Reglas activadas con su grado de activación y su efecto numérico](../manuales/img/11-reglas.png)

## 1.14. F13. Interruptores de ablación

**Descripción.** Dentro del detalle técnico, dos interruptores permiten desactivar la lógica difusa o las reglas de contexto y recalcular. Sirven para comparar qué aporta cada componente.

- **Proceso:** sin lógica difusa, λ_ef = λ_base y no hay penalización por volatilidad ni recompensa del gen c; sin contexto, μ′ = μ y σ′ = σ.
- **Salida:** nueva recomendación con la misma semilla. El mismo mecanismo se usó en los experimentos de ablación del proyecto.

## 1.15. F14. Funcionamiento sin conexión y tolerancia a fallos

**Descripción.** La aplicación funciona aunque no haya una clave de API o el servicio de IA generativa no responda.

- **Proceso:** un extractor de reglas en español y una plantilla de explicación determinista reemplazan al modelo de lenguaje. Si una llamada al modelo devuelve un JSON inválido, se reintenta una vez y luego se usa el modo sin conexión. Las pruebas automáticas se ejecutan siempre en este modo, sin consumir crédito.
- **Salida:** la misma estructura de respuesta. La interfaz muestra el indicador «Modo sin conexión» cuando el sistema está configurado sin proveedor de IA.

## 1.16. F15. Funciones de uso general

- **Nueva consulta:** reinicia el flujo desde el resultado o el panel de contexto.
- **Tema claro u oscuro:** se adapta a la preferencia del sistema y recuerda la elección del usuario.
- **Uso en celular:** el diseño se adapta a pantallas desde 360 píxeles de ancho.
- **Reproducibilidad:** datos de mercado versionados con su procedencia, parámetros configurables en archivos JSON y semilla fija en el algoritmo genético.

## 1.17. Relación entre funcionalidades y componentes del software inteligente

Tabla: Relación entre los componentes exigidos y las funcionalidades

| Componente exigido | Funcionalidades | Técnica |
|---|---|---|
| IA generativa (mediante API) | F02, F03, F10, F14 | Modelo de lenguaje Claude con salida JSON validada; interpreta la solicitud, genera la información de entrada y explica el resultado |
| Algoritmo heurístico | F08, F13 | Algoritmo genético con cromosoma de pesos y gen difuso |
| Razonamiento bajo incertidumbre | F04, F05, F06 | Lógica difusa (Sugeno y Mamdani) e inferencia bayesiana |
| Reglas de contexto | F07, F11 | Base de reglas explícita con tope de influencia |
| Interfaz gráfica | F01, F09, F11, F12, F15 | Aplicación web en React conectada a la API |
