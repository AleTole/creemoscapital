"""
Sube la VISTA PREVIA (para que el equipo la vea y la apruebe) a:

    https://creemoscapital.com/previa-v2-q8x4/

Es lo mismo que hace .github/workflows/vista-previa.yml, pero desde tu PC (sirve cuando
GitHub Actions no esta disponible). NO toca la pagina oficial: solo escribe dentro de esa carpeta.

Uso (PowerShell, desde la carpeta del proyecto):
    python scripts/subir_previa.py            -> prepara y sube (pide la contrasena de FTP; no se guarda)
    python scripts/subir_previa.py --probar   -> solo prepara la copia y lista los archivos, sin conectarse
    python scripts/subir_previa.py --login    -> solo comprueba usuario y contrasena (no sube nada)
    python scripts/subir_previa.py --oficial  -> sube a la PAGINA OFICIAL (https://creemoscapital.com/):
                                                 guarda antes una copia de lo que reemplaza y pide escribir OFICIAL
    python scripts/subir_previa.py --oficial --probar -> muestra que subiria a la oficial, sin conectarse

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
from datetime import datetime
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


def preparar(destino: Path, oficial: bool = False) -> None:
    # 1) datos al dia (noticias, calendario, serie de videos)
    ejecutar(RAIZ / "scripts" / "actualizar_datos.py")

    # 2) copia limpia de src (sin cache ni paquetes). La vista previa tampoco lleva los informes originales;
    #    la pagina oficial si (es el archivo de informes, igual que en el despliegue de siempre).
    excluir = [".cache", "deploy.zip", ".ftp-deploy*"] + ([] if oficial else ["informes"])
    shutil.copytree(SRC, destino, ignore=shutil.ignore_patterns(*excluir))

    # 3) informe mas reciente con el diseno nuevo (valida el formato; si falla, se corta aqui)
    elegido = subprocess.run([sys.executable, str(RAIZ / "scripts" / "elegir_informe.py")], cwd=RAIZ, capture_output=True, text=True)
    if elegido.returncode == 0 and elegido.stdout.strip():
        shutil.copy(RAIZ / elegido.stdout.strip(), destino / "informe.html")
        ejecutar(RAIZ / "scripts" / "recolor_informe.py", destino / "informe.html")

    if oficial:
        return                                  # la pagina oficial NO se oculta a buscadores

    # 4) oculto a buscadores (solo vista previa)
    (destino / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    with open(destino / ".htaccess", "a", encoding="utf-8") as f:
        f.write('\n<IfModule mod_headers.c>\n  Header always set X-Robots-Tag "noindex, nofollow, noarchive"\n</IfModule>\n')
    for html in destino.glob("*.html"):
        t = html.read_text(encoding="utf-8")
        html.write_text(t.replace("<head>", '<head>\n  <meta name="robots" content="noindex, nofollow">', 1), encoding="utf-8")


NOMBRE_CERTIFICADO = "ftp.hstgr.io"      # el certificado de Hostinger es *.hstgr.io, no el numero (IP) del servidor


def conectar_verificado(host: str) -> ftplib.FTP_TLS:
    """Conecta por FTPS verificando el certificado de verdad (cadena de confianza + nombre).
    Se entra por la IP de deploy.py, pero el nombre que se comprueba es el del certificado (*.hstgr.io)."""
    ftp = ftplib.FTP_TLS(context=ssl.create_default_context())
    ftp.connect(host, 21, timeout=30)
    ftp.host = NOMBRE_CERTIFICADO            # ftplib usa este valor como "server_hostname" al cifrar
    ftp.auth()                               # negociacion TLS: aqui se valida el certificado (aun sin enviar usuario ni clave)
    return ftp


def subir_carpeta(ftp: ftplib.FTP, local: Path, remoto: str) -> int:
    n = 0
    if remoto not in (None, "", "."):           # None = la raiz del sitio (donde ya deja el login)
        try:
            ftp.mkd(remoto)
        except ftplib.error_perm:
            pass                                # ya existe
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


def solo_comprobar_acceso():
    """Entra al FTP y lista los nombres de la raiz. No sube, no borra, no modifica nada."""
    host, usuario = leer_constante("FTP_HOST"), leer_constante("FTP_USER")
    print(f"Servidor: {host}\nUsuario:  {usuario}")
    clave = os.environ.get("FTP_PASS") or getpass.getpass("Contrasena de FTP de Hostinger (no se muestra): ")
    ftp = conectar_verificado(host)
    try:
        ftp.login(usuario, clave)
    except ftplib.error_perm as e:
        sys.exit(f"\nEl servidor rechazo el acceso: {e}\n -> revisa usuario y contrasena en hPanel > Archivos > Cuentas FTP.")
    print("\nAcceso CORRECTO. Contenido de la raiz (solo nombres):")
    for nombre in sorted(ftp.nlst()):
        print("  ", nombre)
    ftp.quit()


def respaldar(ftp: ftplib.FTP, archivos, carpeta: Path) -> int:
    """Descarga a tu PC la version ACTUAL de cada archivo que se va a reemplazar (si existe en el servidor).
    Si algo sale mal, ahi esta el sitio tal como estaba."""
    n = 0
    for rel in archivos:
        destino = carpeta / rel
        destino.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(destino, "wb") as f:
                ftp.retrbinary(f"RETR {rel}", f.write)
            n += 1
        except ftplib.error_perm:               # el archivo todavia no existe en el servidor
            destino.unlink(missing_ok=True)
    return n


def main():
    if "--login" in sys.argv:
        return solo_comprobar_acceso()
    solo_probar = "--probar" in sys.argv
    oficial = "--oficial" in sys.argv
    with tempfile.TemporaryDirectory(prefix="previa-cc-") as tmp:
        destino = Path(tmp) / "previa"
        preparar(destino, oficial)
        archivos = sorted(p.relative_to(destino).as_posix() for p in destino.rglob("*") if p.is_file())
        print(f"\nCopia preparada: {len(archivos)} archivos")
        if solo_probar:
            print("\n".join("  " + a for a in archivos))
            print("\n(--probar: no se subio nada)")
            return

        if oficial:
            print("\n" + "=" * 64)
            print(" VAS A SUBIR A LA PAGINA OFICIAL: https://creemoscapital.com/")
            print(f" Se reemplazaran hasta {len(archivos)} archivos. Antes se guarda una copia de lo que hay ahora.")
            print("=" * 64)
            if input(" Escribe OFICIAL y pulsa Enter para continuar (cualquier otra cosa cancela): ").strip() != "OFICIAL":
                sys.exit("Cancelado. No se subio nada.")

        host, usuario = leer_constante("FTP_HOST"), leer_constante("FTP_USER")
        clave = os.environ.get("FTP_PASS") or getpass.getpass("Contrasena de FTP de Hostinger (no se muestra): ")
        print(f"\nConectando a {host} (FTP cifrado)...")
        ftp = conectar_verificado(host)
        ftp.login(usuario, clave)
        ftp.prot_p()
        if oficial:
            carpeta = RAIZ / ("respaldo-sitio-" + datetime.now().strftime("%Y%m%d-%H%M"))
            print(f"Guardando copia de lo que hay ahora en: {carpeta.name} ...")
            print(f"  copia hecha de {respaldar(ftp, archivos, carpeta)} archivos existentes")
            total = subir_carpeta(ftp, destino, None)
            ftp.quit()
            print(f"\nListo: {total} archivos subidos a https://creemoscapital.com/")
            print(f"Si hace falta volver atras: la copia esta en {carpeta}")
            return
        total = subir_carpeta(ftp, destino, CARPETA)
        ftp.quit()
        print(f"\nListo: {total} archivos en {URL}")


if __name__ == "__main__":
    main()
