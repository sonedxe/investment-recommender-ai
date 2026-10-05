# 07 · El feedback del docente, explicado

Explicación conceptual del feedback de la semana 5 y de su relación con lo que el equipo tenía. Complementa [02-feedback-docente.md](02-feedback-docente.md), que resume la brecha de forma técnica.

> **Aviso:** esta es una interpretación de la frase del docente tal como la registró el equipo. Conviene confirmarla con él antes de implementar el algoritmo genético.

## 1. Lo que había en la semana 5

```
Usuario dice "no me gusta arriesgar"
        │
        ▼
IA generativa lo traduce a un número fijo: λ = 2
        │
        ▼
Algoritmo genético
  · cada individuo (cromosoma) = [w1, w2, w3, w4, w5]  ← solo pesos
  · cada individuo se califica con: Fitness = E − λ·σ
```

Dos problemas:

- **Todo era nítido.** "No me gusta arriesgar" pasaba a λ = 2 de golpe, sin matices. Una persona con 2.9 años de horizonte y otra con 3.1 caían en categorías distintas, aunque en la realidad son casi iguales.
- **Los módulos solo se pasaban números.** El bayesiano calculaba μ y σ y se los entregaba al genético. No había integración real entre ellos.

## 2. Lo que dijo el docente

> "Un conjunto difuso en la evaluación/fitness y otro como componente de la cadena genética."

En un algoritmo genético hay dos piezas distintas:

| Pieza | Qué es | Analogía |
|---|---|---|
| **La evaluación (fitness)** | La fórmula que califica a cada individuo | El **jurado** que pone la nota |
| **La cadena genética (cromosoma)** | Lo que cada individuo *es*: lo que se cruza y muta | El **ADN** del individuo |

El docente pidió lógica difusa **en las dos piezas**.

### 2.1. Un conjunto difuso en el jurado (fitness)

La nota de cada portafolio debe calcularse con razonamiento difuso, no con un número fijo. Ejemplo: "unos 3 años" pertenece un poco a "corto" y un poco a "mediano", y eso ajusta λ de forma gradual.

✅ **La v1.1 ya lo hace** con el horizonte temporal: `λ_ef = λ_base · m_H` (ver [08-horizonte-temporal.md](08-horizonte-temporal.md)).

### 2.2. Otro conjunto difuso en el ADN (cromosoma)

El cromosoma debe llevar un gen cuyo significado sea difuso, y el algoritmo genético debe evolucionarlo igual que a los pesos: cruzarlo, mutarlo y seleccionarlo. Así el genético no recibe lo difuso ya resuelto desde afuera: lo **explora** como parte de la búsqueda.

❌ **La v1.1 no lo hace.** La capacidad de absorción terminó también en el jurado (como `σ_max`, un parámetro del fitness) y el cromosoma sigue siendo solo `[w1..w5]`.

### 2.3. Por qué lo pediría

- El enunciado exige una "interacción coordinada" entre los módulos. Si lo difuso solo calcula un número antes de correr el genético, es un paso previo pegado, no una integración. Con un gen difuso, los dos módulos trabajan dentro de la misma búsqueda.
- En la clase de algoritmos genéticos, el docente lista "aprendizaje de reglas de lógica difusa" como aplicación: la combinación está en su propio material.

## 3. La segunda parte: reglas de contexto

El docente pidió que factores del entorno (panorama político, tendencia o precedente de cada campo de inversión, cada uno con un valor por defecto) influyan **directamente** en la función de aptitud.

Hasta la semana 5, la nota de un portafolio dependía solo de la estadística histórica y del perfil del usuario: el mundo exterior no existía.

✅ **La v1.1 lo resuelve** con las reglas RC1–RC7, que ajustan el retorno y el riesgo esperados de cada categoría. No queda "por definir": está diseñado. Falta implementarlo y calibrar los parámetros con fuentes.

## 4. Lo que propuso el equipo y dónde quedó

En clase, el equipo propuso dos conjuntos difusos (capacidad de absorción y horizonte temporal) y dijo que ambos influían en λ. Hay dos problemas:

1. **Ambos quedaban en el jurado** y ninguno en el ADN, que es justo lo que el docente pidió separar.
2. **El informe no coincide con lo dicho:** en la v1.1, la absorción no toca λ, sino `σ_max`. El discurso del equipo debe unificarse antes de la exposición.

## 5. Resumen

| Pedido del docente | Semana 5 | v1.1 | Propuesta |
|---|---|---|---|
| Difuso en el fitness | ❌ λ fijo | ✅ Horizonte → λ_ef | ✅ Se mantiene |
| Difuso en el cromosoma | ❌ | ❌ Absorción también en el fitness | ✅ Absorción → gen `c` en `[w1..w5 \| c]` |
| Reglas de contexto | ❌ | ✅ RC1–RC7 | ✅ Como base de reglas explícita |

De los tres pedidos, la v1.1 cumple dos. Falta justamente el más original: el conjunto difuso dentro del cromosoma. La propuesta para resolverlo está en [04-propuesta-difusa-cromosoma.md](04-propuesta-difusa-cromosoma.md).
