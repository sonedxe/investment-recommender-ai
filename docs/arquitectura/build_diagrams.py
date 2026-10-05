"""Generate the InvestWise architecture diagrams as SVG (palette and type of the design system).

Run: python docs/arquitectura/build_diagrams.py
Then export PNGs with headless Chromium (see docs/arquitectura/README.md).
"""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).parent

INK, MUTED, BG, CARD, SUNK = "#1c1a17", "#55514a", "#f6f4ee", "#fcfbf8", "#edeae2"
BORDER, STRONG, ACCENT, ACCENT_SOFT = "#dad5c9", "#837d6f", "#1f5c5a", "#e4eeeb"
CAUTION, CAUTION_INK = "#f4ecd6", "#6e4f0a"
GEN, HEU, UNC, CTX = "#4f6b8e", "#9a4a3a", "#1f5c5a", "#a87b24"
FONT = "'Source Sans 3', 'Segoe UI', system-ui, sans-serif"
SERIF = "'Source Serif 4', Georgia, serif"
MONO = "'Source Code Pro', 'DejaVu Sans Mono', monospace"


class Svg:
    def __init__(self, width: int, height: int, title: str, desc: str) -> None:
        self.w, self.h, self.parts = width, height, []
        self.head = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="t d">'
            f'<title id="t">{escape(title)}</title><desc id="d">{escape(desc)}</desc>'
            '<defs>'
            f'<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{STRONG}"/></marker>'
            f'<marker id="arrow-accent" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{ACCENT}"/></marker>'
            f'<marker id="arrow-caution" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{CAUTION_INK}"/></marker>'
            '</defs>'
            f'<rect width="{width}" height="{height}" fill="{BG}"/>'
        )

    def rect(self, x, y, w, h, fill=CARD, stroke=BORDER, sw=1, dash=None, rx=4):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def bar(self, x, y, w, color, h=4):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="1" fill="{color}"/>')

    def text(self, x, y, s, size=14, weight=400, color=INK, anchor="start", family=FONT, italic=False):
        st = ' font-style="italic"' if italic else ""
        self.parts.append(
            f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'fill="{color}" text-anchor="{anchor}"{st}>{escape(s)}</text>')

    def lines(self, x, y, items, size=13, gap=18, color=INK, weight=400, family=FONT):
        for i, s in enumerate(items):
            self.text(x, y + i * gap, s, size=size, color=color, weight=weight, family=family)

    def arrow(self, points, color=STRONG, marker="arrow", sw=1.6, dash=None, both=False):
        d = " ".join(("M" if i == 0 else "L") + f"{x},{y}" for i, (x, y) in enumerate(points))
        da = f' stroke-dasharray="{dash}"' if dash else ""
        start = f' marker-start="url(#{marker})"' if both else ""
        self.parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}"{da}{start} marker-end="url(#{marker})"/>')

    def label(self, x, y, s, color=MUTED, size=12, fill=BG):
        w = len(s) * size * 0.52 + 12
        self.parts.append(f'<rect x="{x - w / 2}" y="{y - size}" width="{w}" height="{size + 8}" rx="3" fill="{fill}"/>')
        self.text(x, y + 1, s, size=size, color=color, anchor="middle")

    def save(self, name: str) -> None:
        (OUT / name).write_text(self.head + "".join(self.parts) + "</svg>\n", encoding="utf-8")


def card(s: Svg, x, y, w, h, color, title, subtitle, items, item_size=12.5, gap=17):
    s.rect(x, y, w, h)
    s.bar(x, y, w, color, h=5)
    s.text(x + 14, y + 28, title, size=15.5, weight=600)
    s.text(x + 14, y + 46, subtitle, size=11.5, color=MUTED, family=MONO)
    s.lines(x + 14, y + 70, items, size=item_size, gap=gap)


# ---------------------------------------------------------------- 1. components
def components() -> None:
    s = Svg(1400, 1110, "Arquitectura de componentes de InvestWise",
            "Frontend React, backend FastAPI, núcleo de IA con los tres módulos del curso, reglas de contexto, "
            "datos versionados y servicios externos.")
    s.text(60, 56, "InvestWise · Arquitectura de componentes", size=28, weight=500, family=SERIF)
    s.text(60, 82, "Software Inteligente — IA generativa + algoritmo heurístico + razonamiento bajo incertidumbre", size=14, color=MUTED)

    # user
    s.rect(560, 108, 280, 46, fill=SUNK, stroke=STRONG)
    s.text(700, 137, "Usuario · navegador web", size=15, weight=600, anchor="middle")
    s.arrow([(700, 154), (700, 186)])

    # frontend
    s.rect(60, 188, 1280, 150, fill=CARD, stroke=STRONG)
    s.text(80, 216, "Interfaz gráfica", size=17, weight=600)
    s.text(232, 216, "frontend/ · React + Vite + TypeScript (design system propio)", size=12, color=MUTED, family=MONO)
    boxes = [
        ("Pantallas", ["Inicio (texto libre)", "Aclaración (una pregunta)", "Resultado + explicación", "Contexto · Detalle técnico"]),
        ("Componentes", ["32 componentes", "atoms · molecules", "organisms · screens", "Gráficos SVG accesibles"]),
        ("Contenedores", ["Máquina de estados del flujo", "inicio → aclaración → cálculo", "→ resultado ⇄ contexto", "Tema claro / oscuro"]),
        ("Cliente API", ["Peticiones HTTP tipadas", "Mappers: contrato →", "props del diseño", "Fixtures del backend real"]),
    ]
    for i, (t, items) in enumerate(boxes):
        x = 80 + i * 312
        s.rect(x, 230, 296, 96, fill=SUNK, stroke=BORDER)
        s.text(x + 12, 252, t, size=13.5, weight=600)
        s.lines(x + 12, 270, items, size=12, gap=15, color=MUTED)

    s.arrow([(700, 338), (700, 384)], both=True)
    s.label(700, 366, "HTTP / JSON  ·  /api/*")

    # backend
    s.rect(60, 386, 1280, 114, fill=CARD, stroke=STRONG)
    s.text(80, 414, "API y orquestación", size=17, weight=600)
    s.text(258, 414, "backend/app/ · FastAPI + Pydantic", size=12, color=MUTED, family=MONO)
    s.rect(80, 428, 600, 60, fill=SUNK)
    s.text(92, 449, "Endpoints", size=13.5, weight=600)
    s.text(92, 467, "POST /api/interpret · POST /api/recommend", size=11, color=MUTED, family=MONO)
    s.text(92, 481, "GET /api/context/defaults · GET /api/market/estimates", size=11, color=MUTED, family=MONO)
    s.rect(696, 428, 624, 60, fill=ACCENT_SOFT, stroke=ACCENT)
    s.text(708, 449, "Servicio de recomendación (orquestador)", size=13.5, weight=600, color=ACCENT)
    s.text(708, 469, "Coordina las 8 etapas · interruptores de ablación · reparto exacto al céntimo · semilla reproducible",
           size=11.5, color=INK)

    s.arrow([(700, 500), (700, 540)])
    s.label(700, 524, "llamadas en proceso (sin red)")

    # core
    s.rect(60, 542, 1280, 318, fill=BG, stroke=STRONG, dash="6 5")
    s.text(80, 570, "Núcleo de IA", size=17, weight=600)
    s.text(206, 570, "ai/ · Python + NumPy, programado por el equipo (sin librerías de IA externas)", size=12, color=MUTED, family=MONO)
    card(s, 80, 588, 300, 256, GEN, "1 · IA generativa", "ai/generative/", [
        "Intérprete: texto → perfil", "  (monto, horizonte, riesgo,", "  ahorros, colchón) + evidencia",
        "Preguntas de aclaración", "  (el código decide qué falta)", "Explicador en lenguaje simple",
        "  + validación de cifras", "Puerto LanguageModel:", "  Anthropic · OpenAI · offline"], gap=16.5)
    card(s, 396, 588, 316, 256, UNC, "2 · Razonamiento bajo incertidumbre", "ai/uncertainty/", [
        "Lógica difusa (fuzzy/)", "  Horizonte · Sugeno → λ efectiva", "    = conjunto en el FITNESS",
        "  Absorción · Mamdani → μ_CA", "    = conjunto en el CROMOSOMA", "Bayesiano (bayesian/)",
        "  actualización conjugada normal", "  μ, σ, correlaciones, tendencia", "  prior Anexo A + datos reales"], gap=16.5)
    card(s, 728, 588, 300, 256, HEU, "3 · Algoritmo heurístico", "ai/heuristic/", [
        "Algoritmo genético", "Cromosoma [w1..w5 | c]", "  5 pesos + gen difuso c",
        "Fitness = retorno + contexto", "  − λ·σ − penalización(σ_max(c))", "  + κ·μ_CA(c)",
        "Torneo · cruce aritmético", "  mutación · elitismo", "Tope 40 % por categoría"], gap=16.5)
    card(s, 1044, 588, 276, 256, CTX, "Reglas de contexto", "ai/context/", [
        "Base de reglas RC1–RC7", "Panorama político", "Estabilidad macroeconómica",
        "Precedente por categoría", "Tendencia reciente", "Ajusta μ y σ (μ', Σ')",
        "Tope de influencia c_max", "Traza de reglas activadas"], gap=16.5)

    # external (left, under generative AI) + data (right)
    s.rect(60, 908, 600, 172, fill=CAUTION, stroke=CAUTION_INK, dash="5 4")
    s.text(80, 936, "Servicios externos", size=16, weight=600, color=CAUTION_INK)
    s.text(80, 964, "Anthropic API (Claude)", size=13.5, weight=600)
    s.text(80, 982, "Haiku 4.5 interpreta · Sonnet 5.5 explica · si falla → modo offline", size=12, color=MUTED)
    s.text(80, 1014, "BCRP (BCRPData) · SBS (Boletín SPP)", size=13.5, weight=600)
    s.text(80, 1032, "Series oficiales de mercado y valor cuota del Fondo 2 de las AFP", size=12, color=MUTED)
    s.text(80, 1060, "La aplicación nunca consulta datos de mercado en línea", size=12, color=MUTED, italic=True)

    s.rect(740, 908, 600, 172, fill=CARD, stroke=STRONG)
    s.text(760, 936, "Datos versionados en el repositorio", size=16, weight=600)
    s.rect(760, 950, 276, 112, fill=SUNK)
    s.text(772, 972, "data/parameters/", size=13, weight=600, family=MONO)
    s.lines(772, 992, ["Anexo A (μ, σ de referencia)", "Anexo C (contexto) · conjuntos", "difusos · AG · escala de λ"], size=12, gap=16, color=MUTED)
    s.rect(1050, 950, 276, 112, fill=SUNK)
    s.text(1062, 972, "data/market/", size=13, weight=600, family=MONO)
    s.lines(1062, 992, ["5 series mensuales 2010–2026", "manifest.json + SOURCES.md", "valores tal como se publicaron"], size=12, gap=16, color=MUTED)

    s.arrow([(230, 844), (230, 906)], color=CAUTION_INK, marker="arrow-caution", dash="5 4", both=True)
    s.label(230, 880, "HTTPS (solo IA generativa)", color=CAUTION_INK, size=11.5)
    s.arrow([(1040, 844), (1040, 906)], both=True)
    s.label(1040, 880, "lectura de parámetros y series", size=11.5)
    s.arrow([(660, 1030), (738, 1030)], color=CAUTION_INK, marker="arrow-caution", dash="5 4")
    s.label(700, 1012, "fetch (1 vez)", color=CAUTION_INK, size=11)
    s.save("01-componentes.svg")


# ---------------------------------------------------------------- 2. flow
def flow() -> None:
    s = Svg(1400, 1180, "Flujo de una recomendación en InvestWise",
            "Ocho etapas desde el texto del usuario hasta la explicación, con el conjunto difuso del horizonte en "
            "el fitness y el de la capacidad de absorción dentro del cromosoma.")
    s.text(60, 56, "InvestWise · Flujo de una recomendación", size=28, weight=500, family=SERIF)
    s.text(60, 82, "De un texto libre a un portafolio explicado, en 8 etapas", size=14, color=MUTED)

    def step(n, x, y, w, h, color, title, items, module):
        s.rect(x, y, w, h)
        s.bar(x, y, 6, color, h=h)
        s.parts.append(f'<circle cx="{x + 34}" cy="{y + 30}" r="15" fill="{color}"/>')
        s.text(x + 34, y + 35, str(n), size=14, weight=700, color="#fcfbf8", anchor="middle")
        s.text(x + 60, y + 36, title, size=15.5, weight=600)
        s.text(x + w - 14, y + 36, module, size=11, color=MUTED, anchor="end", family=MONO)
        s.lines(x + 24, y + 64, items, size=12.5, gap=17, color=INK)

    L, R, W = 60, 720, 620
    step(1, L, 110, W, 108, STRONG, "El usuario describe su situación", [
        "Texto libre, sin formularios: «Tengo S/ 5,000 de mis S/ 20,000,",
        "no me gusta arriesgar y no los necesito en unos 3 años»"], "frontend")
    step(2, R, 110, W, 108, GEN, "IA generativa interpreta", [
        "Extrae monto, horizonte, perfil de riesgo, ahorros y colchón con evidencia.",
        "Si falta algo crítico → UNA pregunta de aclaración (nunca supone)."], "ai/generative")
    s.arrow([(L + W, 164), (R, 164)])
    s.arrow([(R + 300, 218), (R + 300, 238), (L + 300, 238), (L + 300, 218)], color=GEN, dash="5 4")
    s.label(L + 640, 242, "bucle de aclaración: pregunta → respuesta", color=GEN, size=11.5)

    step(3, L, 270, W, 116, UNC, "Estimación bayesiana del mercado", [
        "5 series reales (BCRP, SBS) → retornos mensuales.",
        "μ: prior del Anexo A + datos (actualización conjugada).",
        "σ, correlaciones y tendencia de cada categoría."], "ai/uncertainty/bayesian")
    s.text(L + 316, 408, "precalculado desde data/market/ (no depende del usuario)", size=11.5, color=MUTED, italic=True)
    step(4, R, 270, W, 116, UNC, "Lógica difusa sobre el perfil", [
        "Horizonte (Sugeno): «unos 3 años» → m_H → λ efectiva",
        "Absorción (Mamdani, sin desfuzzificar): ahorro comprometido",
        "y meses de colchón → conjunto difuso μ_CA"], "ai/uncertainty/fuzzy")
    s.arrow([(R + 300, 218), (R + 300, 268)])

    step(5, L, 438, W, 116, CTX, "Reglas de contexto", [
        "Panorama político, estabilidad macro, precedente, tendencia.",
        "RC1–RC7 ajustan el retorno (μ') y el riesgo (Σ') por categoría,",
        "con un tope de influencia: el contexto nunca domina a los datos."], "ai/context")
    s.arrow([(L + 300, 386), (L + 300, 436)])

    # GA big box
    gy = 606
    s.rect(L, gy, 1280, 250, fill=CARD, stroke=HEU, sw=1.6)
    s.bar(L, gy, 6, HEU, h=250)
    s.parts.append(f'<circle cx="{L + 34}" cy="{gy + 30}" r="15" fill="{HEU}"/>')
    s.text(L + 34, gy + 35, "6", size=14, weight=700, color="#fcfbf8", anchor="middle")
    s.text(L + 60, gy + 36, "Algoritmo genético: busca el mejor portafolio para ESE usuario en ESE contexto", size=15.5, weight=600)
    s.text(L + 1266, gy + 36, "ai/heuristic", size=11, color=MUTED, anchor="end", family=MONO)
    # chromosome
    s.text(L + 24, gy + 72, "Cromosoma (cada individuo de la población):", size=13, color=MUTED)
    genes = ["w1 acciones", "w2 mixtos", "w3 deuda", "w4 bonos", "w5 depósito"]
    for i, g in enumerate(genes):
        s.rect(L + 24 + i * 112, gy + 84, 106, 40, fill=SUNK, stroke=STRONG)
        s.text(L + 77 + i * 112, gy + 109, g, size=12.5, anchor="middle")
    s.rect(L + 24 + 5 * 112 + 14, gy + 84, 150, 40, fill=ACCENT_SOFT, stroke=ACCENT, sw=1.8)
    s.text(L + 24 + 5 * 112 + 89, gy + 104, "c  · gen difuso", size=12.5, weight=600, color=ACCENT, anchor="middle")
    s.text(L + 24 + 5 * 112 + 89, gy + 119, "nivel de absorción", size=11, color=ACCENT, anchor="middle")
    s.text(L + 24, gy + 146, "Σw = 1 · w ≥ 0 · w ≤ 40 %  ·  c ∈ [0, 1]", size=12, color=MUTED, family=MONO)
    # fitness
    s.text(L + 780, gy + 72, "Función de aptitud (fitness):", size=13, color=MUTED)
    s.rect(L + 780, gy + 84, 476, 62, fill=SUNK, stroke=BORDER)
    s.text(L + 794, gy + 108, "Σ wᵢ·μ'ᵢ  −  λ_ef·σ'(P)", size=14, family=MONO)
    s.text(L + 794, gy + 132, "−  φ·max(0, σ' − σ_max(c))²  +  κ·μ_CA(c)", size=14, family=MONO)
    s.lines(L + 24, gy + 180, [
        "Población de 80 portafolios · selección por torneo · cruce aritmético · mutación gaussiana · elitismo",
        "Se detiene al converger (sin mejora en 25 generaciones) · misma semilla → mismo resultado",
        "Resultado: los 5 pesos, el gen c, el desglose del puntaje y la curva de convergencia"], size=12.5, gap=18)
    # fuzzy arrows into GA
    s.arrow([(R + 480, 386), (R + 480, gy + 82)], color=ACCENT, marker="arrow-accent", sw=2)
    s.label(R + 480, 500, "λ efectiva → FITNESS", color=ACCENT, size=12)
    s.arrow([(R + 140, 386), (R + 140, 470), (L + 24 + 5 * 112 + 89, 470), (L + 24 + 5 * 112 + 89, gy + 82)], color=ACCENT, marker="arrow-accent", sw=2)
    s.label(L + 24 + 5 * 112 + 185, 540, "μ_CA → CROMOSOMA (gen c)", color=ACCENT, size=12)
    s.arrow([(L + 300, 554), (L + 300, gy - 2)])
    s.label(L + 300, 584, "μ', Σ' ajustados", size=12)

    step(7, L, 900, W, 116, GEN, "IA generativa explica", [
        "Recibe SOLO cifras calculadas: reparto en soles, escenarios,",
        "efecto del horizonte y de la absorción, supuestos.",
        "Se valida cada número; si falla → plantilla determinista."], "ai/generative")
    step(8, R, 900, W, 116, STRONG, "Interfaz gráfica", [
        "Portafolio con montos en S/, explicación y supuestos.",
        "Panel de contexto (Adverso / Neutral / Favorable) y",
        "detalle técnico: pertenencias, μ_CA con c y centroide, reglas."], "frontend")
    s.arrow([(L + 300, gy + 250), (L + 300, 898)])
    s.arrow([(L + W, 958), (R, 958)])

    # legend
    ly = 1060
    s.text(L, ly, "Módulos del curso:", size=13, weight=600)
    for i, (c, t) in enumerate([(GEN, "IA generativa"), (UNC, "Razonamiento bajo incertidumbre"), (HEU, "Algoritmo heurístico"),
                                (CTX, "Reglas de contexto")]):
        x = L + 150 + i * 220
        s.rect(x, ly - 12, 14, 14, fill=c, stroke=c, rx=2)
        s.text(x + 22, ly, t, size=12.5)
    s.arrow([(L + 1030, ly - 5), (L + 1072, ly - 5)], color=ACCENT, marker="arrow-accent", sw=2)
    s.text(L + 1082, ly, "conjunto difuso → AG", size=12.5)
    s.text(L, ly + 34, "El conjunto del horizonte actúa en la EVALUACIÓN (fitness) y el de la capacidad de absorción vive en la "
           "CADENA GENÉTICA (gen c): lo que pidió el docente.", size=12.5, color=MUTED, italic=True)
    s.save("02-flujo.svg")


if __name__ == "__main__":
    components()
    flow()
    print("written", sorted(p.name for p in OUT.glob("*.svg")))
