# Documentación

Entregables del trabajo parcial (curso de Software Inteligente):

- `manual_instalacion.md` — manual de instalación (backend, frontend, pruebas,
  solución de problemas).
- `manual_usuario.md` — manual de usuario (flujo de uso, panel de contexto,
  preguntas frecuentes).
- `Informe_Tecnico_InvestWise_v1.1.txt` — informe técnico de desarrollo
  (funcionalidades, arquitectura de los 5 módulos, modelo matemático,
  población objetivo, ventajas frente a software existente).
- `FUENTES_DE_DATOS.md` — trazabilidad de los datos reales de mercado
  (AAFMP/SMV, Banco Mundial/FMI-BCRP, SBS, CEIC, Trading Economics, MEF) que
  alimentan el módulo bayesiano, con valores, citas y método.
- `ENUNCIADO DEL TRABAJO PARCIAL.txt` — enunciado del curso (referencia).

## Trazabilidad informe ↔ código

| Informe técnico v1.1 | Implementación |
|---|---|
| M1 — IA generativa (4.2, 6) | `ai/generative/` (API vía `llm_client.py`; offline: `offline_parser.py` + `explainer.py`) |
| M2 — Bayesiano (4.3) | `ai/uncertainty/bayesian.py` + datos reales en `ai/data/market_data.py` (fuentes: `FUENTES_DE_DATOS.md`) |
| M3 — Algoritmo genético (4.4, 5) | `ai/heuristic/genetic.py` |
| M4 — Lógica difusa (4.5) | `ai/uncertainty/fuzzy.py` |
| M5 — Reglas de contexto (4.6) | `ai/uncertainty/context.py` |
| Anexos A y C | `ai/reference_data.py` |
| Flujo de 8 etapas (4.1) y contratos (4.7) | `backend/app/services/pipeline.py` |
| Interruptores de ablación (4.7) | `Interruptores` en la API y "Opciones avanzadas" en la interfaz |
