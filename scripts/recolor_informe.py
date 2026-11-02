"""
Adapta el informe diario (HTML autocontenido que sube el companero) para
que se vea como una pagina mas de creemoscapital.com, no una pagina aparte:

  - Navbar fijo real (logo, links, ticker OKX en vivo) y footer legal,
    copiados tal cual del resto del sitio (Tailwind + main.js/data.js).
  - Reescribe la paleta de colores (variables CSS :root del informe).
  - Titulo = la fecha del informe (en vez de "Informe Multi-Activo...").
  - Agrupa los activos por categoria (Metales/Cripto/Energia/Indices/
    Divisas) en un sidebar fijo tipo acordeon (click en la categoria
    despliega sus activos con su mnemotecnico + nombre).
  - Reparte las cards de cada activo en 2 columnas (datos a la izquierda,
    Sesgo/Riesgo a la derecha) con alto natural, sin espacios vacios.
  - Pivote en una sola fila compacta.
  - Responsive: meta viewport, breakpoints para mobile.

Uso: python recolor_informe.py <archivo.html>
Modifica el archivo in-place.
"""
import re
import sys
import unicodedata

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

LOGO_PATH = "./img/Logo Creemos Capital Fondo Blanco (2).png"
OKX_LOGO_PATH = "./img/OKX-250x141.png"

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
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.tailwindcss.com"></script>
<script>
  tailwind.config = {
    theme: {
      extend: {
        colors: {
          navy:  { 900: '#050d1a', 800: '#0a1628', 700: '#0f2040', 600: '#153060' },
          sky:   { 400: '#00d4ff', 500: '#00b8e0', 600: '#0099cc' },
          gold:  { 400: '#fbbf24', 500: '#f59e0b' },
          long:  '#22c55e',
          short: '#ef4444',
        },
        fontFamily: {
          sans:    ['Inter', 'system-ui', 'sans-serif'],
          display: ['Space Grotesk', 'system-ui', 'sans-serif'],
        },
      }
    }
  }
</script>
"""

# CSS del navbar/ticker/footer, copiado del resto del sitio (academy.html)
EXTRA_CSS = """
  /* ---- Integracion con creemoscapital.com (navbar/ticker/footer) ---- */
  #navbar {
    transition: background 0.3s ease, box-shadow 0.3s ease;
    background: rgba(5,13,26,0.97);
    box-shadow: 0 1px 20px rgba(0,0,0,0.5);
  }
  .nav-link {
    font-size: 0.8rem; letter-spacing: 0.1em; text-transform: uppercase;
    color: rgba(226,232,240,0.7); text-decoration: none; transition: color 0.2s;
  }
  .nav-link:hover, .nav-link.active { color: #00d4ff; }
  .nav-cta {
    display: inline-flex; align-items: center; justify-content: center; text-align: center;
    padding: 0.5rem 1.25rem; background: linear-gradient(135deg,#22c55e,#15803d);
    color: #04160c !important; font-weight: 700; font-size: 0.8rem; text-transform: uppercase;
    letter-spacing: 0.04em; border-radius: 999px; text-decoration: none;
    box-shadow: 0 0 16px rgba(34,197,94,0.45); transition: transform 0.2s, box-shadow 0.2s;
    animation: ctaPulse 2s ease-in-out infinite;
  }
  .nav-cta:hover { transform: translateY(-1px); box-shadow: 0 0 24px rgba(34,197,94,0.65); }
  @keyframes ctaPulse {
    0%, 100% { box-shadow: 0 0 16px rgba(34,197,94,0.45); }
    50%      { box-shadow: 0 0 28px rgba(34,197,94,0.9); }
  }
  .nav-academy {
    display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.4rem 1rem;
    background: linear-gradient(135deg, rgba(0,212,255,0.18), rgba(99,102,241,0.18));
    border: 1px solid rgba(0,212,255,0.55); border-radius: 999px; color: #00d4ff !important;
    font-size: 0.78rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;
    text-decoration: none; box-shadow: 0 0 14px rgba(0,212,255,0.3);
    transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
  }
  .nav-academy:hover { transform: translateY(-1px); border-color: #00d4ff; box-shadow: 0 0 22px rgba(0,212,255,0.55); }

  @keyframes tickerScroll { from { transform: translateX(0); } to { transform: translateX(-50%); } }
  #okx-ticker-items:hover { animation-play-state: paused; }
  .okx-item  { display:inline-flex;align-items:center;gap:0.45rem;padding:0 1.1rem; }
  .okx-name  { font-size:0.72rem;letter-spacing:0.06em;color:#64748b;font-weight:500; }
  .okx-price { font-size:0.8rem;font-family:'Space Grotesk',sans-serif;font-weight:600;color:#e2e8f0; }
  .okx-pct   { font-size:0.72rem;font-weight:600; }
  .okx-pos   { color:#22c55e; }
  .okx-neg   { color:#ef4444; }
  .okx-sep   { color:#1e3a5f;font-size:1rem;padding:0 0.25rem; }

  body {
    padding-top: 118px; padding-bottom: 28px; font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
    background:
      radial-gradient(ellipse at 15% 0%, rgba(0,212,255,0.14) 0%, transparent 55%),
      radial-gradient(ellipse at 85% 10%, rgba(99,102,241,0.12) 0%, transparent 50%),
      var(--bg);
    background-attachment: fixed;
  }
  h1, .cat-label, .card h2 { font-family: 'DM Sans', 'Inter', sans-serif; }

  /* ---- Titulo = fecha ---- */
  .brand h1{
    background:linear-gradient(135deg,#f1f5f9,#b9e8ff 60%,var(--gold));
    -webkit-background-clip:text; background-clip:text; color:transparent;
    font-size:clamp(1.7rem,3vw,2.3rem); font-weight:700; letter-spacing:-0.01em;
  }
  .brand .ic-year{
    font-size:0.62em; font-weight:600; letter-spacing:0;
    background:none; -webkit-text-fill-color:#94a3b8; color:#94a3b8;
  }
  .brand .sub{
    font-size:0.92rem; font-weight:600; color:#cbd5e1; margin-top:10px;
    line-height:1.6; max-width:900px;
    border-left:3px solid rgba(0,212,255,0.5); padding-left:12px;
  }

  /* ---- Layout: sidebar de categorias (acordeon) + contenido ---- */
  .wrap{ max-width:740px; }
  .ic-layout{ display:block; }
  .ic-content{ min-width:0; }

  .ic-cat-tabs{
    display:flex; flex-direction:column; gap:4px; margin-bottom:20px;
    background:linear-gradient(160deg,#061325,var(--panel) 55%);
    border:1px solid var(--border); border-radius:16px; padding:10px;
  }
  .ic-cat-item{ border-radius:10px; }
  .ic-cat-btn{
    position:relative; width:100%; display:flex; align-items:center; justify-content:space-between; gap:8px;
    text-align:left; border-radius:10px; border:1px solid transparent;
    background:transparent; color:#94a3b8; font-size:0.8rem; font-weight:700;
    letter-spacing:0.03em; text-transform:uppercase; cursor:pointer; padding:0.7rem 0.9rem;
    transition:background .18s,color .18s,border-color .18s;
  }
  .ic-cat-btn:hover{ background:rgba(0,212,255,0.08); color:#e2e8f0; }
  .ic-cat-item.open .ic-cat-btn{
    background:linear-gradient(135deg, rgba(0,212,255,0.18), rgba(99,102,241,0.18));
    color:var(--gold); border-color:rgba(0,212,255,0.45);
  }
  .ic-cat-chevron{ font-size:0.7rem; opacity:0.55; transition:transform .2s; flex-shrink:0; }
  .ic-cat-item.open .ic-cat-chevron{ transform:rotate(90deg); }
  .ic-cat-name{ display:block; }
  .ic-cat-assets-preview{
    display:block; font-size:0.65rem; font-weight:500; letter-spacing:0.01em;
    text-transform:none; color:#64748b; margin-top:2px;
  }
  .ic-cat-item.open .ic-cat-assets-preview{ display:none; }

  .ic-cat-assets-list{ display:none; flex-direction:column; gap:2px; padding:4px 4px 8px 14px; }
  .ic-cat-item.open .ic-cat-assets-list{ display:flex; }
  .ic-cat-assets-list .tab-btn{
    text-align:left; border-radius:8px; background:transparent; border:1px solid transparent;
    color:#94a3b8; cursor:pointer; padding:0.45rem 0.75rem;
  }
  .ic-cat-assets-list .tab-btn:hover{ background:rgba(0,212,255,0.08); transform:none; }
  .ic-cat-assets-list .tab-btn.active{
    background:linear-gradient(135deg,var(--gold),#0099cc);
    box-shadow:0 0 12px rgba(0,212,255,0.35); transform:none;
  }
  .ic-asset-code{
    display:block; font-size:0.78rem; font-weight:700; letter-spacing:0.02em;
    text-transform:uppercase; color:inherit;
  }
  .ic-asset-name{
    display:block; font-size:0.64rem; font-weight:500; color:#64748b; margin-top:1px;
  }
  .ic-cat-assets-list .tab-btn.active .ic-asset-name{ color:rgba(4,18,28,0.65); }

  .ic-cat-group{ display:none; }
  .ic-cat-group.active{ display:block; }

  /* ---- Panel de un activo: grilla compacta, 2 filas de 3 cards ---- */
  .panel.active{ display:flex; flex-direction:column; gap:12px; }
  .card{ margin-bottom:0 !important; padding:13px 15px !important; }
  .card h2{ font-size:12px !important; margin-bottom:6px !important; }
  .price{ font-size:22px !important; }
  .pivot-pp b{ font-size:17px !important; }
  .lvl{ padding:7px 9px !important; }
  .lvl b{ font-size:13px !important; }
  .zone{ padding:7px 10px !important; margin-bottom:6px !important; font-size:12px !important; }
  .card ul{ font-size:12.5px !important; line-height:1.45 !important; }
  .card .sub{ font-size:12px !important; border:none !important; padding-left:0 !important; font-weight:400 !important; color:#94a3b8 !important; }

  /* ---- Pivote compacto en una fila ---- */
  .pivot-wrap{ flex-direction:row !important; align-items:stretch !important; gap:8px !important; }
  .pivot-pp{ flex-shrink:0; display:flex; flex-direction:column; justify-content:center; padding:6px 12px !important; }
  .pivot-grid{ grid-template-columns:repeat(4,1fr) !important; flex:1; gap:6px !important; }

  /* Sidebar fijo pegado a la ventana + contenido centrado, en pantallas grandes */
  @media (min-width:900px){
    body{ padding-left:276px; }
    .wrap{ max-width:none; margin:0; }
    .ic-content{ max-width:1320px; margin:0 auto; padding-left:8px; }

    .ic-cat-tabs{
      position:fixed; left:0; top:110px; bottom:0; width:258px; z-index:20;
      margin-bottom:0; overflow-y:auto; border-radius:0;
      border-right:1px solid var(--border);
      padding:20px 12px; box-shadow:6px 0 30px rgba(0,0,0,0.35);
    }
    .ic-cat-item.open .ic-cat-btn::before{
      content:''; position:absolute; left:-10px; top:50%; transform:translateY(-50%);
      width:4px; height:60%; border-radius:4px;
      background:linear-gradient(180deg,var(--gold),#6366f1);
    }

    /* 3 columnas -> 6 cards caen en 2 filas parejas, en vez de 1 columna larga */
    .panel.active{
      display:grid; grid-template-columns:repeat(3,1fr); grid-auto-rows:min-content; gap:12px;
    }
    .ic-panel-left, .ic-panel-right{ display:contents; }
  }
  @media (min-width:1500px){
    .ic-content{ max-width:1500px; }
  }

  /* ---- Cards con borde degradado estilo Academy ---- */
  .card{ position:relative; overflow:hidden; transition:border-color .2s, box-shadow .2s; }
  .card::before{
    content:''; position:absolute; inset:-1px; border-radius:10px; padding:1px;
    background:linear-gradient(135deg, rgba(0,212,255,0.35), rgba(99,102,241,0.25), rgba(0,212,255,0.35));
    -webkit-mask:linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
    -webkit-mask-composite:xor; mask-composite:exclude;
    opacity:0; transition:opacity .25s; pointer-events:none;
  }
  .card:hover::before{ opacity:1; }
  .card:hover{border-color:rgba(0,212,255,0.55);box-shadow:0 6px 22px rgba(0,184,224,0.12);}

  .brand{grid-template-columns:1fr !important;}
  .brand h1, .brand .sub{grid-column:1 !important;}

  @media (max-width:480px){
    body{padding:14px;padding-top:112px;}
    h1{font-size:19px;}
    .sub{font-size:13px !important;}
    .price{font-size:24px;}
    .cat-label{font-size:10px;}
    .card{padding:13px 14px;}
    .card h2{font-size:12px;}
    .pivot-wrap{ flex-direction:column !important; }
    .pivot-grid{ grid-template-columns:1fr 1fr !important; }
    .pivot-pp{padding:8px 14px;}
    .pivot-pp b{font-size:19px;}
    .intraday, .pivot-grid{gap:6px !important;}
    .lvl{padding:7px 8px;font-size:12px;}
  }
"""

NAVBAR_HTML = """<header id="navbar" class="fixed top-0 left-0 right-0 z-40">
  <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
    <a href="./index.html">
      <img src="./img/Logo Creemos Capital Fondo Blanco (2).png" alt="Creemos Capital" class="h-10 w-auto">
    </a>
    <nav class="hidden md:flex items-center gap-8">
      <a href="./index.html#live" class="nav-link">En Vivo</a>
      <a href="https://academy.creemoscapital.com/cursos" class="nav-link">Cursos</a>
      <a href="./informe.html" class="nav-link active">Informe</a>
      <a href="./academy.html" class="nav-academy">\U0001F393 Academy</a>
    </nav>
    <div class="flex items-center gap-3">
      <a href="./index.html#registro" class="nav-cta">Unete a la Comunidad</a>
      <button onclick="toggleMenu()" class="md:hidden p-2 text-slate-300">
        <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 6h16M4 12h16M4 18h16"/>
        </svg>
      </button>
    </div>
  </div>
  <div id="mobile-menu" class="hidden md:hidden bg-navy-900/98 border-t border-sky-900/30 px-6 py-5 flex flex-col gap-5">
    <a href="./index.html#live" onclick="closeMenu()" class="nav-link">En Vivo</a>
    <a href="https://academy.creemoscapital.com/cursos" onclick="closeMenu()" class="nav-link">Cursos</a>
    <a href="./informe.html" onclick="closeMenu()" class="nav-link active">Informe</a>
    <a href="./academy.html" onclick="closeMenu()" class="nav-academy justify-center">\U0001F393 Academy</a>
    <a href="./index.html#registro" onclick="closeMenu()" class="nav-cta justify-center">Unete a la Comunidad</a>
  </div>
</header>

<div style="position:fixed;top:64px;left:0;right:0;z-index:35;background:rgba(5,14,28,0.97);border-bottom:1px solid rgba(0,212,255,0.15);backdrop-filter:blur(8px);height:46px;display:flex;align-items:center;overflow:hidden;">
  <a href="https://www.okx.com/join/CREEMOS" target="_blank" rel="noopener noreferrer"
     style="flex-shrink:0;padding:0 0.85rem;border-right:1px solid rgba(0,212,255,0.15);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:0.1rem;text-decoration:none;height:100%;">
    <span style="font-size:0.5rem;letter-spacing:0.12em;text-transform:uppercase;color:#475569;line-height:1;">Powered by</span>
    <img src="./img/OKX-250x141.png" alt="OKX" style="height:18px;width:auto;display:block;">
  </a>
  <div style="flex:1;overflow:hidden;mask-image:linear-gradient(to right,transparent 0,black 3%,black 97%,transparent 100%);">
    <div id="okx-ticker-items" style="display:inline-flex;align-items:center;gap:0;animation:tickerScroll 55s linear infinite;white-space:nowrap;">
      <span style="color:#475569;font-size:0.78rem;padding:0 2rem;">Cargando precios en tiempo real…</span>
    </div>
  </div>
</div>
"""

FOOTER_HTML = """<footer class="px-6 pt-10 pb-6 border-t border-sky-900/20" style="margin-top:2rem;">
  <div class="max-w-7xl mx-auto">
    <div class="flex flex-col md:flex-row justify-between items-start gap-6 mb-8">
      <div>
        <p class="font-display font-bold text-xl text-white mb-1">Creemos <span class="text-sky-400">Capital</span></p>
        <p class="text-slate-600 text-xs">Informe de mercado diario · creemoscapital.com</p>
      </div>
      <p class="text-slate-700 text-xs">© 2026 Creemos Capital. Todos los derechos reservados.</p>
    </div>
    <div class="border-t border-sky-900/20 pt-6">
      <p class="text-slate-600 text-xs leading-relaxed mb-3">
        <strong class="text-slate-500">⚠ Aviso Legal:</strong> El contenido de este informe es exclusivamente con fines educativos e informativos y no debe considerarse como asesoramiento financiero, legal o fiscal. El trading y la inversion en los mercados financieros conllevan un alto nivel de riesgo, incluyendo la posibilidad de perder la totalidad del capital invertido.
      </p>
      <p class="text-slate-500 text-xs font-medium">Al usar este contenido, aceptas que eres el unico responsable de tus decisiones financieras. ¡Opera con responsabilidad!</p>
    </div>
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
    for var, value in BRAND.items():
        html = re.sub(rf"({re.escape(var)}\s*:\s*)[^;]+;", rf"\g<1>{value};", html, count=1)
    return html


def ensure_viewport(html: str) -> str:
    if "name=\"viewport\"" in html or "name='viewport'" in html:
        return html
    return re.sub(r"(<meta charset=[\"'][^\"']+[\"']>\s*\n)", rf"\g<1>{VIEWPORT_TAG}", html, count=1)


def ensure_head_assets(html: str) -> str:
    if "cdn.tailwindcss.com" in html:
        return html
    return html.replace("<style>", HEAD_ASSETS + "<style>", 1)


def replace_embedded_logo(html: str) -> str:
    return re.sub(r'src="data:image/[a-zA-Z+]+;base64,[A-Za-z0-9+/=]+"', f'src="{LOGO_PATH}"', html)


def strip_brand_logo_img(html: str) -> str:
    """Saca el logo duplicado dentro de .brand (ya tenemos el logo real en el navbar)."""
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
        f'<h1>{title}<span class="ic-year"> {year}</span></h1>\n'
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
    html = re.sub(r"(<body[^>]*>\s*)", rf"\g<1>{NAVBAR_HTML}", html, count=1)
    html = re.sub(r"(\s*</body>)", f"{FOOTER_HTML}{CATEGORY_SCRIPT}\\1", html, count=1)
    return html


def adapt(html: str) -> str:
    html = recolor(html)
    html = ensure_viewport(html)
    html = replace_embedded_logo(html)
    html = strip_brand_logo_img(html)
    html = fix_title(html)
    html = ensure_head_assets(html)
    html = inject_css(html)
    html = restructure_panel_cards(html)
    html = group_by_category(html)
    html = inject_navbar_footer(html)
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
