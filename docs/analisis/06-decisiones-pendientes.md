# 06 · Decisiones pendientes

Estas decisiones bloquean partes de la implementación. Cada una trae una recomendación por defecto para no frenar el avance si el equipo no la discute a tiempo.

| ID | Decisión | Recomendación por defecto | Bloquea |
|---|---|---|---|
| D1 | Interpretación del feedback: qué conjunto difuso va en el cromosoma | Horizonte → fitness (Sugeno); absorción → gen `c` (Mamdani sin desfuzzificar). Ver [04](04-propuesta-difusa-cromosoma.md). Guion para validarlo con el docente en [10](10-decisiones-d1-d2-d5.md#d1--validar-con-el-docente-el-gen-difuso-del-cromosoma). | Módulo difuso, AG |
| D2 | Corrección de portafolios degenerados | **Recomendado:** tope duro `wᵢ ≤ 0.40` (verificado frente a 0.5 y diversificación). Ver [10](10-decisiones-d1-d2-d5.md#d2--corrección-de-los-portafolios-degenerados). | AG, fitness |
| D3 | Fuente de datos y matriz de correlaciones | ✅ **Decidida:** fuentes combinadas (Yahoo para acciones, BCRP para BTP y depósito, SMV/AAFMP o Anexo A para mixtos y deuda), descargadas una vez como CSV. Ver [09](09-fuentes-de-datos.md). | Módulo bayesiano |
| D4 | Proveedor de IA generativa | Mantener interfaz compatible con OpenAI (ya existe en `.env.example`) detrás de un puerto. Candidatos: OpenAI, Anthropic, Groq/Gemini (planes gratuitos), Ollama (local). Criterios: JSON confiable, español, costo, latencia. **Bloqueado por:** saber si el equipo tiene créditos o una clave. | IA generativa |
| D5 | Escala de λ_base | **Recomendado:** enum de 5 etiquetas; el LLM clasifica y el código mapea a λ. Ver [10](10-decisiones-d1-d2-d5.md#d5--escala-de-λ_base). | IA generativa, AG |
