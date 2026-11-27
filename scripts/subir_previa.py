"""
Sube la VISTA PREVIA (para que el equipo la vea y la apruebe) a:

    https://creemoscapital.com/previa-v2-q8x4/

Es lo mismo que hace .github/workflows/vista-previa.yml, pero desde tu PC (sirve cuando
GitHub Actions no esta disponible). NO toca la pagina oficial: solo escribe dentro de esa carpeta.

Uso (PowerShell, desde la carpeta del proyecto):
    python scripts/subir_previa.py            -> prepara y sube (pide la contrasena de FTP; no se guarda)
    python scripts/subir_previa.py --probar   -> solo prepara la copia y lista los archivos, sin conectarse

Servidor y usuario se leen de deploy.py (ya los tienes ahi). La contrasena: variable FTP_PASS o se pide al ejecutar.
"""
import ftplib
import getpass
import os
import re
import shutil
import ssl
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SRC = RAIZ / "src"
CARPETA = "previa-v2-q8x4"
URL = f"https://creemoscapital.com/{CARPETA}/"


def leer_constante(nombre: str) -> str:
    """Lee FTP_HOST / FTP_USER de deploy.py sin importarlo (importarlo pediria la contrasena)."""
    texto = (RAIZ / "deploy.py").read_text(encoding="utf-8")
    m = re.search(rf'^{nombre}\s*=\s*["\']([^"\']+)["\']', texto, re.M)
    if not m:
        sys.exit(f"No encontre {nombre} en deploy.py")
    return m.group(1)


def ejecutar(*args):
    r = subprocess.run([sys.executable, *map(str, args)], cwd=RAIZ)
    if r.returncode != 0:
        sys.exit(f"Fallo: {' '.join(map(str, args))}")


def preparar(destino: Path) -> None:
    # 1) datos al dia (noticias, calendario, serie de videos)
    ejecutar(RAIZ / "scripts" / "actualizar_datos.py")

    # 2) copia limpia de src (sin cache, sin paquetes, sin informes originales)
    shutil.copytree(
        SRC, destino,
        ignore=shutil.ignore_patterns(".cache", "deploy.zip", "informes", ".ftp-deploy*"),
    )

    # 3) informe mas reciente con el diseno nuevo (valida el formato; si falla, se corta aqui)
    informes = sorted((SRC / "informes").glob("*.html"))
    if informes:
        shutil.copy(informes[-1], destino / "informe.html")
        ejecutar(RAIZ / "scripts" / "recolor_informe.py", destino / "informe.html")

    # 4) oculto a buscadores
    (destino / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    with open(destino / ".htaccess", "a", encoding="utf-8") as f:
        f.write('\n<IfModule mod_headers.c>\n  Header always set X-Robots-Tag "noindex, nofollow, noarchive"\n</IfModule>\n')
    for html in destino.glob("*.html"):
        t = html.read_text(encoding="utf-8")
        html.write_text(t.replace("<head>", '<head>\n  <meta name="robots" content="noindex, nofollow">', 1), encoding="utf-8")


def subir_carpeta(ftp: ftplib.FTP, local: Path, remoto: str) -> int:
    n = 0
    try:
        ftp.mkd(remoto)
    except ftplib.error_perm:
        pass                                    # ya existe
    ftp.cwd(remoto)
    for entrada in sorted(local.iterdir()):
        if entrada.is_dir():
            n += subir_carpeta(ftp, entrada, entrada.name)
            ftp.cwd("..")
        else:
            with open(entrada, "rb") as f:
                ftp.storbinary(f"STOR {entrada.name}", f)
            n += 1
            print(f"  subido: {entrada.name}")
    return n


def main():
    solo_probar = "--probar" in sys.argv
    with tempfile.TemporaryDirectory(prefix="previa-cc-") as tmp:
        destino = Path(tmp) / "previa"
        preparar(destino)
        archivos = sorted(p.relative_to(destino).as_posix() for p in destino.rglob("*") if p.is_file())
        print(f"\nCopia preparada: {len(archivos)} archivos")
        if solo_probar:
            print("\n".join("  " + a for a in archivos))
            print("\n(--probar: no se subio nada)")
            return

        host, usuario = leer_constante("FTP_HOST"), leer_constante("FTP_USER")
        clave = os.environ.get("FTP_PASS") or getpass.getpass("Contrasena de FTP de Hostinger (no se muestra): ")
        print(f"\nConectando a {host} (FTP cifrado)...")
        ftp = ftplib.FTP_TLS(context=ssl.create_default_context())
        ftp.connect(host, 21, timeout=30)
        ftp.login(usuario, clave)
        ftp.prot_p()
        total = subir_carpeta(ftp, destino, CARPETA)
        ftp.quit()
        print(f"\nListo: {total} archivos en {URL}")


if __name__ == "__main__":
    main()
