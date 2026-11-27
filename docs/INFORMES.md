# Informe diario: cómo se publica y cómo se protege el formato

## Flujo
1. Tu compañero sube el informe del día a `src/informes/AAAA-MM-DD.html` (el HTML que ya genera).
2. El workflow **Publicar Informe Diario** (`.github/workflows/informe.yml`) toma el más reciente, lo copia a `src/informe.html` y lo pasa por `scripts/recolor_informe.py`.
3. Ese script **descarta el aspecto del informe original** y lo viste con el diseño del sitio (barra, ticker de Bitget, claro/oscuro, menú lateral por categorías, pie legal). El compañero solo aporta el contenido.
4. Antes de subirlo por FTP, el script **valida** el resultado. Si algo no cuadra, el paso falla y **no se publica nada**: sigue online el último informe bueno.

## Qué debe mantener el informe original (el contenido)
El script reconoce estas piezas del HTML de origen. Mientras se mantengan, el diseño nunca se rompe aunque cambie el aspecto del original:

- Una cabecera `<h1>` seguida de `<div class="sub">` con la fecha (`Lunes 2 Nov 2026 · resumen…`).
- Categorías: `<div class="cat-label">Metales</div>` + `<div class="tabs">` con `<div class="tab-btn" data-tab="xau">XAU</div>`.
- Un panel por activo: `<div class="panel" id="xau">` con sus tarjetas `<div class="card">…`.
- El bloque `<div class="allpanels">` y el pie `<div class="foot">`.

Los nombres largos de los activos (Oro, Bitcoin…) salen de `ASSET_NAMES` en `scripts/recolor_informe.py`. Un activo nuevo se muestra con su código hasta que se agregue ahí.

## Si el formato cambia demasiado
- El workflow falla con un mensaje claro (`Informe NO publicado: …`) y GitHub avisa por correo.
- El sitio no cambia. Se corrige el script (o se le pide al compañero volver al formato) y se vuelve a ejecutar el workflow.

## Prueba rápida en local
```powershell
Copy-Item src/informes/2026-11-02.html src/informe.html
python scripts/recolor_informe.py src/informe.html
```
