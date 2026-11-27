"""
Adapta el informe diario (HTML autocontenido que sube el companero) para
que se vea como una pagina mas de creemoscapital.com (diseno V2.0, mismo
sistema que la portada: css/evolution.css, claro y oscuro):

  - Barra fija con el menu y el ticker de precios de Bitget, y pie legal,
    iguales al resto del sitio (los activa js/main.js).
  - Los colores del informe pasan a ser los tokens del sistema de diseno
    (por eso cambian solos entre modo claro y oscuro).
  - Titulo = la fecha del informe (en vez de "Informe Multi-Activo...").
  - Agrupa los activos por categoria (Metales/Cripto/Energia/Indices/
    Divisas) en un sidebar fijo tipo acordeon.
  - Reparte las cards de cada activo en grilla de 3 columnas.
  - Responsive: meta viewport, breakpoints para mobile.

Uso: python recolor_informe.py <archivo.html>
Modifica el archivo in-place.
"""
import re
import sys
import unicodedata

# Variables propias del informe -> tokens del sistema de diseno.
# --bg / --text / --muted NO se redefinen: ya existen en evolution.css con
# el mismo nombre (si se redefinieran aqui, romperian el modo claro).
MAPPED_VARS = (
    "--panel:var(--surface);--border:var(--line-2);--gold:var(--blue-text);"
    "--green:var(--up);--red:var(--down);"
)

LOGO_PATH = "./img/Logo Creemos Capital Fondo Blanco (2).png"

ASSET_NAMES = {
    "xau": "Oro", "xag": "Plata",
    "btc": "Bitcoin", "eth": "Ethereum",
    "wti": "Petroleo WTI", "brent": "Petroleo Brent", "natgas": "Gas Natural",
    "us30": "Dow Jones", "sp500": "S&P 500", "us100": "Nasdaq 100",
    "dax": "DAX Alemania", "uk100": "FTSE 100", "japan225": "Nikkei 225",
    "dxy": "Indice Dolar", "eurusd": "Euro/Dolar", "gbpusd": "Libra/Dolar", "usdjpy": "Dolar/Yen",
}

MESES = {
    "ene": "enero", "feb": "febrero", "mar": "marzo", "abr": "abril",
    "may": "mayo", "jun": "junio", "jul": "julio", "ago": "agosto",
    "sep": "septiembre", "sept": "septiembre", "oct": "octubre",
    "nov": "noviembre", "dic": "diciembre",
}

VIEWPORT_TAG = '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'

HEAD_ASSETS = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="./css/evolution.css">
<script>
  (function () {
    var s = null; try { s = localStorage.getItem('cc-theme'); } catch (e) {}
    document.documentElement.setAttribute('data-theme', s === 'light' ? 'light' : 'dark');
  })();
</script>
"""

# Se inyecta al FINAL del <style> del informe: gana sobre su CSS original.
EXTRA_CSS = """
  /* ---- Integracion con creemoscapital.com (diseno V2.0) ---- */
  body.informe { padding: 0 !important; margin: 0; background: var(--bg) !important; color: var(--text) !important; font-family: "Geist", system-ui, -apple-system, "Segoe UI", sans-serif !important; }
  .informe .wrap { max-width: none; margin: 0; padding: calc(var(--top) + 28px) var(--gutter) 40px; }
  .informe h1, .informe h2 { font-family: inherit; }

  /* ---- Cabecera: etiqueta + fecha + resumen ---- */
  .informe .tag { margin-bottom: 14px; }
  .rep-brand { display: block !important; margin: 0 0 26px !important; }
  .rep-brand > div { display: block; }
  .rep-brand h1 { margin: 0 !important; font-size: var(--fs-h2) !important; line-height: 1.08; letter-spacing: -.04em; font-weight: 600; color: var(--text) !important; background: none !important; -webkit-text-fill-color: currentColor; }
  .rep-brand .ic-year { font-size: .5em; font-weight: 500; letter-spacing: 0; color: var(--faint); margin-left: .35em; -webkit-text-fill-color: var(--faint); }
  .rep-brand .sub { margin: 14px 0 0 !important; max-width: 84ch; font-size: var(--fs-small); line-height: 1.65; color: var(--muted) !important; border-left: 3px solid var(--lime); padding-left: 14px; }

  /* ---- Layout: sidebar de categorias (acordeon) + contenido ---- */
  .ic-layout { display: block; }
  .ic-content { min-width: 0; }
  .ic-cat-tabs { display: flex; flex-direction: column; gap: 4px; margin-bottom: 22px; background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-lg); padding: 10px; }
  .ic-cat-item { border-radius: 12px; }
  .ic-cat-btn { position: relative; width: 100%; display: flex; align-items: center; justify-content: space-between; gap: 8px; text-align: left; border-radius: 12px; border: 1px solid transparent; background: transparent; color: var(--muted); font: 600 14px "Geist", sans-serif; cursor: pointer; padding: .7rem .9rem; transition: background-color .2s, color .2s; }
  .ic-cat-btn:hover { background: var(--surface-2); color: var(--text); }
  .ic-cat-item.open .ic-cat-btn { background: var(--blue-soft); color: var(--blue-text); }
  .ic-cat-chevron { font-size: .7rem; opacity: .6; transition: transform .25s; flex-shrink: 0; }
  .ic-cat-item.open .ic-cat-chevron { transform: rotate(90deg); }
  .ic-cat-name { display: block; }
  .ic-cat-assets-preview { display: block; font-size: 11px; font-weight: 400; color: var(--faint); margin-top: 2px; }
  .ic-cat-item.open .ic-cat-assets-preview { display: none; }
  .ic-cat-assets-list { display: none; flex-direction: column; gap: 2px; padding: 4px 4px 8px 12px; }
  .ic-cat-item.open .ic-cat-assets-list { display: flex; }
  .ic-cat-assets-list .tab-btn { flex: none; text-align: left; border-radius: 10px; background: transparent; border: 1px solid transparent; color: var(--muted); cursor: pointer; padding: .45rem .75rem; font-size: inherit; transition: background-color .2s, color .2s; }
  .ic-cat-assets-list .tab-btn:hover { background: var(--surface-2); color: var(--text); }
  .ic-cat-assets-list .tab-btn.active { background: var(--text); color: var(--bg); border-color: var(--text); }
  .ic-asset-code { display: block; font: 600 12px "Geist Mono", ui-monospace, monospace; letter-spacing: .02em; text-transform: uppercase; color: inherit; }
  .ic-asset-name { display: block; font-size: 11px; font-weight: 400; opacity: .7; margin-top: 1px; }
  .ic-cat-group { display: none; }
  .ic-cat-group.active { display: block; }

  /* ---- Tarjetas (el .card del informe, sin los efectos de la portada) ---- */
  .informe .card { display: block; position: relative; overflow: visible; background: var(--surface); border: 1px solid var(--line); border-radius: var(--r); padding: 15px 17px; margin: 0; box-shadow: none; transform: none; transition: border-color .2s; }
  .informe .card:hover { transform: none; border-color: var(--line-2); }
  .informe .card h2 { margin: 0 0 8px; font-size: 12px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--blue-text); }
  .informe .card.risk h2, .informe .risk h2 { color: var(--down); }
  .informe .card .sub { font-size: 12.5px; line-height: 1.5; border: 0; padding-left: 0; font-weight: 400; color: var(--muted); }
  .informe .price { font: 600 26px "Geist Mono", ui-monospace, monospace; letter-spacing: -.02em; color: var(--up); }
  .informe .price.down { color: var(--down); }
  .informe ul { margin: 6px 0 0; padding-left: 18px; font-size: 13px; line-height: 1.55; color: var(--muted); }
  .informe li::marker { color: var(--faint); }
  .informe .zone { border-radius: 12px; padding: 8px 11px; margin-bottom: 6px; font-size: 12.5px; color: var(--text); }
  .informe .zone b { font-size: 13px; }
  .informe .zone-supply { background: color-mix(in srgb, var(--down) 10%, transparent); border: 1px solid color-mix(in srgb, var(--down) 32%, transparent); }
  .informe .zone-demand { background: color-mix(in srgb, var(--up) 10%, transparent); border: 1px solid color-mix(in srgb, var(--up) 32%, transparent); }
  .informe .lvl { background: var(--surface-2); border: 1px solid var(--line); border-radius: 12px; padding: 7px 10px; font-size: 12.5px; }
  .informe .lvl b { font: 600 13px "Geist Mono", ui-monospace, monospace; }
  .informe .note { background: var(--surface-2); border: 1px dashed var(--line-2); border-radius: 12px; color: var(--muted); }
  .informe .foot { color: var(--faint); }

  /* ---- Panel de un activo ---- */
  .panel.active { display: flex; flex-direction: column; gap: 12px; }
  .ic-panel-left, .ic-panel-right { display: flex; flex-direction: column; gap: 12px; }

  /* ---- Pivote compacto en una fila ---- */
  .pivot-wrap { flex-direction: row !important; align-items: stretch !important; gap: 8px !important; }
  .pivot-pp { flex-shrink: 0; display: flex; flex-direction: column; justify-content: center; padding: 6px 14px; background: var(--lime-soft); border: 1px solid color-mix(in srgb, var(--lime) 45%, transparent); border-radius: 14px; }
  .pivot-pp span { color: var(--muted); }
  .pivot-pp b { font: 600 17px "Geist Mono", ui-monospace, monospace; color: var(--lime-text); }
  .pivot-grid { grid-template-columns: repeat(4, 1fr) !important; flex: 1; gap: 6px !important; }
  .intraday { gap: 6px; }

  /* Sidebar fijo + contenido en grilla, en pantallas grandes */
  @media (min-width: 900px) {
    .informe .wrap { padding-left: calc(272px + var(--gutter)); }
    .ic-cat-tabs { position: fixed; left: 0; top: var(--top); bottom: 0; width: 256px; z-index: 20; margin: 0; overflow-y: auto; border-radius: 0; border-width: 0 1px 0 0; background: var(--bg-2); padding: 20px 12px; }
    .ic-content { max-width: 1320px; margin: 0 auto; }
    .panel.active { display: grid; grid-template-columns: repeat(3, 1fr); grid-auto-rows: min-content; gap: 12px; }
    .ic-panel-left, .ic-panel-right { display: contents; }
  }
  @media (min-width: 1500px) { .ic-content { max-width: 1500px; } }

  @media (max-width: 480px) {
    .informe .price { font-size: 24px; }
    .pivot-wrap { flex-direction: column !important; }
    .pivot-grid { grid-template-columns: 1fr 1fr !important; }
    .pivot-pp { padding: 8px 14px; }
    .informe .lvl { padding: 7px 8px; font-size: 12px; }
  }
"""

NAVBAR_HTML = """<header class="nav" id="navbar">
  <div class="container">
    <a class="brand" href="./index.html" aria-label="Creemos Capital, inicio">
      <img src="./img/Logo Creemos Capital Fondo Blanco (2).png" alt="">
      <span class="brand-name">Creemos Capital<small>TRADING EN VIVO</small></span>
    </a>
    <nav class="nav-links" aria-label="Principal">
      <a href="./index.html#mercados">Mercados</a>
      <a href="./index.html#serie">Reto <img class="bg-ico" src="./img/bitget.webp" alt="" width="18" height="18">Bitget</a>
      <a href="./index.html#unete">&Uacute;nete</a>
      <a href="./index.html#noticias">Noticias</a>
      <a href="https://academy.creemoscapital.com/cursos">Cursos</a>
      <a href="./informe.html" aria-current="page">Informe</a>
      <a href="./academy.html" class="pill">Academy</a>
    </nav>
    <div class="nav-actions">
      <button class="icon-btn" id="theme" type="button" aria-label="Cambiar entre modo claro y oscuro">
        <svg class="theme-ico-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
        <svg class="theme-ico-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
      </button>
      <a class="btn btn-primary btn-sm" href="./index.html#unete">&Uacute;nete gratis</a>
      <button class="icon-btn menu-btn" id="menu" type="button" aria-label="Abrir men&uacute;" aria-expanded="false" aria-controls="mobile-menu">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 8h16M4 16h16"/></svg>
      </button>
    </div>
  </div>
  <div class="ticker" aria-label="Precios en tiempo real de Bitget">
    <a class="ticker-badge" href="https://partner.bitget.com/bg/E1X2FN" target="_blank" rel="noopener noreferrer" aria-label="Bitget">
      <span>Powered by</span>
      <b><img src="./img/bitget.webp" alt="" width="16" height="16">Bitget</b>
    </a>
    <div class="ticker-view">
      <div id="ticker-items"><span class="ticker-empty">Cargando precios en tiempo real&hellip;</span></div>
    </div>
  </div>
</header>
<div class="mobile-menu" id="mobile-menu">
  <a href="./index.html#mercados">Mercados</a>
  <a href="./index.html#serie">Reto <img class="bg-ico" src="./img/bitget.webp" alt="" width="18" height="18">Bitget</a>
  <a href="./index.html#unete">&Uacute;nete</a>
  <a href="./index.html#noticias">Noticias</a>
  <a href="https://academy.creemoscapital.com/cursos">Cursos</a>
  <a href="./informe.html">Informe</a>
  <a href="./academy.html">Academy</a>
  <a class="btn btn-primary" href="./index.html#unete">&Uacute;nete a la comunidad</a>
</div>
"""

FOOTER_HTML = """<footer>
  <div class="container">
    <div class="foot-grid">
      <div>
        <a class="brand" href="./index.html" aria-label="Creemos Capital, inicio">
          <img src="./img/Logo Creemos Capital Fondo Blanco (2).png" alt="">
          <span class="brand-name">Creemos Capital<small>TRADING EN VIVO</small></span>
        </a>
        <p>Informe de mercado diario &middot; an&aacute;lisis de mercados en vivo, formaci&oacute;n y comunidad.</p>
      </div>
      <div>
        <h5>Explora</h5>
        <a href="./index.html#mercados">Mercados</a>
        <a href="./index.html#serie">Reto <img class="bg-ico" src="./img/bitget.webp" alt="" width="18" height="18">Bitget</a>
        <a href="./index.html#noticias">Noticias</a>
        <a href="./informe.html">Informe diario</a>
      </div>
      <div>
        <h5>Aprende</h5>
        <a href="./academy.html">Academy</a>
        <a href="https://academy.creemoscapital.com/cursos">Cursos</a>
        <a href="./index.html#unete">&Uacute;nete gratis</a>
      </div>
      <div>
        <h5>Comunidad</h5>
        <a href="https://t.me/creemoscapitaloficial" target="_blank" rel="noopener">Telegram</a>
        <a href="https://www.youtube.com/@CreemosCapital" target="_blank" rel="noopener">YouTube</a>
        <a href="https://kick.com/creemoscapital" target="_blank" rel="noopener">Kick</a>
        <a href="mailto:info@creemoscapital.com">info@creemoscapital.com</a>
      </div>
    </div>
    <div class="legal">
      <p><strong>&#9888; Aviso legal:</strong> El contenido de este informe es exclusivamente con fines educativos e informativos y no debe considerarse como asesoramiento financiero, legal o fiscal. El trading y la inversi&oacute;n en los mercados financieros conllevan un alto nivel de riesgo, incluyendo la posibilidad de perder la totalidad del capital invertido.</p>
      <p><strong>Al usar este contenido, aceptas que eres el &uacute;nico responsable de tus decisiones financieras. &iexcl;Opera con responsabilidad!</strong></p>
    </div>
    <p class="copy">&copy; 2026 Creemos Capital. Todos los derechos reservados.</p>
  </div>
</footer>

<script src="./js/data.js" defer></script>
<script src="./js/main.js" defer></script>
"""

CATEGORY_SCRIPT = """
<script>
  document.querySelectorAll('.ic-cat-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var item = btn.closest('.ic-cat-item');
      var cat = btn.dataset.cat;

      document.querySelectorAll('.ic-cat-item').forEach(function (it) { it.classList.remove('open'); });
      document.querySelectorAll('.ic-cat-group').forEach(function (g) { g.classList.remove('active'); });

      item.classList.add('open');
      var group = document.querySelector('.ic-cat-group[data-cat="' + cat + '"]');
      if (!group) return;
      group.classList.add('active');

      if (!group.querySelector('.panel.active')) {
        var firstTab = item.querySelector('.tab-btn');
        if (firstTab) {
          document.querySelectorAll('.tab-btn').forEach(function (b) { b.classList.remove('active'); });
          document.querySelectorAll('.panel').forEach(function (p) { p.classList.remove('active'); });
          firstTab.classList.add('active');
          var firstPanel = document.getElementById(firstTab.dataset.tab);
          if (firstPanel) firstPanel.classList.add('active');
        }
      }
    });
  });
</script>
"""


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def split_top_level_divs(fragment: str, marker: str):
    """Devuelve los bloques <div class="marker...">...</div> de nivel superior
    dentro de fragment, resolviendo correctamente divs anidados."""
    results = []
    idx = fragment.find(marker)
    while idx != -1:
        open_end = fragment.find(">", idx)
        if open_end == -1:
            break
        pos = open_end + 1
        depth = 1
        while depth > 0:
            next_open = fragment.find("<div", pos)
            next_close = fragment.find("</div>", pos)
            if next_close == -1:
                pos = len(fragment)
                break
            if next_open != -1 and next_open < next_close:
                depth += 1
                pos = next_open + 4
            else:
                depth -= 1
                pos = next_close + 6
        results.append(fragment[idx:pos])
        idx = fragment.find(marker, pos)
    return results


def recolor(html: str) -> str:
    """Sustituye el :root del informe por el mapeo a los tokens del sitio."""
    return re.sub(r":root\s*\{[^}]*\}", ":root{" + MAPPED_VARS + "}", html, count=1)


def ensure_viewport(html: str) -> str:
    if "name=\"viewport\"" in html or "name='viewport'" in html:
        return html
    return re.sub(r"(<meta charset=[\"'][^\"']+[\"']>\s*\n)", rf"\g<1>{VIEWPORT_TAG}", html, count=1)


def ensure_head_assets(html: str) -> str:
    if "css/evolution.css" in html:
        return html
    return html.replace("<style>", HEAD_ASSETS + "<style>", 1)


def mark_document(html: str) -> str:
    """Tema oscuro por defecto en <html> y clase 'informe' en <body>."""
    html = re.sub(r"<html([^>]*)>", lambda m: m.group(0) if "data-theme" in m.group(1) else f'<html{m.group(1)} data-theme="dark">', html, count=1)
    html = re.sub(r"<body([^>]*)>", lambda m: f'<body class="informe no-js"{m.group(1)}>' if "class=" not in m.group(1) else m.group(0), html, count=1)
    return html


def rename_report_brand(html: str) -> str:
    """El informe usa .brand para su cabecera; el sitio usa .brand para el logo
    de la barra. Se renombra el del informe para que no choquen."""
    html = html.replace('class="brand"', 'class="rep-brand"')
    html = re.sub(r"(?<![\w-])\.brand(?![\w-])", ".rep-brand", html)
    return html


def replace_embedded_logo(html: str) -> str:
    return re.sub(r'src="data:image/[a-zA-Z+]+;base64,[A-Za-z0-9+/=]+"', f'src="{LOGO_PATH}"', html)


def strip_brand_logo_img(html: str) -> str:
    """Saca el logo duplicado dentro de la cabecera (ya esta en la barra)."""
    return re.sub(
        rf'<img src="{re.escape(LOGO_PATH)}" alt="Creemos Capital">\s*',
        "",
        html,
        count=1,
    )


def fix_title(html: str) -> str:
    m = re.search(
        r'<h1>[^<]*</h1>\s*<div class="sub">\s*'
        r'([A-Za-zÁÉÍÓÚáéíóúñÑ]+)\s+(\d{1,2})\s+([A-Za-zÁÉÍÓÚáéíóúñÑ]+)\.?\s+(\d{4})\s*'
        r'[··]\s*(.*?)</div>',
        html,
        re.S,
    )
    if not m:
        return html
    weekday, day, month_raw, year, rest = m.groups()
    month_full = MESES.get(month_raw.strip(".").lower(), month_raw)
    title = f"{weekday.capitalize()} {int(day)} de {month_full}"
    new_block = (
        '<span class="tag"><i></i>Informe diario</span>\n'
        f'    <h1>{title}<span class="ic-year"> {year}</span></h1>\n'
        f'    <div class="sub">{rest.strip()}</div>'
    )
    return html[: m.start()] + new_block + html[m.end() :]


def inject_css(html: str) -> str:
    return html.replace("</style>", EXTRA_CSS + "</style>", 1)


def group_by_category(html: str) -> str:
    cat_pattern = re.compile(
        r'<div class="cat-label">([^<]+)</div>\s*<div class="tabs">\s*((?:<div class="tab-btn.*?</div>\s*)+)</div>',
        re.S,
    )
    categories = cat_pattern.findall(html)
    if not categories:
        return html

    panels_match = re.search(r'<div class="allpanels">(.*?)\n\s*</div>\s*\n\s*<div class="foot">', html, re.S)
    if not panels_match:
        return html
    panels_blob = panels_match.group(1)

    chunks = re.split(r"(?=<!--\s*\w+\s*-->)", panels_blob)
    panels_by_id = {}
    for chunk in chunks:
        m = re.search(r'id="(\w+)"', chunk)
        if m:
            panels_by_id[m.group(1)] = chunk.strip()

    groups_html = []
    items_html = []
    for i, (cat_name, tabs_inner) in enumerate(categories):
        cat_name = cat_name.strip()
        slug = slugify(cat_name)
        asset_entries = re.findall(r'<div class="tab-btn( active)?" data-tab="(\w+)">', tabs_inner)
        asset_ids = [aid for _, aid in asset_entries]
        group_panels = "\n".join(panels_by_id.get(aid, "") for aid in asset_ids)
        active_cls = " active" if i == 0 else ""
        open_cls = " open" if i == 0 else ""
        asset_names = ", ".join(ASSET_NAMES.get(aid, aid.upper()) for aid in asset_ids)

        asset_buttons = "\n    ".join(
            f'<div class="tab-btn{was_active}" data-tab="{aid}">'
            f'<span class="ic-asset-code">{aid.upper()}</span>'
            f'<span class="ic-asset-name">{ASSET_NAMES.get(aid, "")}</span>'
            f'</div>'
            for was_active, aid in asset_entries
        )

        items_html.append(
            f'<div class="ic-cat-item{open_cls}" data-cat="{slug}">\n'
            f'  <button class="ic-cat-btn" data-cat="{slug}">\n'
            f'    <span><span class="ic-cat-name">{cat_name}</span>'
            f'<span class="ic-cat-assets-preview">{asset_names}</span></span>\n'
            f'    <span class="ic-cat-chevron">&#9656;</span>\n'
            f'  </button>\n'
            f'  <div class="ic-cat-assets-list">\n    {asset_buttons}\n  </div>\n'
            f'</div>'
        )
        groups_html.append(
            f'<div class="ic-cat-group{active_cls}" data-cat="{slug}">\n'
            f'  <div class="allpanels">\n{group_panels}\n  </div>\n'
            f'</div>'
        )

    new_block = (
        '<div class="ic-layout">\n'
        '<nav class="ic-cat-tabs">\n' + "\n".join(items_html) + "\n</nav>\n"
        '<div class="ic-content">\n' + "\n\n".join(groups_html) + "\n</div>\n"
        '</div>\n\n'
    )

    start = html.index(f'<div class="cat-label">{categories[0][0]}')
    foot_start = html.index('<div class="foot">', panels_match.start())
    html = html[:start] + new_block + html[foot_start:]
    return html


def restructure_panel_cards(html: str) -> str:
    """Divide las cards de cada activo en 2 columnas: datos (izq) y
    Sesgo/Riesgo (der), con alto natural (sin espacios vacios forzados)."""
    comment_re = re.compile(r"(<!--\s*\w+\s*-->)")
    parts = comment_re.split(html)
    for i in range(2, len(parts), 2):
        chunk = parts[i]
        panels = split_top_level_divs(chunk, '<div class="panel')
        if not panels:
            continue
        panel_html = panels[0]
        open_match = re.match(r'(<div class="panel[^"]*"[^>]*>)', panel_html)
        if not open_match or not panel_html.endswith("</div>"):
            continue
        inner = panel_html[open_match.end() : -len("</div>")]
        cards = split_top_level_divs(inner, '<div class="card')
        if len(cards) < 2:
            continue
        left = cards[:4]
        right = cards[4:]
        new_panel = (
            open_match.group(1) + "\n"
            '<div class="ic-panel-left">\n' + "\n".join(left) + "\n</div>\n"
            '<div class="ic-panel-right">\n' + "\n".join(right) + "\n</div>\n"
            "</div>"
        )
        start = chunk.find(panel_html)
        parts[i] = chunk[:start] + new_panel + chunk[start + len(panel_html) :]
    return "".join(parts)


def inject_navbar_footer(html: str) -> str:
    html = re.sub(r"(<body[^>]*>\s*)", lambda m: m.group(1) + NAVBAR_HTML, html, count=1)
    html = re.sub(r"(\s*</body>)", lambda m: FOOTER_HTML + CATEGORY_SCRIPT + m.group(1), html, count=1)
    return html


def adapt(html: str) -> str:
    html = recolor(html)
    html = ensure_viewport(html)
    html = replace_embedded_logo(html)
    html = strip_brand_logo_img(html)
    html = rename_report_brand(html)
    html = fix_title(html)
    html = mark_document(html)
    html = ensure_head_assets(html)
    html = inject_css(html)
    html = restructure_panel_cards(html)
    html = group_by_category(html)
    html = inject_navbar_footer(html)
    return html


def validar(html: str):
    """Comprueba que el informe adaptado quedo con el diseno del sitio.
    Devuelve (errores, avisos). Con errores NO se publica: asi nunca sale una pagina rota."""
    errores, avisos = [], []
    if "css/evolution.css" not in html:
        errores.append("falta la hoja de estilos del sitio (css/evolution.css)")
    if html.count('id="ticker-items"') != 1:
        errores.append("falta la barra con el ticker de precios")
    if 'class="ic-cat-tabs"' not in html or "ic-cat-item" not in html:
        errores.append("no se reconocieron las categorias de activos (Metales, Cripto...): el formato del informe cambio")
    tabs = re.findall(r'<div class="tab-btn[^"]*" data-tab="(\w+)"', html)
    if not tabs:
        errores.append("no se encontro ningun activo en el menu lateral")
    for t in tabs:
        if f'id="{t}"' not in html:
            errores.append(f"el activo {t.upper()} esta en el menu pero no tiene su panel")
    if 'class="ic-year"' not in html:
        avisos.append("no se pudo convertir el titulo a la fecha (se deja el titulo original del informe)")
    if "data:image" in html:
        avisos.append("quedan imagenes incrustadas en base64 (pesan mucho)")
    return errores, avisos


def main():
    if len(sys.argv) != 2:
        print("Uso: python recolor_informe.py <archivo.html>")
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    html = adapt(html)

    errores, avisos = validar(html)
    for a in avisos:
        print(f"::warning::Informe: {a}")
    if errores:
        for e in errores:
            print(f"::error::Informe NO publicado: {e}")
        print("El archivo no se modifico. En el sitio sigue el ultimo informe valido.", file=sys.stderr)
        sys.exit(1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Adaptado a Creemos Capital: {path}")


if __name__ == "__main__":
    main()
