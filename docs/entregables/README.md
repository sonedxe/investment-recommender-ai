# Entregables

| Archivo | Contenido |
|---|---|
| [`Manual_de_Instalacion_InvestWise.pdf`](Manual_de_Instalacion_InvestWise.pdf) | Manual de instalación: requisitos, backend en Linux, macOS y Windows, frontend, `.env` y proveedor de IA generativa (offline, Anthropic u OpenAI), ejecución, verificación, herramientas opcionales y problemas frecuentes. |
| [`Manual_de_Usuario_InvestWise.pdf`](Manual_de_Usuario_InvestWise.pdf) | Manual de usuario: qué hace la aplicación, cómo describir tu situación, preguntas de aclaración, lectura del resultado, contexto, detalle técnico, tema, modo sin conexión, uso en el celular, preguntas frecuentes y glosario. |
| [`build_manuals.py`](build_manuals.py) | Script que genera ambos PDF a partir de `docs/manuales/*.md` y `docs/manuales/img/`. |

Los PDF tienen portada, índice con número de página, figuras numeradas y pie de página. El contenido se edita **solo** en los Markdown de [`docs/manuales/`](../manuales/README.md); los PDF se regeneran a partir de ellos.

## Cómo regenerar los PDF

Requisitos: Chromium o Google Chrome en el `PATH` y un entorno de Python aparte con `markdown` y `pypdf` (no forman parte de `requirements.txt`).

```bash
python3 -m venv /tmp/claude-1000/docs-venv
/tmp/claude-1000/docs-venv/bin/pip install markdown pypdf
/tmp/claude-1000/docs-venv/bin/python docs/entregables/build_manuals.py
```

El script:

1. Convierte cada Markdown a HTML, usa el primer título como portada, numera las figuras ("Figura N.") a partir del texto alternativo de cada imagen y arma el índice con los títulos de nivel 2 y 3.
2. Aplica una hoja de estilos de impresión A4 con la tipografía del sistema de diseño (Source Serif 4, Source Sans 3 y Source Code Pro, descargadas una vez de Google Fonts a una caché temporal; sin red usa fuentes del sistema).
3. Imprime a PDF con Chromium sin interfaz dos veces: la primera ubica la página de cada título y la segunda escribe esos números en el índice. El pie de página ("InvestWise · Manual de … · página N") sale de las cajas de margen de CSS `@page`.

`--keep-html` deja el HTML intermedio en `docs/entregables/build/` para revisarlo.

Las capturas de `docs/manuales/img/` se tomaron de la aplicación real; si la interfaz cambia, vuelve a capturarlas antes de regenerar.
