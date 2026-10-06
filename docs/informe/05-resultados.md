# 5. Resultados y validación

Este capítulo reúne la evidencia que respalda el funcionamiento del sistema y las ventajas descritas en el capítulo 4: pruebas automáticas, pruebas de referencia contra cálculos hechos a mano, evaluación de la IA generativa con un conjunto de casos de prueba, experimentos sobre el modelo y conciliación de los datos con las fuentes oficiales.

## 5.1. Pruebas automáticas

El proyecto tiene 390 pruebas automáticas: 306 del backend y del núcleo de IA (pytest) y 84 de la interfaz gráfica (Vitest y Testing Library). Todas se ejecutan en modo sin conexión, sin consumir crédito de la API, y todas pasan en la versión entregada.

Tabla: {#tab:pruebas-backend} Pruebas del backend y del núcleo de IA por módulo

| Módulo | Qué verifican | Pruebas |
|---|---|---|
| IA generativa | Adaptadores (construcción de peticiones, selección de modelo, errores del proveedor), interpretación y política de aclaración, explicación y validador de cifras, extractor sin conexión, conjunto de prueba sin conexión | 101 |
| Algoritmo genético | Reparación del cromosoma con piso y tope, función de aptitud y su desglose, operadores, convergencia, reproducibilidad con semilla, regresión del gen c | 39 |
| Lógica difusa | Funciones de pertenencia, motores de Sugeno y Mamdani, sistemas de horizonte y absorción | 32 |
| Parámetros y tipos | Carga y validación de los archivos JSON y de los tipos compartidos | 32 |
| Estimación bayesiana | Transformaciones a retornos, actualización conjugada, correlaciones, reparación de la matriz, tendencia, lectura del manifiesto | 28 |
| Descarga de datos | Lectura de las tablas del BCRP y del archivo de la SBS, filtro de valores anómalos | 27 |
| Reglas de contexto | Reglas RC1 a RC7, asimetría, tope de influencia, preservación de correlaciones | 18 |
| Integración | Rutas de la API de extremo a extremo, conectividad y ejecución de los experimentos | 29 |
| Total | | 306 |

Tabla: {#tab:pruebas-frontend} Pruebas de la interfaz gráfica

| Área | Qué verifican | Pruebas |
|---|---|---|
| Máquina de estados del flujo | Transiciones válidas, descarte de respuestas obsoletas, reutilización de la semilla, errores y reinicio | 22 |
| Cliente de la API y *mappers* | Peticiones, clases de error y traducción de los contratos capturados del backend real | 30 |
| Componentes y pantallas | Formato de montos, gráficos accesibles con tabla equivalente, reglas con su activación, pantallas con datos fijos | 22 |
| Flujo completo | Texto → pregunta → respuesta → resultado → cambio de contexto, reintentos y tema | 7 |
| Utilidades | Formato de porcentajes y escalas de los gráficos | 3 |
| Total | | 84 |

## 5.2. Pruebas de referencia

Tres pruebas comparan el código con cálculos hechos a mano en documentos del curso y del proyecto:

- **Ejercicio de la propina (Mamdani).** Con servicio = 3 y comida = 8, el motor obtiene el centroide exacto 16,009 %, calculado por integrales con el recorte correcto de la regla R1. La diapositiva de clase informa 15,9 % porque no recorta esa regla entre P = 10 y P = 11,67 (sección 2.6.3).
- **Horizonte H = 2,5 años (Sugeno).** Pertenencias 0,25 y 0,17, m_H = 1,30 y λ_ef = 2,6 para λ_base = 2, como en el ejemplo de la sección 2.6.1.
- **Tabla 4.6.4 del informe de avance (contexto).** Con s_pol = −1 y los valores de referencia, cᵢ = −2,5; −1,2; −0,5; −0,8; −0,3 pp, μ′ de acciones = 9,7 % y σ′ de acciones = 28,5 %.

## 5.3. Evaluación de la IA generativa

La interpretación se evaluó con un conjunto de 23 casos de prueba (*golden set*) que cubre perfiles completos, horizontes vagos y en meses, montos en palabras, montos en dólares, contradicciones, negativas a responder y conversaciones de varios turnos. Cada caso fija los campos esperados, si el perfil debe quedar completo y qué campo debe preguntarse.

Tabla: {#tab:golden} Resultados del conjunto de prueba de interpretación (23 casos)

| Métrica | Anthropic (Claude Haiku 4.5, prompt v2) | Sin conexión |
|---|---|---|
| Exactitud global por campo | 98,3 % | 100,0 % |
| Perfil completo o incompleto correcto | 100,0 % | 100,0 % |
| Campo preguntado correcto | 100,0 % | 100,0 % |
| Casos ambiguos o contradictorios con pregunta | 100,0 % | 100,0 % |
| JSON válido | 100,0 % | No aplica |
| Latencia media / máxima | 2674 ms / 3188 ms | 0,8 ms / 2,2 ms |

Con el modelo real, los únicos campos fallados fueron dos clasificaciones del perfil de riesgo (91,3 % de exactitud en ese campo); los montos, horizontes, ahorros, fondos de emergencia y negativas se extrajeron sin error, y todas las preguntas de aclaración fueron las esperadas. El 100 % del modo sin conexión debe leerse con cautela: sus reglas se ajustaron con estos mismos casos, por lo que sobrestima su exactitud ante textos nuevos; su función es servir de respaldo con el mismo contrato. Las explicaciones se validan en cada ejecución con el validador de cifras (sección 2.5.4); cuando el modelo no supera la validación tras un reintento, la plantilla determinista garantiza un texto sin cifras inventadas.

## 5.4. Experimentos sobre el modelo

Los experimentos ejecutan las etapas 3 a 6 del flujo real con los módulos de `ai/` y los parámetros de `data/parameters/`, con 10 semillas por configuración (660 corridas en total) y un monto de S/ 10,000. Se usan tres arquetipos: conservador (λ_base 2, horizonte de 2 años, absorción baja), moderado (λ_base 1, 5 años, absorción media-alta) y agresivo (λ_base 0,5, 12 años, absorción alta).

### 5.4.1. Ablación

Se comparan cuatro configuraciones con los interruptores del servicio: base (sin lógica difusa ni contexto), solo difuso, solo contexto y completo; las configuraciones con contexto usan un panorama político levemente adverso (s_pol = −0,5).

Tabla: {#tab:ablacion} Ablación en el arquetipo agresivo (pesos, E y σ en %)

| Configuración | Acciones | Mixtos | Deuda | Bonos | Plazo fijo | E | σ | λ_ef |
|---|---|---|---|---|---|---|---|---|
| Base | 5,0 | 8,8 | 25,5 | 20,7 | 40,0 | 5,1 | 2,6 | 0,50 |
| Solo difuso | 39,2 | 10,8 | 5,0 | 40,0 | 5,0 | 8,3 | 10,3 | 0,35 |
| Solo contexto | 5,0 | 17,3 | 40,0 | 5,0 | 32,7 | 5,3 | 2,8 | 0,50 |
| Completo | 8,4 | 40,0 | 40,0 | 6,6 | 5,0 | 6,5 | 5,5 | 0,35 |

![{#fig:ablacion} Pesos medios por configuración y arquetipo en la ablación](../../experiments/results/fig_ablation_weights.png)

- **El horizonte difuso es el componente que más mueve los pesos en el arquetipo agresivo:** con H = 12 años (m_H = 0,7) la aversión efectiva baja de 0,5 a 0,35 y las acciones pasan de 5,0 % a 39,2 % (E de 5,1 % a 8,3 %). En el conservador (m_H = 1,5) los pesos no cambian porque el portafolio ya está en su forma más prudente, y en el moderado (m_H = 1) no hay modulación, como corresponde.
- **El contexto adverso reduce la exposición a acciones:** en el agresivo, de 39,2 % (solo difuso) a 8,4 % (completo), con los mixtos en 40,0 %.
- **Estabilidad:** el algoritmo produce el mismo portafolio con las 10 semillas (desviación de los pesos menor que 0,01 puntos porcentuales en 10 de las 12 celdas) y las 120 corridas terminan por convergencia, en 36 a 87 generaciones de media.

### 5.4.2. Escenarios de contexto

Para el arquetipo moderado se combinaron los tres niveles del factor político con los tres del macroeconómico (90 corridas).

Tabla: {#tab:contexto} Efecto del contexto en el arquetipo moderado (pesos, E y σ en %)

| Político | Macro | Acciones | Mixtos | Deuda | Bonos | Plazo fijo | Δ renta variable (pp) | E | σ |
|---|---|---|---|---|---|---|---|---|---|
| −1 | −1 | 5,0 | 5,0 | 40,0 | 10,0 | 40,0 | −3,9 | 4,2 | 2,7 |
| 0 | −1 | 5,0 | 6,7 | 40,0 | 8,3 | 40,0 | −2,3 | 4,8 | 2,1 |
| +1 | −1 | 5,0 | 8,4 | 40,0 | 6,6 | 40,0 | −0,5 | 5,3 | 2,2 |
| −1 | 0 | 5,0 | 5,0 | 40,0 | 10,0 | 40,0 | −3,9 | 4,7 | 2,5 |
| 0 | 0 | 5,0 | 8,9 | 40,0 | 6,1 | 40,0 | 0,0 | 5,3 | 1,9 |
| +1 | 0 | 5,0 | 9,7 | 40,0 | 5,3 | 40,0 | +0,8 | 5,7 | 1,9 |
| −1 | +1 | 5,0 | 5,0 | 40,0 | 10,0 | 40,0 | −3,9 | 5,1 | 2,5 |
| 0 | +1 | 5,0 | 10,0 | 40,0 | 5,0 | 40,0 | +1,1 | 5,8 | 1,9 |
| +1 | +1 | 5,0 | 7,8 | 40,0 | 7,2 | 40,0 | −1,1 | 6,0 | 1,9 |

![{#fig:contexto-exp} Pesos del perfil moderado según el contexto](../../experiments/results/fig_context_shift.png)

Un panorama adverso reduce la renta variable (acciones más mixtos) y uno favorable la mantiene o la aumenta levemente; el factor político pesa más que el macroeconómico, de acuerdo con sus coeficientes. En este perfil los cambios se concentran en el 15 % que queda libre tras el piso y el tope, porque deuda y depósito a plazo permanecen en 40 % y acciones en 5 %; en el agresivo el efecto es mayor (sección 5.4.1).

### 5.4.3. Gen difuso c

Se evaluaron tres situaciones de absorción (baja, media y alta) con λ_base de 0,2 a 2 y horizonte de 5 años (120 corridas), comparando cada caso con el mismo algoritmo sin penalización ni recompensa.

Tabla: {#tab:gen} Negociación del gen c en los casos en que la restricción actúa

| Absorción | λ_base | c | μ_CA(c) | σ | σ_max(c) | σ sin penalización |
|---|---|---|---|---|---|---|
| Baja | 0,2 | 0,205 | 0,778 | 5,9 % | 5,7 % | 11,3 % |
| Baja | 0,5 | 0,169 | 0,778 | 5,0 % | 5,2 % | 5,0 % |
| Media | 0,2 | 0,624 | 0,500 | 11,2 % | 11,1 % | 11,3 % |
| Alta | 0,2 | 0,923 | 1,000 | 11,3 % | 15,0 % | 11,3 % |

![{#fig:gen} Gen c evolucionado frente a la moda y el centroide (arriba) y volatilidades (abajo)](../../experiments/results/fig_gene_c.png)

Cuando la volatilidad que pide el perfil cabe en la zona de pertenencia máxima del conjunto μ_CA, el gen c se ubica en esa zona y no restringe nada. Cuando el perfil pide más volatilidad de la que la capacidad permite (λ_base = 0,2 con absorción baja), c se detiene en el borde de la zona de pertenencia máxima (0,205) y lo que cede es el portafolio: la volatilidad baja de 11,3 % a 5,9 %. Con absorción alta el límite no interviene. Este comportamiento es el de una restricción difusa flexible: el algoritmo busca el mayor nivel de capacidad que los datos del usuario todavía respaldan y recorta el riesgo hasta ese nivel, en lugar de suponer una capacidad que no tiene.

### 5.4.4. Calibración de κ, φ, tope y piso

Se varió un parámetro a la vez (κ ∈ {0,01; 0,03; 0,05}, φ ∈ {10; 50; 200}, tope ∈ {0,35; 0,40; 0,50}, piso ∈ {0; 0,05}) en los arquetipos moderado y agresivo y en un caso de estrés de baja absorción (330 corridas).

![{#fig:calibracion} Efecto de κ, φ y el tope sobre σ y c](../../experiments/results/fig_calibration.png)

- **κ y φ** no cambian ningún peso en el rango probado; κ solo mueve c dentro de la zona de pertenencia máxima. Se mantienen κ = 0,03 y φ = 50, que se encuentran en una zona estable.
- **El tope es el parámetro con mayor efecto.** Con 0,50 reaparece la concentración (85 % en dos categorías, índice de Herfindahl 0,380); con 0,35 el portafolio se diversifica más. Se mantiene 0,40 como punto intermedio.
- **El piso de 5 % cuesta poco:** baja la aptitud entre 0,0002 y 0,0026 y cambia E entre −0,23 y +0,24 puntos porcentuales, a cambio de que ninguna categoría quede en 0 %.
- **Robustez del gen c:** tras la corrección de la inicialización de c (sección 2.9.3), ninguna de las 660 corridas termina con μ_CA(c) = 0 (mínimo 0,5).

## 5.5. Conciliación de los datos con las fuentes

El documento *Evidencia de fuentes de datos* contrasta las páginas oficiales del BCRP y de la SBS con los archivos del repositorio. La comparación valor por valor coincide exactamente en **48 de 48 valores del BCRP y 36 de 36 valores de la SBS** incluidos en los archivos; los 3 valores de la SBS de septiembre de 2026 se excluyeron a propósito porque el mes estaba incompleto en la publicación (datos hasta el 25 de septiembre). El documento incluye además las capturas de cada fuente, las primeras filas de cada archivo y su huella SHA-256, de modo que cualquier lector puede verificar que los datos usados son los publicados.
