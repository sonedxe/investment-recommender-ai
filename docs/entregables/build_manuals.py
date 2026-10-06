"""Build the deliverable PDFs: installation and user manuals and the technical development report.

Each document is built from an ordered list of Markdown sources concatenated into one body
(the manuals have one source; the report concatenates docs/informe/00..06-*.md).

Pipeline: Markdown -> HTML (python-markdown) with a print stylesheet, a cover page and a
table of contents -> PDF with headless Chromium. The PDF is rendered twice: the first pass
finds the page of every heading (pypdf), the second writes those page numbers in the index.
Page numbers in the footer come from CSS @page margin boxes.

Requirements (kept out of the project requirements on purpose):
    python3 -m venv /tmp/claude-1000/docs-venv
    /tmp/claude-1000/docs-venv/bin/pip install markdown pypdf
    chromium (or google-chrome) on PATH

Usage (from the repository root):
    /tmp/claude-1000/docs-venv/bin/python docs/entregables/build_manuals.py [--keep-html]

Fonts (Source Serif 4, Source Sans 3, Source Code Pro) are downloaded once from Google
Fonts into a local cache; without network the stylesheet falls back to system fonts.
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
import struct
import subprocess
import tempfile
import urllib.request
from pathlib import Path

import markdown
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "docs" / "manuales"
OUT = ROOT / "docs" / "entregables"
FONT_CACHE = Path(tempfile.gettempdir()) / "investwise-manual-fonts"
FONTS_URL = (
    "https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400"
    "&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&family=Source+Code+Pro:wght@400;600&display=block"
)
CHROME_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"

COVER = {
    "faculty": "Facultad de Ingeniería de Sistemas e Informática",
    "school": "Escuela Profesional de Ingeniería de Software",
    "crest": OUT / "assets" / "escudo-unmsm.png",
    "course": "Software Inteligente",
    "proposal": "Recomendador de Inversión / Portafolio Personal",
    "group": "Grupo 4:",
    # As written on the team's official cover.
    "members": [
        "León Robles, Illary Marcelo",
        "Chavez Gave, Jose Luis",
        "Limachi Sarmiento José Luis",
        "Gutierrez Campos Edson Luis",
        "Arias Chumpitaz, Giovanni",
    ],
    "teacher": "Calderón Vilca, David",
    "place": "Lima, Perú",
    "year": "2026",
}

INFORME = ROOT / "docs" / "informe"

MANUALS = [
    {
        "sources": [SRC / "instalacion.md"],
        "output": OUT / "Manual_de_Instalacion_InvestWise.pdf",
        "title": "Manual de Instalación",
        "footer": "Manual de Instalación — ",
        "lead": "Instalación, configuración, ejecución y verificación del sistema en Linux, macOS y Windows.",
    },
    {
        "sources": [SRC / "usuario.md"],
        "output": OUT / "Manual_de_Usuario_InvestWise.pdf",
        "title": "Manual de Usuario",
        "footer": "Manual de Usuario — ",
        "lead": "Guía para obtener y entender una distribución de ejemplo, sin conocimientos financieros previos.",
    },
    {
        # Chapters: '# ' headings start a page and are indexed with their '## ' sections.
        "sources": [INFORME / name for name in (
            "00-introduccion.md", "01-funcionalidades.md", "02-arquitectura.md", "03-poblacion.md",
            "04-ventajas.md", "05-resultados.md", "06-anexos.md",
        )],
        "output": OUT / "Informe_Tecnico_de_Desarrollo_InvestWise.pdf",
        "title": "Informe Técnico de Desarrollo",
        "footer": "Informe Técnico de Desarrollo — ",
        "lead": "",
        "chapters": True,
    },
]

CSS = """
@page { size: A4; margin: 25mm 22mm 22mm 25mm;
  @bottom-center { content: "__FOOTER__" counter(page); font-family: "Times New Roman", "Liberation Serif", serif;
                   font-size: 9pt; color: #000; } }
@page cover { margin: 0; @bottom-center { content: none; } }
:root { --ink: #000; --muted: #333; --border: #9a9a9a; --surface: #f4f4f4; --surface-2: #e9e9e9; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; color: var(--ink); background: #fff;
       font-family: "Times New Roman", "Liberation Serif", "Noto Serif", serif;
       font-size: 11.5pt; line-height: 1.5; text-align: justify; hyphens: manual; }
h1, h2, h3, h4 { font-family: inherit; font-weight: 700; color: var(--ink); text-align: left;
                 break-after: avoid; page-break-after: avoid; break-inside: avoid; }
h2 { font-size: 15pt; line-height: 1.25; margin: 20pt 0 8pt; }
h3 { font-size: 12.5pt; line-height: 1.3; margin: 14pt 0 5pt; }
p { margin: 0 0 7pt; orphans: 3; widows: 3; }
ul, ol { margin: 0 0 8pt; padding-left: 20pt; }
li { margin-bottom: 3pt; }
a { color: var(--ink); text-decoration: none; }
strong { font-weight: 700; }
em { font-style: italic; }
code { font-family: "Courier New", "Liberation Mono", monospace; font-size: 9.5pt;
       background: var(--surface); padding: 0 2pt; overflow-wrap: anywhere; }
pre { background: var(--surface); border: 0.6pt solid var(--border); padding: 7pt 9pt; margin: 4pt 0 10pt;
      white-space: pre-wrap; overflow-wrap: anywhere; break-inside: avoid; text-align: left; }
pre code { background: none; padding: 0; font-size: 9pt; line-height: 1.4; }
table { width: 100%; border-collapse: collapse; margin: 4pt 0 11pt; font-size: 10pt; line-height: 1.35;
        text-align: left; }
thead { display: table-header-group; }
th { font-weight: 700; background: var(--surface-2); color: var(--ink); }
th, td { border: 0.6pt solid var(--border); padding: 4pt 6pt; vertical-align: top; }
tr { break-inside: avoid; }
table.short { break-inside: avoid; }
td code, th code { font-size: 9pt; }
figure { margin: 8pt 0 14pt; break-inside: avoid; text-align: center; }
figure img { max-width: 100%; max-height: 215mm; border: 0.6pt solid var(--border); }
figure.narrow img { max-width: 58%; }
figcaption { font-size: 10pt; color: var(--ink); margin-top: 5pt; text-align: center; }
figcaption b { font-weight: 700; }
.keep { break-inside: avoid; }
p:has(+ pre, + ul, + ol, + table, + .keep) { break-after: avoid; }

/* Cover (academic format of the team) */
.cover { page: cover; height: 297mm; box-sizing: border-box; padding: 24mm 25mm 20mm; text-align: center;
         break-after: page; color: #000; }
.cover p { margin: 0; text-align: center; }
.cover .fac { font-size: 13pt; font-weight: 700; line-height: 1.3; }
.cover .crest { display: block; width: 46mm; margin: 12mm auto 16mm; }
.cover .title { font-size: 17pt; font-weight: 700; margin-bottom: 8pt; }
.cover .subtitle { font-size: 14pt; font-weight: 700; margin-bottom: 26mm; }
.cover .label { font-size: 12.5pt; font-weight: 700; margin-bottom: 4pt; }
.cover .names { font-size: 12pt; line-height: 1.55; margin-bottom: 18mm; }
.cover .teacher { font-size: 12pt; margin: 2pt 0 12mm; }
.cover .course { font-size: 12.5pt; font-weight: 700; margin-bottom: 14mm; }
.cover .place { font-size: 12.5pt; font-weight: 700; line-height: 1.5; }

/* Index */
.toc { break-after: page; }
.toc h2 { margin-top: 0; text-align: center; }
.toc ol { list-style: none; padding: 0; margin: 0; }
.toc li { display: flex; align-items: baseline; margin: 0 0 4pt; font-size: 11.5pt; text-align: left; }
.toc li.l3 { padding-left: 9mm; font-size: 11pt; margin-bottom: 2.5pt; }
.toc li.l2 { font-weight: 700; margin-top: 6pt; }
.toc .dots { flex: 1; border-bottom: 0.8pt dotted #000; margin: 0 4pt 3pt; }
.toc .pg { min-width: 7mm; text-align: right; font-variant-numeric: tabular-nums; }
.toc li.c1 { font-weight: 700; margin-top: 7pt; }
.toc li.c2 { padding-left: 7mm; font-size: 11pt; margin-bottom: 2.5pt; }
.toc li.lf { font-size: 10.5pt; margin-bottom: 2.5pt; }
.toc li.lf a, .toc li.c2 a { max-width: 88%; }

/* Report chapters, captions and formulas */
h1 { font-size: 18pt; line-height: 1.25; margin: 0 0 12pt; }
h1.chapter { break-before: page; }
caption { caption-side: top; text-align: left; font-size: 10pt; padding: 0 0 4pt; color: var(--ink); }
caption b { font-weight: 700; }
figure.chart img { max-width: 88%; border: none; }
body.report p:has(+ ul, + ol, + table) { break-after: auto; }
body.report td.num { white-space: nowrap; }
body.report td code { overflow-wrap: normal; word-break: normal; }
body.report table.wide { font-size: 9pt; }
body.report table.wide th, body.report table.wide td { padding: 3pt 4pt; }
.toc li { align-items: last baseline; }
.toc li.lf { font-size: 10pt; margin-bottom: 1.5pt; line-height: 1.35; }
"""


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as fh:
        head = fh.read(24)
    return struct.unpack(">II", head[16:24])


def font_css() -> str:
    """@font-face rules pointing to locally cached font files ('' if they cannot be fetched)."""
    css_file = FONT_CACHE / "fonts.css"
    if not css_file.exists():
        try:
            FONT_CACHE.mkdir(parents=True, exist_ok=True)
            req = urllib.request.Request(FONTS_URL, headers={"User-Agent": CHROME_UA})
            css = urllib.request.urlopen(req, timeout=20).read().decode()
            css = re.sub(r"/\*.*?\*/\s*", "", css, flags=re.S)
            for i, url in enumerate(sorted(set(re.findall(r"url\((https://[^)]+)\)", css)))):
                local = FONT_CACHE / f"f{i}{Path(url).suffix or '.woff2'}"
                if not local.exists():
                    local.write_bytes(urllib.request.urlopen(url, timeout=20).read())
                css = css.replace(url, local.as_uri())
            css_file.write_text(css)
        except OSError as exc:  # offline: system fonts
            print(f"warning: fonts not downloaded ({exc}); using system fonts")
            return ""
    return css_file.read_text()


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


LABEL = re.compile(r"\{#((?:fig|tab):[\w-]+)\}\s*")


def convert(md_text: str, base: Path, chapters: bool = False) -> tuple[str, str, list, list, list]:
    """Return (title, body html, headings [(level, id, text)], figures [(n, caption)], tables [(n, caption)]).

    Manuals: the first '# ' heading is the document title and '##'/'###' are indexed.
    Chapters mode (report): every '# ' is a chapter that starts a page; '#' and '##' are indexed.
    Figures are numbered from the image alt text and tables from a preceding 'Tabla: caption'
    paragraph; '{#fig:key}' / '{#tab:key}' label them, '@fig:key' / '@tab:key' cite them and
    '{split}' in a table caption lets that table continue on the next page.
    """
    title = ""
    if not chapters:
        title_match = re.match(r"#\s+(.+)\n", md_text)
        title = title_match.group(1).strip() if title_match else ""
        md_text = md_text[title_match.end():] if title_match else md_text
    body = markdown.markdown(md_text, extensions=["tables", "fenced_code", "sane_lists"], output_format="html5")

    headings: list[tuple[int, str, str]] = []
    indexed = "12" if chapters else "23"

    def heading(m: re.Match) -> str:
        level, inner = int(m.group(1)), m.group(2)
        text = html.unescape(re.sub(r"<[^>]+>", "", inner)).strip()
        hid = f"h-{len(headings)}-{slug(text)[:40]}"
        headings.append((level, hid, text))
        cls = ' class="chapter"' if chapters and level == 1 else ""
        return f'<h{level} id="{hid}"{cls}>{inner}</h{level}>'

    body = re.sub(rf"<h([{indexed}])>(.*?)</h\1>", heading, body, flags=re.S)

    labels: dict[str, str] = {}
    figures: list[tuple[int, str]] = []

    def figure(m: re.Match) -> str:
        attrs = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
        src = (base / html.unescape(attrs["src"])).resolve()
        if not src.exists():
            raise FileNotFoundError(f"image not found: {src}")
        w, h = png_size(src)
        alt = attrs.get("alt", "")
        label = LABEL.match(alt)
        caption = LABEL.sub("", alt, count=1) if label else alt
        n = len(figures) + 1
        if label:
            labels[label.group(1)] = f"Figura {n}"
        figures.append((n, html.unescape(caption)))
        cls = "chart" if chapters and "fig" in src.name else ("narrow" if w < 800 else "")
        return (f'<figure class="{cls}" id="fig-{n}"><img src="{src.as_uri()}" alt="{caption}">'
                f'<figcaption><b>Figura {n}.</b> {caption}</figcaption></figure>')

    short_rows = 16 if chapters else 14
    # Short tables stay on one page (the header row alone at a page bottom reads badly).
    body = re.sub(r"<table>(.*?)</table>",
                  lambda m: f'<table class="{"short" if m.group(1).count("<tr") <= short_rows else ""}">{m.group(1)}</table>',
                  body, flags=re.S)
    body = re.sub(r"<p>\s*<img ([^>]+?)\s*/?>\s*</p>", figure, body)

    tables: list[tuple[int, str]] = []

    def table(m: re.Match) -> str:
        caption, cls = m.group(1).strip(), m.group(2)
        if "{split}" in caption:  # a table allowed to continue on the next page
            caption, cls = caption.replace("{split}", "").strip(), cls.replace("short", "").strip()
        label = LABEL.match(caption)
        if label:
            caption = LABEL.sub("", caption, count=1)
        n = len(tables) + 1
        if label:
            labels[label.group(1)] = f"Tabla {n}"
        tables.append((n, html.unescape(re.sub(r"<[^>]+>", "", caption))))
        return (f'<table class="{cls}" id="tab-{n}"><caption><b>Tabla {n}.</b> {caption}</caption>')

    body = re.sub(r'<p>Tabla:\s*(.*?)</p>\s*<table class="([^"]*)">', table, body, flags=re.S)
    if chapters:
        # Numbers stay on one line; code in cells may break only after '/' or '_'; wide tables get a smaller font.
        body = re.sub(r"<td>([\s\d,.%+−\-–()\[\];/pxS]+)</td>",
                      lambda m: f'<td class="num">{m.group(1)}</td>' if re.search(r"\d", m.group(1)) else m.group(0), body)
        body = re.sub(r"<td>(.*?)</td>", lambda m: "<td>" + re.sub(
            r"<code>(.*?)</code>", lambda c: "<code>" + re.sub(r"([/_])", r"\1<wbr>", c.group(1)) + "</code>",
            m.group(1)) + "</td>", body, flags=re.S)
        body = re.sub(r'<table class="([^"]*)"( id="tab-\d+">.*?</thead>)',
                      lambda m: f'<table class="{m.group(1)}{" wide" if m.group(2).count("<th>") >= 8 else ""}"{m.group(2)}',
                      body, flags=re.S)
    if re.search(r"<p>Tabla:", body):
        raise ValueError("a 'Tabla:' caption is not followed by a table")

    def cite(m: re.Match) -> str:
        if m.group(1) not in labels:
            raise KeyError(f"unknown reference @{m.group(1)}")
        return labels[m.group(1)]

    body = re.sub(r"@((?:fig|tab):[\w-]+)", cite, body)

    # Keep a short lead-in paragraph together with the code block or table it introduces.
    body = re.sub(r"(<p>(?:(?!</p>).){0,300}:</p>\s*)(<pre>.*?</pre>)",
                  r'<div class="keep">\1\2</div>', body, flags=re.S)
    return title, body, headings, figures, tables


def cover_html(manual: dict) -> str:
    c = COVER
    names = "<br>".join(html.escape(m) for m in c["members"])
    return f"""
<section class="cover">
  <p class="fac">{c['faculty']}<br>{c['school']}</p>
  <img class="crest" src="{c['crest'].as_uri()}" alt="Escudo de la Universidad Nacional Mayor de San Marcos">
  <p class="title">{c['course']} - {manual['title']}</p>
  <p class="subtitle">{c['proposal']}</p>
  <p class="label">{c['group']}</p>
  <p class="names">{names}</p>
  <p class="label">Docente:</p>
  <p class="teacher">{c['teacher']}</p>
  <p class="course">Curso: {c['course']}</p>
  <p class="place">{c['place']}<br>{c['year']}</p>
</section>"""


def _entry(cls: str, target: str, text: str, pg) -> str:
    return (f'<li class="{cls}"><a href="#{target}">{html.escape(text)}</a>'
            f'<span class="dots"></span><span class="pg">{pg}</span></li>')


def toc_html(headings: list, pages: dict, figures: list, tables: list, chapters: bool) -> str:
    items = [_entry(f"l{level}" if not chapters else f"c{level}", hid, text, pages.get(hid, ""))
             for level, hid, text in headings]
    out = f'<section class="toc"><h2>Índice</h2><ol>{"".join(items)}</ol></section>'
    if chapters and figures:
        rows = [_entry("lf", f"fig-{n}", f"Figura {n}. {cap}", pages.get(f"fig-{n}", "")) for n, cap in figures]
        out += f'<section class="toc"><h2>Índice de figuras</h2><ol>{"".join(rows)}</ol></section>'
    if chapters and tables:
        rows = [_entry("lf", f"tab-{n}", f"Tabla {n}. {cap}", pages.get(f"tab-{n}", "")) for n, cap in tables]
        out += f'<section class="toc"><h2>Índice de tablas</h2><ol>{"".join(rows)}</ol></section>'
    return out


def render(html_text: str, pdf: Path, workdir: Path) -> None:
    page = workdir / f"{pdf.stem}.html"
    page.write_text(html_text, encoding="utf-8")
    chrome = next((b for b in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable")
                   if shutil.which(b)), None)
    if chrome is None:
        raise SystemExit("chromium or google-chrome is required")
    subprocess.run(
        [chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
         "--allow-file-access-from-files", "--virtual-time-budget=15000",
         f"--user-data-dir={workdir / 'profile'}", f"--print-to-pdf={pdf}", page.as_uri()],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def _norm(text: str) -> str:
    return re.sub(r"\s+", "", text).lower()


def find_pages(pdf: Path, entries: list[tuple[str, str]], first_page: int) -> dict[str, int]:
    """1-based page where each (id, text) appears, searching forward from the previous one."""
    texts = [_norm(p.extract_text() or "") for p in PdfReader(str(pdf)).pages]
    pages, start = {}, first_page - 1
    for key, text in entries:
        needle = _norm(text)
        for i in range(start, len(texts)):
            if needle in texts[i]:
                pages[key] = i + 1
                start = i
                break
        else:
            print(f"warning: not found in PDF: {text[:60]}")
    return pages


def build(manual: dict, fonts: str, workdir: Path) -> None:
    sources = manual["sources"]
    md_text = "\n\n".join(src.read_text(encoding="utf-8") for src in sources)
    chapters = manual.get("chapters", False)
    title, body, headings, figures, tables = convert(md_text, sources[0].parent, chapters)
    title = title or manual["title"]
    css = CSS.replace("__FOOTER__", manual["footer"])
    # Headings in reading order, then figure and table captions (searched by their first words).
    entries = [(hid, text) for _, hid, text in headings]
    captions = [(f"fig-{n}", f"Figura {n}. {cap[:40]}") for n, cap in figures]
    captions += [(f"tab-{n}", f"Tabla {n}. {cap[:40]}") for n, cap in tables]

    def document(pages: dict, with_body: bool = True) -> str:
        main = f"<main>{body}</main>" if with_body else ""
        return (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{html.escape(title)} · InvestWise</title>'
                f"<style>{fonts}{css}</style></head><body class=\"{'report' if chapters else 'manual'}\">{cover_html(manual)}"
                f"{toc_html(headings, pages, figures, tables, chapters)}{main}</body></html>")

    placeholder = {key: 88 for key, _ in entries + captions}
    front = workdir / f"front-{manual['output'].name}"
    render(document(placeholder, with_body=False), front, workdir)
    toc_pages = len(PdfReader(str(front)).pages)

    def locate(pdf: Path) -> dict[str, int]:
        pages = find_pages(pdf, entries, toc_pages + 1)
        for key, text in captions:  # captions are ordered per kind, not with the headings
            pages.update(find_pages(pdf, [(key, text)], toc_pages + 1))
        return pages

    draft = workdir / f"draft-{manual['output'].name}"
    render(document(placeholder), draft, workdir)
    pages = locate(draft)
    render(document(pages), manual["output"], workdir)
    final = locate(manual["output"])
    if final != pages:
        print("warning: page numbers moved between passes; check the index")
    n = len(PdfReader(str(manual["output"])).pages)
    print(f"{manual['output'].relative_to(ROOT)}: {n} pages, {len(headings)} index entries, "
          f"{len(figures)} figures, {len(tables)} tables")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--keep-html", action="store_true", help="keep the intermediate HTML in docs/entregables/build/")
    args = parser.parse_args()
    fonts = ""  # academic style: system Times New Roman / Liberation Serif, no web fonts
    with tempfile.TemporaryDirectory(prefix="investwise-manuals-") as tmp:
        workdir = Path(tmp)
        for manual in MANUALS:
            build(manual, fonts, workdir)
        if args.keep_html:
            keep = OUT / "build"
            keep.mkdir(exist_ok=True)
            for f in workdir.glob("*.html"):
                shutil.copy(f, keep / f.name)


if __name__ == "__main__":
    main()
