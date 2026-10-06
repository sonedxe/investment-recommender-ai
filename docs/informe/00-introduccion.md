# Introducción

## Problema

Una persona que tiene ahorros en soles y desea invertir una parte de ellos enfrenta tres dificultades simultáneas. La primera es de lenguaje: describe su situación con expresiones imprecisas («en unos años», «no me gusta arriesgar», «tengo algo ahorrado») que no encajan en los formularios de opción múltiple de las calculadoras de perfil de riesgo. La segunda es de cálculo: repartir un monto entre varios instrumentos con retornos, volatilidades y correlaciones distintas es un problema de optimización que no se resuelve de forma intuitiva. La tercera es de comprensión: aun cuando se obtiene una recomendación, esta suele expresarse en términos técnicos (volatilidad, renta fija, duración) que la persona no domina, por lo que no puede evaluarla ni confiar en ella.

A estas dificultades se suma la incertidumbre propia del problema. Los retornos futuros no se conocen, los datos históricos solo los aproximan y el entorno político y económico del país modifica las expectativas de forma que los promedios históricos no capturan.

## Objetivo

El objetivo del proyecto es desarrollar **InvestWise**, un software inteligente que, a partir de la descripción en lenguaje natural de la situación de una persona, recomiende y explique cómo repartir un monto en soles entre cinco categorías representativas de inversión del mercado peruano: fondos de acciones, fondos mixtos, fondos de deuda, bonos soberanos (BTP) y depósitos a plazo fijo.

Los objetivos específicos son:

- interpretar el texto libre del usuario y obtener los datos necesarios para el cálculo, preguntando cuando falta un dato o es ambiguo, en lugar de suponerlo;
- estimar el retorno esperado, la volatilidad y las correlaciones de cada categoría con series históricas oficiales y un modelo bayesiano;
- modelar la imprecisión del horizonte temporal y de la capacidad de absorber pérdidas con lógica difusa;
- ajustar las estimaciones según el contexto político y macroeconómico mediante una base de reglas explícita y acotada;
- encontrar el reparto que mejor equilibra retorno y riesgo para el perfil del usuario con un algoritmo genético;
- explicar el resultado en lenguaje simple, con montos en soles y escenarios, sin introducir cifras que el sistema no haya calculado.

## Integración de los componentes del curso

El enunciado del trabajo exige integrar en una aplicación con interfaz gráfica tres componentes: inteligencia artificial generativa conectada mediante una API, un algoritmo heurístico y razonamiento bajo incertidumbre. En InvestWise cada componente resuelve una de las dificultades descritas y entrega su resultado al siguiente, de modo que ninguno funciona como un añadido aislado:

- **IA generativa.** Un modelo de lenguaje de Anthropic, accedido mediante su API, interpreta el texto del usuario y lo convierte en un perfil estructurado con evidencia textual de cada dato (Claude Haiku 4.5) y, al final del flujo, redacta la explicación del resultado (Claude Sonnet 5.5). El código decide qué falta, qué se pregunta y qué cifras pueden aparecer en el texto.
- **Razonamiento bajo incertidumbre.** Se emplean dos técnicas con roles distintos. La inferencia bayesiana trata la incertidumbre estadística de los retornos: combina valores de referencia con cinco series mensuales oficiales del BCRP y de la SBS. La lógica difusa trata la imprecisión del lenguaje: el horizonte temporal se modela con un sistema de Sugeno cuyo resultado modula la aversión al riesgo dentro de la función de aptitud, y la capacidad de absorción de pérdidas con un sistema de Mamdani cuyo conjunto difuso de salida, sin desfuzzificar, se incorpora como un gen del cromosoma.
- **Algoritmo heurístico.** Un algoritmo genético busca el reparto óptimo sobre un cromosoma de cinco pesos y un gen difuso, con una función de aptitud que combina el retorno ajustado, el riesgo ponderado por la aversión efectiva, una penalización por volatilidad excesiva y una recompensa por la compatibilidad del gen difuso con la capacidad real del usuario.

A estos tres componentes se suman unas **reglas de contexto** (RC1 a RC7) que ajustan el retorno y el riesgo según el panorama político, la estabilidad macroeconómica y la tendencia reciente de cada categoría, y una **interfaz gráfica** web que conduce la conversación, presenta el portafolio y permite inspeccionar cada cálculo.

## Organización del informe

El capítulo 1 describe las funcionalidades; el 2, la arquitectura y cada componente, con sus contratos, fórmulas, parámetros y ejemplos calculados con el código del proyecto; el 3, la población que puede usar el sistema; el 4, sus ventajas frente a otros programas, y el 5, la evidencia que las respalda. Los anexos contienen los parámetros, las fuentes de datos y las decisiones de diseño.

**Convenciones.** El texto y las tablas usan la coma decimal (12,2 %); las fórmulas, la notación `Tri` y `Trap` y el código usan el punto decimal. Los montos siguen el formato de la aplicación (S/ 1,250.00) y el apóstrofo (μ′, σ′) indica un valor ajustado por el contexto. Todas las cifras provienen del código, de los archivos de datos y parámetros o de los resultados del repositorio.
