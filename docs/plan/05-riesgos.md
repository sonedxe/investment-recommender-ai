# 05 · Riesgos y mitigaciones

| # | Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|---|
| R1 | El docente interpreta el feedback del cromosoma de otra forma | Media | Alto | Consultarlo en la semana 6 (T0.2); el AG recibe `μ_CA` como función, así que cambiar qué conjunto va en el cromosoma no rehace el motor. |
| R2 | No se consiguen series históricas | Media | Medio | Usar el Anexo A como prior y una matriz ρ fija documentada; declararlo como limitación. |
| R3 | La API del LLM falla, cuesta o está sin saldo el día de la demo | Media | Alto | Modo offline determinista; capturas de respaldo. |
| R4 | El LLM inventa cifras en la explicación | Media | Alto | Le pasamos solo cifras calculadas; validación posterior de cada número; si falla, se usa una plantilla determinista. |
| R5 | El LLM devuelve JSON inválido o supone datos | Media | Medio | Esquema estricto, enum para el perfil, reintento acotado y golden set. |
| R6 | Persisten los portafolios degenerados tras la corrección | Baja | Alto | Test de regresión (T3.5) y calibración en F8 antes de cerrar parámetros. |
| R7 | κ, φ o el tope mal calibrados hacen que un término domine el fitness | Media | Medio | Desglose del fitness visible; barrido de parámetros en T8.3. |
| R8 | Se integra tarde y aparecen incompatibilidades entre streams | Media | Alto | Contratos y tipos en F0 (T0.3); integración continua desde la semana 6. |
| R9 | Falta tiempo para la semana 7 | Media | Alto | Priorizar: núcleo + API + GUI mínima en S6; lo opcional (T3.6, T8.5, CommonKADS) se recorta primero. |
| R10 | Se percibe como asesoría financiera real | Baja | Medio | Aviso permanente en la GUI y en cada explicación; categorías representativas, no productos. |
