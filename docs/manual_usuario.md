# Manual de Usuario — InvestWise (Recomendador de Inversión con IA)

Guía para usar la aplicación desde el navegador. No se necesita ningún
conocimiento financiero ni técnico.

> ⚠️ **Aviso permanente:** InvestWise es una herramienta **educativa** con
> fines académicos. **No es asesoría financiera real.** Antes de invertir
> dinero de verdad, consulte con un asesor certificado.

---

## 1. ¿Qué hace la aplicación?

Usted describe su situación **con sus propias palabras** (sin formularios
rígidos) y el sistema le sugiere cómo repartir su dinero entre 5 categorías
de inversión del mercado peruano:

1. **Fondos de acciones** — inversiones en empresas; mayor potencial de
   ganancia, pero también mayor variabilidad.
2. **Fondos mixtos** — combinan acciones y renta fija.
3. **Fondos de deuda** — renta fija; más predecibles y de menor riesgo.
4. **Bonos soberanos (BTP)** — préstamos al Estado peruano; bajo riesgo.
5. **Depósito a plazo fijo** — ahorro bancario con tasa pactada; el más estable.

Las categorías son **representativas** (promedios históricos de referencia del
mercado peruano), no productos específicos de ningún banco o entidad.

## 2. Paso a paso

### Paso 1 — Cuente su situación

En el cuadro de texto inicial, escriba libremente. Para una recomendación
completa, mencione:

- **Cuánto quiere invertir** (en soles): *"quiero invertir S/ 5,000"*.
- **Por cuánto tiempo no necesitará el dinero**: *"unos 3 años"* o
  *"a largo plazo"*.
- **Su disposición al riesgo**: *"no me gusta arriesgar"*, *"soy moderado"*,
  *"soy agresivo"*.
- **Sus ahorros totales** (para saber qué parte compromete): *"de mis
  S/ 20,000 de ahorro"*.
- **Su fondo de emergencia**: *"puedo cubrir 6 meses de mis gastos"*.

**Ejemplo completo (puede copiarlo):**

```
Tengo 30 años, quiero invertir S/ 5000 de mis S/ 20000 de ahorro,
no me gusta arriesgar mucho y no los necesitaré por unos 3 años,
tengo un fondo de emergencia para 4 meses
```

Pulse **Obtener recomendación** (o la tecla Enter).

### Paso 2 — Preguntas de aclaración (si hace falta)

Si falta información importante, el sistema **no inventa valores**: le hará una
pregunta específica, por ejemplo *"¿Por cuánto tiempo aproximadamente no
necesitarías este dinero?"*. Responda con sus palabras y pulse **Responder**.

Si le preguntan datos que prefiere no dar (ahorros totales, fondo de
emergencia), puede escribir **"prefiero no decirlo"**: el sistema continuará
con un supuesto medio y **se lo dirá claramente** en la explicación final.

### Paso 3 — Lea su recomendación

La respuesta incluye:

- **Explicación en lenguaje simple**: la distribución sugerida con montos
  concretos en soles (*"aproximadamente S/ 1,250 de tus S/ 5,000"*), el
  rendimiento esperado en un año promedio, un **escenario de año malo**, cómo
  influyeron su plazo y su capacidad de asumir pérdidas, y los supuestos de
  contexto usados.
- **Gráfico y tabla del portafolio**: peso (%) y monto aproximado por categoría.
- **Gráfico de convergencia**: cómo el algoritmo genético fue mejorando su
  propuesta generación a generación.
- **"Ver detalle técnico"** (opcional, colapsado): valores exactos de cada
  módulo (λ, pertenencias difusas, ajustes de contexto, matriz de covarianza,
  descomposición del fitness), pensado para usuarios avanzados y evaluadores.

## 3. Panel de factores de contexto

El entorno también importa. Con este panel usted puede explorar escenarios:

| Factor | Posiciones | Efecto general |
|---|---|---|
| **Panorama político** | Adverso / Neutral / Favorable | Adverso: baja los retornos esperados y sube el riesgo (más en acciones). Favorable: sube retornos (el riesgo no baja, por prudencia). |
| **Estabilidad económica** | Adverso / Neutral / Favorable | Similar, ligado a inflación y tasas. |

- Por defecto todo está en **Neutral** (la recomendación se basa en los
  promedios históricos).
- Hay un deslizador para ajustes intermedios (de −1 a +1).
- **No son predicciones**: son supuestos ajustables que usted controla; la
  explicación siempre declara cuáles están activos.
- Si cambia un factor después de obtener una recomendación, el sistema
  **recalcula automáticamente**.

### Opciones avanzadas (pruebas de ablación)

Dentro del panel, el desplegable *"Opciones avanzadas"* permite activar o
desactivar por separado dos módulos, para comparar resultados:

- **Ajuste gradual del perfil (lógica difusa)** — transiciones suaves según el
  plazo y la capacidad de asumir pérdidas.
- **Ajuste por contexto** — los factores ambientales del punto anterior.

## 4. Consejos y preguntas frecuentes

- **"Tengo 30 años"** no se confunde con el plazo: el sistema distingue la
  edad del horizonte de inversión.
- Puede usar montos con o sin símbolo: *"S/ 5000"*, *"5000 soles"*,
  *"5 mil soles"*, *"mis ahorros son 30000"*.
- Si escribe algo muy distinto de una situación de inversión, el sistema le
  pedirá los datos que faltan en lugar de adivinar.
- **Nueva consulta** borra la conversación y los resultados para empezar de cero.
- La explicación puede generarse en modo **API** (si se configuró una clave de
  LLM en el backend) u **offline** (determinista); el modo usado se indica
  debajo de la explicación.

## 5. ¿Qué NO hace la aplicación?

- No recomienda productos específicos de ninguna entidad financiera.
- No ejecuta inversiones ni se conecta a cuentas bancarias o de corretaje.
- No usa datos de mercado en tiempo real (usa promedios históricos de
  referencia, actualizables).
- No predice el futuro político ni económico: los factores de contexto son
  escenarios que usted mismo configura.
- No reemplaza a un asesor financiero certificado.
