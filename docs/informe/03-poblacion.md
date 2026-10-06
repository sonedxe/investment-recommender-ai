# 3. Tipo de población que puede usar el software inteligente

InvestWise está diseñado para personas que necesitan una primera orientación sobre cómo distribuir sus ahorros y que no cuentan con formación financiera ni con acceso a un asesor. Su diseño responde a las características de ese público: acepta texto libre en lugar de formularios técnicos, pregunta cuando falta un dato en vez de suponerlo, expresa el resultado en soles y explica el riesgo con escenarios concretos. Este capítulo identifica los segmentos que pueden usarlo, sus necesidades y la forma en que el sistema las atiende, así como los usos para los que no está indicado.

## 3.1. Población objetivo principal: ciudadanos sin conocimientos financieros

El segmento principal son ciudadanos del Perú que tienen un ahorro en soles, desean invertir una parte y desconocen los instrumentos disponibles o el significado de términos como volatilidad, renta fija o duración. Para este público, las dificultades habituales son tres: no saben qué datos de su situación son relevantes, no pueden comparar instrumentos con riesgos distintos y no comprenden las recomendaciones expresadas en lenguaje técnico.

InvestWise atiende esas dificultades en cada etapa del flujo:

- **Ingreso.** La persona escribe su situación como la contaría a un conocido («tengo S/ 5,000 de mis S/ 20,000 de ahorro, no me gusta arriesgar y no los voy a necesitar en unos 3 años»). No necesita conocer su perfil de riesgo en términos técnicos: el sistema lo clasifica a partir de cómo describe su relación con el riesgo.
- **Aclaración.** Si un dato falta o es vago («en unos años»), el sistema formula una sola pregunta sencilla, con opciones o con un ejemplo de respuesta, y muestra qué entendió hasta ese momento y de qué frase lo obtuvo. La persona puede negarse a dar sus ahorros totales o su fondo de emergencia; en ese caso el sistema declara el supuesto que aplica.
- **Resultado.** El reparto se presenta en soles y en porcentaje, con montos exactos al céntimo, y cada categoría se describe con palabras simples.
- **Comprensión del riesgo.** En lugar de una cifra abstracta de volatilidad, la explicación indica cuánto podría ganar o perder en un año malo, normal o bueno, en soles.
- **Contexto.** La persona puede indicar si percibe un panorama político o económico adverso y observar cómo cambia la recomendación, presentada siempre como un supuesto configurable.

## 3.2. Segmentos secundarios

Además del ciudadano sin formación financiera, el sistema resulta útil para otros grupos. La @tab:segmentos resume cada segmento, su necesidad, la forma en que InvestWise la atiende y un ejemplo de uso.

Tabla: {#tab:segmentos} Segmentos de población, necesidades y casos de uso

| Segmento | Necesidad | Cómo ayuda InvestWise | Ejemplo de uso |
|---|---|---|---|
| Ciudadanos sin conocimientos financieros (principal) | Saber cómo repartir un ahorro según su plazo y su tolerancia al riesgo, en un lenguaje comprensible | Conversación en lenguaje natural, preguntas de aclaración, montos en soles, escenarios y explicación sin jerga | Una trabajadora dependiente con S/ 8,000 que no necesitará en 5 años describe su situación y obtiene un reparto con la ganancia o pérdida posible en un año malo |
| Estudiantes de finanzas, economía o ingeniería | Comprender cómo interactúan retorno, riesgo, correlación, incertidumbre y optimización en un problema real | Detalle técnico con μ y σ originales y ajustados, pertenencias difusas, reglas activadas, desglose de la aptitud y curva de convergencia; interruptores para apagar componentes | Un estudiante compara el portafolio de un perfil agresivo con horizonte de 2 y de 12 años y observa cómo cambia λ_ef |
| Pequeñas empresas y profesionales independientes | Obtener una primera referencia para un fondo de reserva o de ahorro propio antes de consultar a un asesor certificado | Reparto entre instrumentos del mercado peruano con escenarios en soles y sensibilidad al contexto | Un profesional independiente evalúa cómo distribuir S/ 30,000 de su fondo de reserva con un panorama político adverso |
| Instituciones educativas | Disponer de un caso de estudio que integre varias técnicas de inteligencia artificial con fines pedagógicos | Código fuente organizado por módulo del curso, parámetros en archivos JSON, experimentos reproducibles con semilla y pruebas automáticas | Un curso de software inteligente usa la aplicación para mostrar un sistema difuso de Mamdani sin desfuzzificar dentro de un cromosoma |
| Programas de educación financiera (municipalidades, ONG, áreas de bienestar de empresas) | Enseñar conceptos básicos de inversión a públicos amplios con ejemplos concretos | Funcionamiento sin conexión y sin costo de API, adaptación a celulares desde 360 píxeles y tema claro u oscuro | Un taller de educación financiera usa el modo sin conexión para que cada participante pruebe su propio caso |

En todos los segmentos el resultado tiene carácter orientativo: las categorías son representativas del mercado peruano y no productos específicos, y las estimaciones provienen de datos históricos ajustados por supuestos de contexto.

## 3.3. Usos a los que no está dirigido

El sistema no está dirigido a:

- **inversionistas institucionales y gestores profesionales de fondos**, que requieren instrumentos específicos, datos en tiempo real, restricciones regulatorias de cartera, costos de transacción y modelos de riesgo más completos;
- **asesoría financiera regulada**, es decir, cualquier uso que requiera cumplimiento normativo, evaluación de idoneidad de un cliente o recomendación de productos concretos de una entidad;
- **decisiones de corto plazo o especulativas**, como la compra y venta frecuente de valores, porque el modelo trabaja con estimaciones anuales y horizontes de inversión, no con señales de mercado diarias.

Esta delimitación es coherente con el diseño: los datos de mercado se descargan una vez y se versionan, las categorías son representativas y el contexto se modela como un supuesto ajustable por el usuario, no como una predicción.
