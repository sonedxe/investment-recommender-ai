# 06 · Decisiones pendientes

Estas decisiones bloquean partes de la implementación. Cada una trae una recomendación por defecto para no frenar el avance si el equipo no la discute a tiempo.

| ID | Decisión | Recomendación por defecto | Bloquea |
|---|---|---|---|
| D1 | Interpretación del feedback: qué conjunto difuso va en el cromosoma | Horizonte → fitness (Sugeno); absorción → gen `c` (Mamdani sin desfuzzificar). Ver [04](04-propuesta-difusa-cromosoma.md). Guion para validarlo con el docente en [10](10-decisiones-d1-d2-d5.md#d1--validar-con-el-docente-el-gen-difuso-del-cromosoma). | Módulo difuso, AG |
| D2 | Corrección de portafolios degenerados | **Decidida:** tope duro `wᵢ ≤ 0.40` (verificado frente a 0.5 y diversificación) y, desde W16, piso `wᵢ ≥ 0.05` para que ninguna categoría quede en 0 %. Ver [10](10-decisiones-d1-d2-d5.md#d2--corrección-de-los-portafolios-degenerados). | AG, fitness |
| D3 | Fuente de datos y matriz de correlaciones | ✅ **Decidida (revisada en W14–W15):** las cinco categorías con datos reales — BCRP (índice BVL, BTP 10 años, CD BCRP, depósito a plazo) y SBS (Fondo 2 de las AFP para fondos mixtos) —, descargadas una vez como CSV con manifiesto. Evidencia en `docs/evidencia/`. Ver [09](09-fuentes-de-datos.md). | Módulo bayesiano |
| D4 | Proveedor de IA generativa | ✅ **Decidida (2026-10-05): Anthropic** — Haiku 4.5 para interpretar y Sonnet 5.5 para explicar, con modo offline como respaldo automático. Golden set real: 98.0 % de exactitud por campo, 100 % JSON válido, 100 % de preguntas ante casos ambiguos, 3.1 s de latencia media (`experiments/results/golden_anthropic.md`). El 100 % del modo offline está sobreajustado: sus reglas se afinaron con estos mismos 20 casos. OpenAI sigue disponible cambiando `LLM_PROVIDER`. | IA generativa |
| D5 | Escala de λ_base | **Recomendado:** enum de 5 etiquetas; el LLM clasifica y el código mapea a λ. Ver [10](10-decisiones-d1-d2-d5.md#d5--escala-de-λ_base). | IA generativa, AG |
