# 06 · Frontend

Plan de la interfaz gráfica a partir del design system generado en Claude web.

> Fuente del diseño: <https://claude.ai/artifact/HDhLD15WouGDnREwjNgApw> (design system "InvestWise", 32 componentes, tokens claro/oscuro, tipos en `components/index.d.ts`).

## 1. Qué trae el design system

| Aspecto | Contenido |
|---|---|
| Estilo | Editorial y sobrio: blanco roto cálido, un solo acento (verde petróleo `#1f5c5a`), bordes finos, sin sombras, sin íconos ni emojis |
| Tipografía | Source Serif 4 (títulos) + Source Sans 3 (interfaz), cifras tabulares |
| Tokens | Color (2 temas), tipografía, espaciado `space-1`…`space-9`, radios, bordes, una sombra reservada |
| Categorías | `stocks`, `mixed`, `debt`, `bonds`, `term` con color desaturado propio |
| Accesibilidad | AA en ambos temas, foco visible, radios nativos, gráficos con `title`/`desc` y tabla equivalente |
| Responsive | Container queries, desde 360 px hasta 1120 px de contenido |
| Código | `bundle.js` (script clásico que expone `window.InvestWise`), `bundle.css`, tipos en `index.d.ts`, datos de ejemplo |

### Inventario por atomic design

| Nivel | Componentes |
|---|---|
| Átomos | `Button`, `Badge`, `CategoryDot`, `Money`, `ProgressLine`, `TextArea`, `DisclaimerNotice` |
| Moléculas | `AllocationRow`, `AllocationBar`, `DataPoint`, `FactorSelector`, `QuestionField`, `StatusBanner`, `AssumptionList`, `LoadingState` |
| Organismos | `AppHeader`, `AllocationBreakdown`, `UnderstoodPanel`, `ClarificationForm`, `ExplanationText`, `ContextPanel`, `ParameterTable`, `MembershipChart`, `AbsorptionChart`, `ConvergenceChart`, `RulesTable`, `ScoreBreakdown`, `TechnicalDetail` |
| Pantallas | `HomeScreen`, `ClarificationScreen`, `ResultScreen`, `ContextScreen` |

## 2. Contraste con los contratos del backend

| Dato del contrato ([01](01-arquitectura.md#contratos-entre-módulos)) | ¿Lo cubre el diseño? | Nota |
|---|---|---|
| Pesos + montos por categoría | ✅ `AllocationItem` | — |
| Pregunta de aclaración + datos entendidos | ✅ `ClarificationForm`, `UnderstoodItem` | Incluye estado `assumed` para el supuesto declarado |
| Supuestos | ✅ `AssumptionList` | — |
| Explicación + escenarios en S/ | ✅ `ExplanationText`, `Scenario` | — |
| Factores de contexto + antes/después | ✅ `ContextPanel` | — |
| μ, σ originales y ajustados | ✅ `ParamRow` | Falta el ajuste `cᵢ` explícito (se puede derivar) |
| λ_base, λ_ef | ✅ `TechnicalData` | Falta `m_H` |
| Pertenencias del horizonte | ✅ `MembershipChart` | — |
| `μ_CA`, gen `c`, centroide | ✅ `AbsorptionChart` | Falta mostrar el valor `μ_CA(c)` y las entradas `r` y `E` |
| Reglas activadas | ⚠️ `Rule` con `condition`/`effect` en texto | **Falta el grado de activación α** y distinguir reglas difusas (RH, RA) de reglas de contexto (RC) |
| Desglose del fitness | ✅ `ScoreBreakdown` | — |
| Historial de convergencia | ✅ `ConvergenceChart` | — |
| Interruptores (ablación) | ❌ | Opcional: útil para mostrar la ablación en la exposición |

## 3. Ajustes al design system

| ID | Ajuste | Motivo |
|---|---|---|
| A1 | `Rule`: agregar `kind: 'horizon' \| 'absorption' \| 'context'` y `activation?: number` | El docente evalúa los grados de activación de las reglas (paso 2 del FIS) |
| A2 | `AbsorptionChart`: agregar `membershipAtC` y las entradas `r`, `E` | Mostrar por qué el AG eligió ese `c` |
| A3 | `TechnicalData`: agregar `mH` | Completar la explicación del ajuste por horizonte |
| A4 | Renombrar el tipo `Tri` a `ContextLevel` | En el código, `tri()` es la función de pertenencia triangular; evita confusión |
| A5 | (Opcional) `ParamRow`: agregar `contextAdj` (cᵢ) | Hacer visible el efecto de las reglas de contexto por categoría |
| A6 | (Opcional) Interruptores de difuso y contexto en el detalle técnico | Demo de ablación en vivo |

**Decisión:** el código del repo es la fuente de verdad. Los ajustes se hacen solo ahí; el design system queda como referencia visual congelada (estilo, tokens, composición de pantallas). No se sincroniza: mantener dos copias del mismo componente duplica trabajo sin aportar a la evaluación.

## 4. Integración en el repo

### Estrategia

El `bundle.js` del design system es un script clásico pensado para las previews; no se importa tal cual. Se **portan** los componentes a TSX dentro de `frontend/src/components/`, usando `index.d.ts` como contrato de props y `bundle.css` + `tokens.json` como fuente de estilos.

### Estructura

```
frontend/src/
├── styles/
│   ├── tokens.css         # generado desde tokens.json (variables CSS por tema)
│   └── base.css           # iw-root, iw-cq, iw-screen, tipografía
├── components/
│   ├── atoms/
│   ├── molecules/
│   ├── organisms/
│   └── screens/           # HomeScreen, ClarificationScreen, ResultScreen, ContextScreen
├── containers/            # estado, llamadas a la API, mapeo a props
│   ├── AppContainer.tsx   # máquina de estados del flujo
│   ├── HomeContainer.tsx
│   ├── ClarificationContainer.tsx
│   ├── ResultContainer.tsx
│   └── ContextContainer.tsx
├── api/
│   ├── client.ts          # fetch a /api/*
│   └── mappers.ts         # contrato del backend -> props del design system
├── types/                 # index.d.ts portado + tipos de la API
└── fixtures/              # datos de ejemplo (window.InvestWise.sample portado)
```

### Flujo (máquina de estados, sin router)

```
input ──submit──> interpreting ──completo=false──> clarifying ──respuesta──> interpreting
                       │                                                         │
                       └──────────────completo=true──────────────> calculating <─┘
                                                                        │
                                              result <──────────────────┘
                                                │  ▲
                                         ajustar│  │volver / recalcular
                                                ▼  │
                                              context
error y offline: estados transversales (StatusBanner, AppHeader offline)
```

### Convenciones

- Los IDs de categoría (`stocks`, `mixed`, `debt`, `bonds`, `term`) pasan a ser los **canónicos en todo el sistema**, backend incluido.
- La API devuelve JSON en inglés `snake_case`; `api/mappers.ts` lo convierte a las props `camelCase` del diseño. Ningún componente presentacional conoce la API.
- Porcentajes: el backend envía pesos en [0, 1]; el mapper los convierte a `pct` 0–100.
- Gráficos: SVG propio, como en el design system, en vez de una librería; ya están diseñados así y son accesibles.

## 5. Tareas (reemplazan F7 de [02](02-fases-y-tareas.md#f7--interfaz-gráfica--frontend))

| ID | Tarea | Criterio de aceptación | Depende de |
|---|---|---|---|
| T7.0 | Tokens y estilos base: `tokens.css` generado desde `tokens.json`, `base.css`, fuentes de Google, cambio de tema | Ambos temas se ven idénticos a las previews | — |
| T7.1 | Portar átomos y moléculas a TSX con tipos | Cada componente renderiza con `fixtures/` | T7.0 |
| T7.2 | Portar organismos, incluidos los gráficos SVG, aplicando los ajustes A1–A4 | Gráficos con `title`/`desc` y tabla equivalente | T7.1 |
| T7.3 | Portar las 4 pantallas | Coinciden con las previews en escritorio y en 360 px | T7.2 |
| T7.4 | `api/client.ts` + `api/mappers.ts` con tests unitarios | Un JSON de ejemplo del backend se mapea a las props correctas | T5.2 |
| T7.5 | Contenedores y máquina de estados del flujo | Recorrido completo inicio → aclaración → resultado → contexto | T7.3, T7.4 |
| T7.6 | Estados transversales: calculando, error, modo offline, entrada vacía | Reproducen la galería de estados | T7.5 |
| T7.7 | Revisión de accesibilidad y responsive | Navegación por teclado completa; contraste AA; sin scroll horizontal en 360 px | T7.6 |
| T7.8 | (Opcional) Interruptores de ablación (A6) | Se recalcula con difuso/contexto apagados | T7.5 |

**Mínimo para la semana 6:** T7.0–T7.5 con pantallas de inicio, aclaración y resultado. **Semana 7:** contexto, detalle técnico completo, T7.6–T7.7.
