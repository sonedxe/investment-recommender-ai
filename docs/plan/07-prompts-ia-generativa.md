# 07 · Prompts de la IA generativa

Diseño de las dos intervenciones del LLM: **interpretación** (texto del usuario → perfil estructurado o pregunta) y **explicación** (resultado calculado → texto en lenguaje simple). Implementa las tareas T6.2–T6.5.

## 1. Principios

| Principio | Aplicación |
|---|---|
| El LLM interpreta y redacta; **el código decide y calcula** | El LLM extrae datos y escribe texto. La completitud, λ, el portafolio y las cifras los define el código. |
| Salida estructurada siempre | Ambas llamadas devuelven JSON validado contra un esquema (structured outputs / tool use, según el proveedor). |
| Nada se supone en silencio | Un dato no dicho es `null`, nunca un valor inventado. |
| El LLM no inventa cifras | La explicación recibe las cifras calculadas y solo puede citar esas; un validador lo verifica. |
| Prompts versionados | Archivos en `ai/generative/prompts/` con versión (`interpret.v1.md`, `explain.v1.md`); la versión se registra en cada respuesta. |
| Mismo contrato en offline | El adaptador offline devuelve el mismo JSON con reglas deterministas (expresiones regulares + plantillas). |

## 2. Interpretación

### 2.1. Flujo

```
texto + historial
      │
      ▼
LLM: extracción (JSON)  ──>  código: ¿faltan campos críticos?
                                  │ sí                     │ no
                                  ▼                        ▼
                     pregunta para el PRIMER        perfil completo
                     campo faltante (prioridad)     → /api/recommend
```

El LLM **no decide** si el perfil está completo: el código revisa los campos y elige qué preguntar. El LLM solo redacta la pregunta en lenguaje natural, o se usa una plantilla.

**Campos críticos, en orden de prioridad:** `monto_invertir` → `horizonte` → `perfil_riesgo`.
**Campos de absorción:** `ahorro_total`, `cobertura_emergencia_meses`. Se preguntan una vez; si el usuario se niega, se asume "Media" y se declara.

### 2.2. Esquema de salida

```json
{
  "monto_invertir": 5000,
  "horizonte_anios": 3,
  "horizonte_etiqueta": null,
  "perfil_riesgo": "conservador",
  "ahorro_total": 20000,
  "cobertura_emergencia_meses": null,
  "evidencia": {
    "monto_invertir": "quiero invertir S/ 5000",
    "horizonte": "no los necesito en unos 3 años",
    "perfil_riesgo": "no me gusta arriesgar mucho",
    "ahorro_total": "de mis S/ 20000"
  },
  "rechazos": [],
  "contradicciones": []
}
```

| Campo | Tipo | Regla |
|---|---|---|
| `monto_invertir`, `ahorro_total` | número (soles) o `null` | "5 mil" → 5000; si viene en dólares → `null` y contradicción "moneda" |
| `horizonte_anios` | número o `null` | Solo si el usuario dio una cifra ("unos 3 años" → 3) |
| `horizonte_etiqueta` | `"corto" \| "mediano" \| "largo"` o `null` | Solo si no hay cifra ("a largo plazo") |
| `perfil_riesgo` | enum de 5 valores ([10 · D5](../analisis/10-decisiones-d1-d2-d5.md#d5--escala-de-λ_base)) o `null` | `null` si hay señales contradictorias |
| `cobertura_emergencia_meses` | número o `null` | "tengo un colchón de 4 meses" → 4 |
| `evidencia` | frase textual por campo | Obligatoria para cada campo no nulo |
| `rechazos` | lista de campos | El usuario dijo explícitamente que no quiere responder |
| `contradicciones` | lista de textos | Ej.: "máxima ganancia" + "no puedo perder nada" |

### 2.3. Prompt de sistema (`interpret.v1.md`)

```text
Eres el componente de interpretación de InvestWise, una herramienta educativa que
reparte un monto en soles entre cinco categorías de inversión del mercado peruano.

Tu única tarea es EXTRAER datos del mensaje del usuario y del historial. No das
consejos, no recomiendas inversiones y no calculas nada.

Reglas:
1. Si un dato no aparece de forma explícita o claramente inferible, devuélvelo como
   null. Nunca inventes ni supongas valores.
2. Para cada dato que no sea null, copia en "evidencia" la frase exacta del usuario
   que lo respalda.
3. Montos: conviértelos a número en soles ("5 mil" = 5000). Si el monto está en
   otra moneda, devuelve null y anótalo en "contradicciones".
4. Horizonte: si hay una cifra, usa "horizonte_anios"; si solo hay una expresión
   ("a largo plazo"), usa "horizonte_etiqueta" con corto, mediano o largo.
5. Perfil de riesgo: clasifica en muy_agresivo, agresivo, moderado, conservador o
   muy_conservador según cómo describe su relación con el riesgo. Si hay señales
   opuestas, devuelve null y descríbelas en "contradicciones".
6. Si el usuario dice que no quiere dar un dato, agrégalo a "rechazos".
7. El historial contiene preguntas anteriores del sistema y respuestas del usuario:
   combina toda la información; la respuesta más reciente prevalece.

Responde solo con el JSON del esquema.
```

### 2.4. Ejemplos few-shot (incluidos en el prompt)

| Entrada | Salida clave |
|---|---|
| "Tengo 30 años y quiero invertir S/ 5000, no me gusta arriesgar" | monto 5000, perfil conservador, horizonte `null` |
| "Para dentro de unos añitos, nada muy arriesgado" | horizonte `null` (vago), perfil moderado o conservador con evidencia |
| "Quiero la máxima ganancia pero no puedo perder nada" | perfil `null`, contradicción registrada |
| "Prefiero no decir cuánto tengo ahorrado" | `rechazos: ["ahorro_total"]` |

### 2.5. Prompt de la pregunta de aclaración

El código pasa el campo faltante y el contexto; el LLM devuelve `{ "pregunta": "...", "ayuda": "..." }`.

```text
Redacta UNA pregunta corta, amable y en español neutro (tuteo) para obtener el dato
"{campo}". El usuario no sabe de finanzas: no uses jerga. Si existe, usa este
contexto: {contexto}. Agrega una ayuda opcional de una línea con un ejemplo de
respuesta. No saludes ni te presentes.
```

**Plantillas de respaldo** (offline o si falla el LLM):

| Campo | Pregunta |
|---|---|
| `monto_invertir` | ¿Cuánto dinero quieres invertir, en soles? |
| `horizonte` | ¿Por cuánto tiempo aproximadamente no necesitarías este dinero? |
| `perfil_riesgo` | Si en un año malo tu inversión bajara un 10 %, ¿cómo te sentirías? (opciones) |
| `ahorro_total` | Aparte de este monto, ¿cuánto tienes ahorrado en total? |
| `cobertura_emergencia_meses` | Si dejaras de recibir ingresos, ¿cuántos meses podrías cubrir tus gastos con tus ahorros? |

## 3. Explicación

### 3.1. Entrada (la arma el código)

```json
{
  "monto_total": 5000,
  "portafolio": [
    {"categoria": "Fondos de acciones", "peso": 0.02, "monto": 100},
    {"categoria": "Depósito a plazo fijo", "peso": 0.40, "monto": 2000}
  ],
  "escenarios": [
    {"nombre": "año malo", "monto": -150},
    {"nombre": "año normal", "monto": 260}
  ],
  "perfil": {"perfil_riesgo": "conservador", "horizonte_anios": 3},
  "efectos_difusos": {
    "horizonte": "corto-mediano; el sistema fue más cauteloso",
    "absorcion": "media; se aceptó una variabilidad moderada"
  },
  "supuestos": ["Se asumió un panorama político neutral."],
  "cifras_permitidas": [5000, 100, 2000, 150, 260, 2, 40]
}
```

Los escenarios se calculan en el código (p. ej., año malo = E − 1.65·σ sobre el monto); el LLM no los estima.

### 3.2. Esquema de salida (coincide con `ExplanationTextProps`)

```json
{
  "resumen": "una oración",
  "parrafos": ["3 a 6 párrafos cortos"],
  "escenarios": [{"label": "En un año malo", "text": "...", "amount": -150}],
  "supuestos": ["..."]
}
```

### 3.3. Prompt de sistema (`explain.v1.md`)

```text
Eres el redactor de InvestWise, una herramienta educativa. Explicas a una persona
sin conocimientos financieros el portafolio que ya calculó el sistema. No
recalculas nada ni cambias la recomendación.

Reglas obligatorias:
1. Usa solo las cifras de "cifras_permitidas". No escribas ningún otro número.
2. Todo porcentaje va acompañado de su monto en soles (formato S/ 1,250.00).
3. Ningún término técnico sin traducción inmediata en la misma oración
   (ej.: "renta fija, es decir, inversiones más predecibles").
4. Explica el riesgo con los escenarios dados, no con la palabra "riesgo" sola.
5. Di en una o dos frases cómo influyeron el horizonte y la capacidad de absorber
   pérdidas, usando "efectos_difusos", sin nombrar la técnica.
6. Declara todos los "supuestos" como supuestos ajustables, nunca como predicciones.
7. Nombra las categorías con su descripción (ej.: "fondos de acciones, inversiones
   en empresas con más potencial de ganancia y más variabilidad").
8. Español neutro, tuteo, frases cortas. Sin emojis, sin saludo, sin presentarte.
9. No digas que es una recomendación personal ni asesoría financiera.

Responde solo con el JSON del esquema.
```

### 3.4. Validación posterior

1. Extraer todos los números del texto generado.
2. Comprobar que cada uno está en `cifras_permitidas` (tolerancia de redondeo).
3. Verificar el formato de moneda y que existan los supuestos.
4. **Si falla:** reintentar una vez con el error indicado; si vuelve a fallar, usar la **plantilla determinista** de explicación (la misma del modo offline).
5. El aviso educativo **no** lo genera el LLM: lo agrega siempre la interfaz.

## 4. Parámetros de llamada

| Llamada | Temperatura | Máximo de tokens | Reintentos |
|---|---|---|---|
| Interpretación | 0 | ~500 | 1 (JSON inválido) |
| Pregunta de aclaración | 0.3 | ~150 | 0 (plantilla de respaldo) |
| Explicación | 0.3 | ~1200 | 1 (validación fallida) |

Modelo y forma de forzar el JSON dependen del proveedor (decisión D4). El puerto `LanguageModel` expone `complete_json(system, messages, schema)`, y cada adaptador lo implementa con el mecanismo nativo de su proveedor.

## 5. Evaluación

El golden set (T6.5, ver [03](03-estrategia-de-pruebas.md#golden-set-de-ia-generativa)) se corre contra cada versión de prompt. Un cambio de prompt solo se acepta si no empeora:

- exactitud por campo de la interpretación;
- 100 % de casos ambiguos o contradictorios → pregunta (nunca suposición);
- 100 % de explicaciones que pasan la validación de cifras.
