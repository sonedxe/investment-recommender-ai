# Informe técnico de desarrollo

Fuentes en Markdown del entregable [`Informe_Tecnico_de_Desarrollo_InvestWise.pdf`](../entregables/Informe_Tecnico_de_Desarrollo_InvestWise.pdf). El PDF se genera concatenando los capítulos en este orden; el contenido se edita **solo** aquí.

| Archivo | Capítulo |
|---|---|
| [`00-introduccion.md`](00-introduccion.md) | Introducción: problema, objetivo, integración de los componentes del curso y convenciones |
| [`01-funcionalidades.md`](01-funcionalidades.md) | 1. Descripción de funcionalidades (F01 a F15) |
| [`02-arquitectura.md`](02-arquitectura.md) | 2. Arquitectura de software inteligente y detalle de cada componente |
| [`03-poblacion.md`](03-poblacion.md) | 3. Tipo de población que puede usar el software |
| [`04-ventajas.md`](04-ventajas.md) | 4. Ventajas frente a otros softwares existentes |
| [`05-resultados.md`](05-resultados.md) | 5. Resultados y validación |
| [`06-anexos.md`](06-anexos.md) | Anexos A (parámetros), B (fuentes de datos) y C (decisiones de diseño) |
| [`build_figures.py`](build_figures.py) | Genera `img/fig-*.png` con el código real (horizonte, absorción y convergencia) |

## Convenciones de las fuentes

- `# ` abre un capítulo (nueva página) y `## ` una sección; ambos niveles entran en el índice.
- Una figura es una imagen con texto alternativo: `![{#fig:clave} Leyenda](ruta.png)`.
- Una tabla lleva antes un párrafo `Tabla: {#tab:clave} Leyenda`; `{split}` en la leyenda permite que la tabla continúe en la página siguiente.
- `@fig:clave` y `@tab:clave` se reemplazan por «Figura N» y «Tabla N» al generar el PDF.

## Regenerar

```bash
PYTHONPATH=. .venv/bin/python docs/informe/build_figures.py        # solo si cambian el código o los parámetros
/tmp/claude-1000/docs-venv/bin/python docs/entregables/build_manuals.py
```
