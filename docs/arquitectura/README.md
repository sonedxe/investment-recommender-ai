# Arquitectura · diagramas

Diagramas para el informe técnico y la exposición, con la paleta y la tipografía de la interfaz.

| Archivo | Contenido |
|---|---|
| `01-componentes.svg` / `.png` | Componentes: interfaz gráfica → API y orquestación → núcleo de IA (IA generativa, razonamiento bajo incertidumbre, algoritmo heurístico, reglas de contexto) → datos versionados y servicios externos |
| `02-flujo.svg` / `.png` | Flujo de una recomendación en 8 etapas, con el conjunto difuso del horizonte en el **fitness** y el de la capacidad de absorción en el **cromosoma** (gen `c`) |

- **SVG:** vectorial, para el informe en PDF o las diapositivas (se ve nítido a cualquier tamaño).
- **PNG:** a 2× de resolución, para pegar en Word o Google Docs.

## Regenerar

Los SVG se generan con código, así que se editan en `build_diagrams.py` y no a mano:

```bash
python3 docs/arquitectura/build_diagrams.py
```

Para exportar un PNG, envolver el SVG en un HTML que cargue las fuentes (Source Sans 3, Source Serif 4, Source Code Pro de Google Fonts) y capturarlo con Chromium:

```bash
chromium --headless=new --hide-scrollbars --force-device-scale-factor=2 \
  --window-size=1400,1180 --virtual-time-budget=8000 \
  --screenshot=docs/arquitectura/02-flujo.png file:///ruta/al/02-flujo.html
```

Alto de la ventana: 1110 px para `01-componentes` y 1180 px para `02-flujo`.
