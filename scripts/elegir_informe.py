"""
Elige el informe MAS RECIENTE de src/informes/ por su fecha real, no por el nombre del archivo.

Por que: tu companero no siempre nombra igual los archivos ("2026-11-27.html", "24 Nov 2026.html",
"informe_2026-11-09.html"...). Ordenar por nombre (ls | sort | tail) elegia "informe_2026-11-09.html"
como el ultimo, aunque hubiera uno del 27. Aqui la fecha se lee primero del CONTENIDO del informe
("Lunes 2 Nov 2026 · ...") y, si no esta, del nombre del archivo.

Uso:
    python scripts/elegir_informe.py            -> imprime la ruta del informe mas reciente
    python scripts/elegir_informe.py --lista    -> lista todos con la fecha detectada
"""
import re
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CARPETA = RAIZ / "src" / "informes"

MESES = {
    "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6, "jul": 7, "ago": 8,
    "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dic": 12,
    "jan": 1, "apr": 4, "aug": 8, "dec": 12,
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
    "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
}


def _fecha(d, m, a):
    try:
        mes = MESES[m.lower().strip(".")]
        return date(int(a), mes, int(d))
    except (KeyError, ValueError):
        return None


def fecha_del_contenido(texto: str):
    m = re.search(r'class="sub">\s*[A-Za-zÁÉÍÓÚáéíóúñÑ]+\s+(\d{1,2})\s+([A-Za-zÁÉÍÓÚáéíóúñÑ]+)\.?\s+(\d{4})', texto)
    return _fecha(*m.groups()) if m else None


def fecha_del_nombre(nombre: str):
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", nombre)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass
    m = re.search(r"(\d{1,2})\s+([A-Za-zñÑ]{3,10})\.?\s+(\d{4})", nombre)
    return _fecha(*m.groups()) if m else None


def listar():
    filas = []
    for f in sorted(CARPETA.glob("*.html")):
        try:
            texto = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        d_cont, d_nom = fecha_del_contenido(texto), fecha_del_nombre(f.name)
        filas.append((d_cont or d_nom or date.min, f, d_cont, d_nom))
    return filas


def main():
    filas = listar()
    if not filas:
        sys.exit("No hay informes en src/informes/")
    if "--lista" in sys.argv:
        for fecha, f, d_cont, d_nom in sorted(filas, key=lambda x: (x[0], x[1].name)):
            aviso = "" if (d_cont is None or d_nom is None or d_cont == d_nom) else f"   <- el nombre dice {d_nom}"
            print(f"{fecha}  {f.name}{aviso}")
        return
    # el mas reciente por fecha; en empate, el de nombre mas "limpio" (AAAA-MM-DD) y luego orden alfabetico
    mejor = max(filas, key=lambda x: (x[0], bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}\.html", x[1].name)), x[1].name))
    print(mejor[1].relative_to(RAIZ).as_posix())


if __name__ == "__main__":
    main()
