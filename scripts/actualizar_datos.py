"""
Actualiza los datos dinamicos de creemoscapital.com (solo libreria estandar):

  src/data/serie-bitget.json  Videos "Dia N de 33 operando con Bitget" del canal de
                              YouTube. ACUMULA: el RSS del canal solo guarda los
                              ultimos 15 videos, asi que cada dia nuevo se agrega y
                              los anteriores nunca se borran. Se versiona en git.
  src/data/noticias.json      Noticias del dia (mercados, cripto y anuncios de los
                              exchanges). Se regenera cada vez y NO se versiona.

Lo ejecuta .github/workflows/datos.yml cada 30 minutos. Cada fuente va aislada:
si una falla, se conserva lo que ya habia y las demas siguen funcionando.

Uso:  python scripts/actualizar_datos.py
"""
import html
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
# En el VPS (publicar_datos.py) la carpeta de trabajo se indica con CC_DATOS_DIR; por defecto es src/data del proyecto.
DATOS = Path(os.environ["CC_DATOS_DIR"]) if os.environ.get("CC_DATOS_DIR") else RAIZ / "src" / "data"
UA = {"User-Agent": "Mozilla/5.0 (compatible; CreemosCapitalBot/1.0)", "Accept-Language": "es-ES,es;q=0.9,en;q=0.5"}

CANAL_ID = "UCnRW1Op2WPvanUHkv5fW40Q"          # @CreemosCapital
CANAL_SHORTS = "https://www.youtube.com/@CreemosCapital/shorts"
CANAL_RSS = f"https://www.youtube.com/feeds/videos.xml?channel_id={CANAL_ID}"

# Dias que ya estaban publicados al crear esto (el RSS ya no los trae). Se completan solos.
SEMILLA = {
    1: "-jypxfjhmtI",
    2: "DrCWflxLtVw",
    3: "eUyW-tPVgWo",
    4: "RdmS3uJhiwI",
    5: "ZhZsIP1njng",
    6: "2hzNyUGeMxY",
}

# Fuentes de noticias: (categoria, nombre que se muestra, url del RSS, autores permitidos o None)
# En las noticias de Investing solo se aceptan las propias de la redaccion: el resto son notas de
# prensa pagadas (p. ej. "Emprendedores de Hoy", "Chainwire").
SOLO_INVESTING = {"Investing.com"}
FUENTES_RSS = [
    ("mercados", "Investing.com", "https://es.investing.com/rss/news_1.rss", SOLO_INVESTING),
    ("mercados", "Investing.com", "https://es.investing.com/rss/news_25.rss", SOLO_INVESTING),
    ("mercados", "Investing.com", "https://es.investing.com/rss/market_overview.rss", None),
    ("cripto", "Investing.com", "https://es.investing.com/rss/news_301.rss", SOLO_INVESTING),
    ("cripto", "CriptoNoticias", "https://www.criptonoticias.com/feed/", None),
    ("cripto", "Diario Bitcoin", "https://www.diariobitcoin.com/index.php/feed", None),
    ("cripto", "BeInCrypto", "https://es.beincrypto.com/feed/", None),
]

# Ruido que no queremos mostrar: publicidad, apuestas, contenido pagado o solo para registrados.
CATEGORIAS_BLOQUEADAS = {
    "casinos", "casino", "apuestas", "artículos patrocinados", "articulos patrocinados", "patrocinado",
    "publicidad", "solo para usuarios registrados", "comunicado de prensa", "press release",
}
TITULOS_BLOQUEADOS = re.compile(
    r"casino|apuestas|tragaperras|slots?\b|p[oó]ker|bono de|bonos de|c[oó]digo promocional|sin dep[oó]sito",
    re.I,
)
MAX_POR_CATEGORIA = 12
VENTANA_HORAS = 48


def descargar(url: str, extra_headers=None, timeout=25) -> str:
    req = urllib.request.Request(url, headers={**UA, **(extra_headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def leer_json(ruta: Path, defecto):
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return defecto


def escribir_json(ruta: Path, datos) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def xml_seguro(texto: str):
    """Parsea XML de terceros rechazando DTD/entidades (evita expansion de entidades)."""
    if "<!DOCTYPE" in texto or "<!ENTITY" in texto:
        raise ValueError("XML con DTD rechazado")
    return ET.fromstring(texto)


def limpiar(texto: str) -> str:
    texto = re.sub(r"<[^>]+>", " ", html.unescape(texto or ""))
    return re.sub(r"\s+", " ", texto).strip()


def parsear_fecha(valor: str):
    valor = (valor or "").strip()
    if not valor:
        return None
    try:
        d = parsedate_to_datetime(valor)
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return d.astimezone(timezone.utc)
    except (TypeError, ValueError):
        pass
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z"):
        try:
            d = datetime.strptime(valor, fmt)
            if d.tzinfo is None:
                d = d.replace(tzinfo=timezone.utc)      # Investing publica en UTC
            return d.astimezone(timezone.utc)
        except ValueError:
            continue
    return None


def enlace_valido(url: str) -> bool:
    return isinstance(url, str) and url.startswith(("https://", "http://"))


# ──────────────────────────────────────────────────────────────
#  Serie "Dia N de 33 operando con Bitget"
# ──────────────────────────────────────────────────────────────
PATRON_DIA = re.compile(r"d[ií]a\s*(\d{1,2})\s*de\s*(\d{1,3})", re.I)


def detectar_dia(titulo: str):
    """Devuelve (dia, total) si el titulo es de la serie con Bitget, o None."""
    if "bitget" not in titulo.lower():
        return None
    m = PATRON_DIA.search(titulo)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


def videos_desde_rss():
    xml = descargar(CANAL_RSS)
    raiz = xml_seguro(xml)
    ns = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}
    encontrados = []
    for e in raiz.findall("a:entry", ns):
        vid = e.findtext("yt:videoId", default="", namespaces=ns)
        titulo = limpiar(e.findtext("a:title", default="", namespaces=ns))
        fecha = e.findtext("a:published", default="", namespaces=ns)
        encontrados.append((vid, titulo, fecha[:10] if fecha else None))
    return encontrados


def videos_desde_pagina_shorts():
    """La pagina de Shorts trae mas que el RSS (los ultimos ~30). Es mejor esfuerzo:
    si YouTube cambia el formato, simplemente no aporta nada."""
    h = descargar(CANAL_SHORTS)
    encontrados = []
    for m in re.finditer(r'"videoId":"([\w-]{11})"', h):
        ctx = h[m.start(): m.start() + 1500]
        t = re.search(r'"(?:text|accessibilityText|content)":"([^"]*?de\s*\d+[^"]*?)"', ctx, re.I)
        if t:
            try:
                titulo = json.loads('"' + t.group(1) + '"')     # el texto viene como cadena JSON (con \uXXXX)
            except ValueError:
                titulo = t.group(1)
            encontrados.append((m.group(1), limpiar(titulo), None))
    return encontrados


def actualizar_serie():
    ruta = DATOS / "serie-bitget.json"
    previo = leer_json(ruta, {})
    dias = {int(v["dia"]): v for v in previo.get("videos", []) if "dia" in v and "id" in v}
    total = int(previo.get("total", 33))

    for dia, vid in SEMILLA.items():
        dias.setdefault(dia, {"dia": dia, "id": vid, "titulo": f"Día {dia} de {total} operando con Bitget", "fecha": None})

    nuevos = 0
    for nombre, fuente in (("RSS", videos_desde_rss), ("página de Shorts", videos_desde_pagina_shorts)):
        try:
            for vid, titulo, fecha in fuente():
                det = detectar_dia(titulo)
                if not det or not re.fullmatch(r"[\w-]{11}", vid or ""):
                    continue
                dia, tot = det
                total = max(total, tot)
                if dia in dias:
                    if not dias[dia].get("fecha") and fecha:
                        dias[dia]["fecha"] = fecha
                    continue
                dias[dia] = {"dia": dia, "id": vid, "titulo": f"Día {dia} de {tot} operando con Bitget", "fecha": fecha}
                nuevos += 1
        except Exception as exc:
            print(f"  aviso: {nombre} no disponible ({exc})")

    resultado = {
        "total": total,
        "canal": "https://www.youtube.com/@CreemosCapital",
        "videos": [dias[d] for d in sorted(dias)],
    }
    if resultado != previo:
        escribir_json(ruta, resultado)
    print(f"Serie Bitget: {len(dias)} días cargados de {total} ({nuevos} nuevos)")


# ──────────────────────────────────────────────────────────────
#  Noticias
# ──────────────────────────────────────────────────────────────
def items_rss(categoria: str, fuente: str, url: str, autores_ok=None):
    raiz = xml_seguro(descargar(url))
    items = []
    for it in raiz.iter("item"):
        titulo = limpiar(it.findtext("title"))
        enlace = (it.findtext("link") or "").strip()
        fecha = parsear_fecha(it.findtext("pubDate") or it.findtext("{http://purl.org/dc/elements/1.1/}date") or "")
        autor = limpiar(it.findtext("author") or "")
        cats = {limpiar(c.text or "").lower() for c in it.findall("category")}
        if autores_ok is not None and autor not in autores_ok:
            continue
        if cats & CATEGORIAS_BLOQUEADAS or TITULOS_BLOQUEADOS.search(titulo):
            continue
        if titulo and enlace_valido(enlace) and fecha:
            items.append({"titulo": titulo, "enlace": enlace, "fuente": fuente, "cat": categoria, "fecha": fecha})
    return items


def anuncios_bitget():
    datos = json.loads(descargar("https://api.bitget.com/api/v2/public/annoucements?language=es_ES"))
    items = []
    for a in datos.get("data", []):
        try:
            fecha = datetime.fromtimestamp(int(a["cTime"]) / 1000, tz=timezone.utc)
        except (KeyError, ValueError):
            continue
        if enlace_valido(a.get("annUrl")) and a.get("annTitle"):
            items.append({"titulo": limpiar(a["annTitle"]), "enlace": a["annUrl"], "fuente": "Bitget", "cat": "exchanges", "fecha": fecha})
    return items


def anuncios_okx():
    datos = json.loads(descargar("https://www.okx.com/api/v5/support/announcements?page=1"))
    items = []
    for bloque in datos.get("data", []):
        for a in bloque.get("details", []):
            try:
                fecha = datetime.fromtimestamp(int(a["pTime"]) / 1000, tz=timezone.utc)
            except (KeyError, ValueError):
                continue
            if enlace_valido(a.get("url")) and a.get("title"):
                items.append({"titulo": limpiar(a["title"]), "enlace": a["url"], "fuente": "OKX", "cat": "exchanges", "fecha": fecha})
    return items


def actualizar_noticias():
    ruta = DATOS / "noticias.json"
    previo = leer_json(ruta, {})
    ahora = datetime.now(timezone.utc)
    todas = []

    trabajos = [(f"{c}/{f}", lambda c=c, f=f, u=u, a=a: items_rss(c, f, u, a)) for c, f, u, a in FUENTES_RSS]
    trabajos += [("Bitget", anuncios_bitget), ("OKX", anuncios_okx)]
    for nombre, fn in trabajos:
        try:
            todas += fn()
        except Exception as exc:
            print(f"  aviso: {nombre} no disponible ({exc})")

    salida = {"generado": ahora.isoformat(timespec="seconds"), "mercados": [], "cripto": [], "exchanges": []}
    for cat in ("mercados", "cripto", "exchanges"):
        grupo = [i for i in todas if i["cat"] == cat]
        vistos, unicos = set(), []
        for i in sorted(grupo, key=lambda x: x["fecha"], reverse=True):
            clave = re.sub(r"\W+", "", i["titulo"].lower())[:80]
            if clave in vistos:
                continue
            vistos.add(clave)
            unicos.append(i)
        recientes = [i for i in unicos if ahora - i["fecha"] <= timedelta(hours=VENTANA_HORAS)]
        elegidos = (recientes if len(recientes) >= 4 else unicos)[:MAX_POR_CATEGORIA]
        if not elegidos and previo.get(cat):
            salida[cat] = previo[cat]          # todas las fuentes fallaron: conservar lo anterior
            continue
        salida[cat] = [
            {"titulo": i["titulo"], "enlace": i["enlace"], "fuente": i["fuente"],
             "fecha": i["fecha"].isoformat(timespec="seconds")}
            for i in elegidos
        ]
    escribir_json(ruta, salida)
    print("Noticias:", {c: len(salida[c]) for c in ("mercados", "cripto", "exchanges")})


# ──────────────────────────────────────────────────────────────
#  Calendario economico (Forex Factory, semana actual)
# ──────────────────────────────────────────────────────────────
CALENDARIO_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json?timezone=America%2FBogota"


def actualizar_calendario():
    """Guarda el calendario como archivo propio del sitio: asi el navegador no depende de CORS ni de PHP.
    Si la fuente falla se deja el archivo anterior tal cual."""
    datos = json.loads(descargar(CALENDARIO_URL))
    if not isinstance(datos, list) or not datos:
        raise ValueError("el calendario llego vacio o con otro formato")
    eventos = [
        {k: str(e.get(k, "")) for k in ("title", "country", "date", "impact", "forecast", "previous", "actual")}
        for e in datos if isinstance(e, dict) and e.get("date")
    ]
    escribir_json(DATOS / "calendario.json", eventos)
    print(f"Calendario: {len(eventos)} eventos")


def main():
    for nombre, fn in (("serie", actualizar_serie), ("noticias", actualizar_noticias), ("calendario", actualizar_calendario)):
        try:
            fn()
        except Exception as exc:                  # nunca romper el workflow por una sola parte
            print(f"ERROR en {nombre}: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
