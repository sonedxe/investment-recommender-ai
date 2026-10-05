"""Pruebas del módulo de IA generativa en modo offline (parser + explicador)."""

from ai.generative import explicar_offline, interpretar_offline

TEXTO_EJEMPLO = (
    "Tengo 30 años, quiero invertir S/ 5000 de mis S/ 20000 de ahorro, "
    "no me gusta arriesgar mucho y no los necesitaré por unos 3 años, "
    "tengo un fondo de emergencia para 4 meses"
)


def test_interpreta_ejemplo_del_informe() -> None:
    """El ejemplo canónico de la sección 4.1 (etapa 1) se extrae completo."""
    r = interpretar_offline(TEXTO_EJEMPLO)
    assert r.completo
    assert r.monto_invertir == 5000.0
    assert r.ahorro_total == 20000.0
    assert r.horizonte_anios == 3.0
    assert r.lambda_base == 2.0  # "no me gusta arriesgar" -> conservador
    assert r.cobertura_emergencia_meses == 4.0
    assert r.pregunta_aclaracion is None


def test_no_confunde_edad_con_horizonte() -> None:
    r = interpretar_offline(TEXTO_EJEMPLO)
    assert r.horizonte_anios != 30.0


def test_loop_de_clarificacion_pide_lo_que_falta() -> None:
    """Requisito formal 4.2: nunca asume valores en silencio."""
    r = interpretar_offline("hola, quiero invertir")
    assert not r.completo
    assert r.pregunta_aclaracion is not None
    assert "dinero" in r.pregunta_aclaracion

    r2 = interpretar_offline("quiero invertir 10000 soles")
    assert not r2.completo
    assert "tiempo" in r2.pregunta_aclaracion


def test_loop_de_clarificacion_con_conversacion_acumulada() -> None:
    """El loop funciona re-analizando la conversación completa."""
    turno1 = "quiero invertir 10000 soles"
    turno2 = "unos 5 años"
    turno3 = "soy agresivo, prefiero no decir mis ahorros"
    r = interpretar_offline(f"{turno1}. {turno2}. {turno3}")
    assert r.completo
    assert r.absorcion_declinada
    assert r.horizonte_anios == 5.0
    assert r.lambda_base == 0.2


def test_negacion_arriesgar_es_conservador() -> None:
    r = interpretar_offline("no me gusta arriesgar nada, quiero invertir S/ 3000 a largo plazo, prefiero no decir mis ahorros")
    assert r.lambda_base == 2.0


def test_explicacion_cumple_reglas_de_lenguaje_simple() -> None:
    """Reglas de la sección 6: soles, escenario de riesgo, supuestos, cierre."""
    texto = explicar_offline(
        monto_invertir=5000,
        perfil_riesgo="conservador",
        pesos=[0.1, 0.1, 0.2, 0.3, 0.3],
        E_portafolio=0.05,
        C_contexto=0.0,
        sigma_portafolio=0.06,
        horizonte_anios=3,
        horizonte_etiqueta=None,
        m_H=1.0,
        ca_asumida=False,
        CA=0.5,
        s_pol=0.0,
        s_mac=0.0,
        contexto_activo=True,
    )
    assert "S/" in texto                       # regla 2: ejemplos en soles
    assert "año malo" in texto                 # regla 3: escenario de riesgo
    assert "panorama político" in texto        # regla 6: supuestos de contexto
    assert "educativa" in texto                # regla 7: cierre obligatorio
    assert "(" in texto                        # regla 4: categorías con aclaración


def test_explicacion_declara_supuesto_cuando_usuario_declina() -> None:
    """Sección 4.2: el valor asumido se declara visiblemente."""
    texto = explicar_offline(
        monto_invertir=5000,
        perfil_riesgo="moderado",
        pesos=[0.2, 0.2, 0.2, 0.2, 0.2],
        E_portafolio=0.06,
        C_contexto=0.0,
        sigma_portafolio=0.07,
        horizonte_anios=None,
        horizonte_etiqueta="largo",
        m_H=0.7,
        ca_asumida=True,
        CA=0.5,
        s_pol=-1.0,
        s_mac=0.0,
        contexto_activo=True,
    )
    assert "preferiste no indicar" in texto
    assert "adverso" in texto
