"""
Pone ?v=<huella> a los enlaces ./js/*.js y ./css/*.css de las paginas HTML del sitio.

Por que: el hosting le dice al navegador que guarde los JS y CSS 7 dias. Sin esto, quien ya conocia el sitio
seguia usando un main.js VIEJO con la pagina NUEVA (por ejemplo, el boton de modo claro dejaba de funcionar).
Con la huella, cada vez que un archivo cambia su enlace cambia, y el navegador baja el correcto.

Uso:  python scripts/versionar.py             (src/ del proyecto)
      python scripts/versionar.py <carpeta>   (otra carpeta con css/ y js/)
`subir_previa.py` lo aplica solo a la copia que sube; ejecutalo tambien antes de guardar cambios de JS/CSS en git.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recolor_informe import versionar_assets  # noqa: E402


def versionar_carpeta(src: Path) -> int:
    cambiadas = 0
    for html in sorted(src.glob("*.html")):
        original = html.read_text(encoding="utf-8")
        nuevo = versionar_assets(original, src)
        if nuevo != original:
            html.write_text(nuevo, encoding="utf-8")
            cambiadas += 1
            print(f"  versionado: {html.name}")
    return cambiadas


if __name__ == "__main__":
    carpeta = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "src"
    n = versionar_carpeta(carpeta)
    print(f"{n} pagina(s) actualizada(s) en {carpeta}")
