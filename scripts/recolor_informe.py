"""
Reescribe la paleta de colores del informe diario (variables CSS :root)
a la identidad visual de Creemos Capital, sin importar que valores
traiga el archivo original.

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

FONT_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">\n'
)


def recolor(html: str) -> str:
    for var, value in BRAND.items():
        # --bg:#0d0f12;  o  --bg: #0d0f12 ;  (con o sin espacios)
        html = re.sub(
            rf"({re.escape(var)}\s*:\s*)[^;]+;",
            rf"\g<1>{value};",
            html,
            count=1,
        )

    # Tipografia: preferir Inter (igual que el resto del sitio)
    html = html.replace("'Segoe UI'", "'Inter','Segoe UI'", 1)

    if "fonts.googleapis.com" not in html:
        html = html.replace("<style>", FONT_LINK + "<style>", 1)

    return html


def main():
    if len(sys.argv) != 2:
        print("Uso: python recolor_informe.py <archivo.html>")
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    html = recolor(html)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Recoloreado: {path}")


if __name__ == "__main__":
    main()
