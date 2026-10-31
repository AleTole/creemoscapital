"""
Adapta el informe diario (HTML autocontenido que sube el companero) a la
identidad visual y responsive de Creemos Capital, sin importar el
formato/colores que traiga el archivo original:

  - Reescribe la paleta de colores (variables CSS :root).
  - Agrega meta viewport (el original no lo trae -> se ve mal en mobile).
  - Agrega tipografia Inter + DM Sans (igual que el resto del sitio).
  - Inyecta breakpoints responsive para pantallas chicas.
  - Envuelve el contenido con una cabecera (logo + volver) y un pie de
    pagina con el mismo tono que el resto de creemoscapital.com.

Uso: python recolor_informe.py <archivo.html>
Modifica el archivo in-place.
"""
import re
import sys

BRAND = {
    "--bg": "#051828",
    "--panel": "#050e1c",
    "--border": "rgba(0,212,255,0.38)",
    "--gold": "#00d4ff",
    "--green": "#22c55e",
    "--red": "#ef4444",
    "--text": "#e2e8f0",
    "--muted": "#64748b",
}

VIEWPORT_TAG = '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'

FONT_LINKS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700'
    '&family=DM+Sans:wght@600;700&display=swap" rel="stylesheet">\n'
)

EXTRA_CSS = """
  /* ---- Integracion con creemoscapital.com ---- */
  h1, .cat-label, .card h2 { font-family: 'DM Sans', 'Inter', sans-serif; }
  .ic-header{
    max-width:740px;margin:0 auto 20px;padding-bottom:14px;
    display:flex;align-items:center;justify-content:space-between;gap:12px;
    border-bottom:1px solid var(--border);
  }
  .ic-header a.ic-logo{display:flex;align-items:center;gap:8px;text-decoration:none;}
  .ic-header img{height:28px;width:auto;display:block;}
  .ic-back{
    color:var(--muted);font-size:12px;text-decoration:none;
    display:inline-flex;align-items:center;gap:4px;transition:color .15s;
  }
  .ic-back:hover{color:var(--gold);}
  .ic-footer{
    max-width:740px;margin:28px auto 0;padding-top:16px;
    border-top:1px solid var(--border);text-align:center;
    font-size:11px;color:var(--muted);line-height:1.6;
  }
  .ic-footer a{color:var(--gold);text-decoration:none;}

  /* ---- Responsive ---- */
  @media (max-width:480px){
    body{padding:14px;}
    h1{font-size:19px;}
    .sub{font-size:12px;}
    .price{font-size:24px;}
    .cat-label{font-size:10px;}
    .tab-btn{font-size:10px;padding:8px 2px;min-width:48px;}
    .card{padding:13px 14px;}
    .card h2{font-size:12px;}
    .pivot-pp{padding:8px 14px;}
    .pivot-pp b{font-size:19px;}
    .intraday, .pivot-grid{gap:6px;}
    .lvl{padding:7px 8px;font-size:12px;}
    .ic-header img{height:24px;}
  }
  @media (max-width:360px){
    .tabs{gap:4px;}
    .tab-btn{min-width:42px;font-size:9.5px;}
  }
"""


def header_html() -> str:
    return (
        '<div class="ic-header">\n'
        '  <a href="./index.html" class="ic-logo">\n'
        '    <img src="./img/Logo Creemos Capital Fondo Blanco (2).png" alt="Creemos Capital">\n'
        '  </a>\n'
        '  <a href="./index.html" class="ic-back">&larr; Volver al sitio</a>\n'
        '</div>\n'
    )


def footer_html() -> str:
    return (
        '<div class="ic-footer">\n'
        '  Creemos Capital &middot; Informe de mercado diario &middot; '
        'Solo referencia, no es consejo financiero.<br>\n'
        '  <a href="./index.html">creemoscapital.com</a>\n'
        '</div>\n'
    )


def recolor(html: str) -> str:
    for var, value in BRAND.items():
        html = re.sub(
            rf"({re.escape(var)}\s*:\s*)[^;]+;",
            rf"\g<1>{value};",
            html,
            count=1,
        )
    return html


def ensure_viewport(html: str) -> str:
    if "name=\"viewport\"" in html or "name='viewport'" in html:
        return html
    return re.sub(
        r"(<meta charset=[\"'][^\"']+[\"']>\s*\n)",
        rf"\g<1>{VIEWPORT_TAG}",
        html,
        count=1,
    )


def ensure_fonts(html: str) -> str:
    if "fonts.googleapis.com" in html:
        return html
    return html.replace("<style>", FONT_LINKS + "<style>", 1)


def inject_css(html: str) -> str:
    return html.replace("</style>", EXTRA_CSS + "</style>", 1)


def inject_header_footer(html: str) -> str:
    html = re.sub(r"(<body[^>]*>\s*)", rf"\g<1>{header_html()}", html, count=1)
    html = re.sub(r"(\s*</body>)", f"{footer_html()}\\1", html, count=1)
    return html


def adapt(html: str) -> str:
    html = recolor(html)
    html = ensure_viewport(html)
    html = ensure_fonts(html)
    html = inject_css(html)
    html = inject_header_footer(html)
    return html


def main():
    if len(sys.argv) != 2:
        print("Uso: python recolor_informe.py <archivo.html>")
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    html = adapt(html)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Adaptado a Creemos Capital: {path}")


if __name__ == "__main__":
    main()
