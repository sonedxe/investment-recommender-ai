# Entregables

| Archivo | Contenido |
|---|---|
| [`Informe_Tecnico_de_Desarrollo_InvestWise.pdf`](Informe_Tecnico_de_Desarrollo_InvestWise.pdf) | Informe técnico de desarrollo: introducción, descripción de funcionalidades, arquitectura de software inteligente con el detalle de cada componente, población que puede usar el sistema, ventajas frente a otros softwares, resultados y validación, y anexos de parámetros, fuentes de datos y decisiones de diseño. |
| [`Manual_de_Instalacion_InvestWise.pdf`](Manual_de_Instalacion_InvestWise.pdf) | Manual de instalación: requisitos, backend en Linux, macOS y Windows, frontend, `.env` y proveedor de IA generativa (offline, Anthropic u OpenAI), ejecución, verificación, herramientas opcionales y problemas frecuentes. |
| [`Manual_de_Usuario_InvestWise.pdf`](Manual_de_Usuario_InvestWise.pdf) | Manual de usuario: qué hace la aplicación, cómo describir tu situación, preguntas de aclaración, lectura del resultado, contexto, detalle técnico, tema, modo sin conexión, uso en el celular, preguntas frecuentes y glosario. |
| [`build_manuals.py`](build_manuals.py) | Script que genera los tres PDF. |

Los PDF tienen la portada académica del equipo, índice con número de página, figuras numeradas y pie de página. El contenido se edita **solo** en los Markdown: [`docs/manuales/`](../manuales/README.md) para los manuales y [`docs/informe/`](../informe/README.md) para el informe técnico, que reemplaza a la antigua *Descripción de funcionalidades* (ahora su capítulo 1). Los PDF se regeneran a partir de ellos.

## Cómo regenerar los PDF

Requisitos: Chromium o Google Chrome en el `PATH` y un entorno de Python aparte con `markdown` y `pypdf` (no forman parte de `requirements.txt`).

```bash
python3 -m venv /tmp/claude-1000/docs-venv
/tmp/claude-1000/docs-venv/bin/pip install markdown pypdf
/tmp/claude-1000/docs-venv/bin/python docs/entregables/build_manuals.py
```

El script:

1. Concatena, para cada documento, una lista ordenada de fuentes Markdown en un solo cuerpo y lo convierte a HTML. En los manuales el primer título es la portada y el índice usa los títulos de nivel 2 y 3; en el informe cada `# ` es un capítulo que empieza en página nueva y el índice usa los niveles 1 y 2, seguido de un índice de figuras y uno de tablas.
2. Numera las figuras ("Figura N.") a partir del texto alternativo de cada imagen y las tablas ("Tabla N.") a partir del párrafo `Tabla: …` que las precede, y resuelve las referencias `@fig:clave` y `@tab:clave` (convenciones en [`docs/informe/README.md`](../informe/README.md)).
3. Aplica una hoja de estilos de impresión A4 con tipografía serif negra del sistema (Times New Roman o Liberation Serif) y la portada académica del equipo.
4. Imprime a PDF con Chromium sin interfaz en varias pasadas: la primera ubica la página de cada título, figura y tabla, y la última escribe esos números en los índices. El pie de página ("<Documento> — N") sale de las cajas de margen de CSS `@page`.

`--keep-html` deja el HTML intermedio en `docs/entregables/build/` para revisarlo.

Las capturas de `docs/manuales/img/` se tomaron de la aplicación real; si la interfaz cambia, vuelve a capturarlas antes de regenerar. Las figuras de `docs/informe/img/` se generan con `docs/informe/build_figures.py`.
