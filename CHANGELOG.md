# Changelog — Creemos Capital

Todas las versiones del sitio documentadas acá.

---

## [v0.4.0] — 2026-04-06
**Commit:** `2da3a15`

### Sitio publicado en producción
- Deploy exitoso en **creemoscapital.com** via Hostinger
- WordPress anterior eliminado y reemplazado por el sitio estático

### Fixes
- Calendario económico: proxy PHP propio (`calendar-proxy.php`) para evitar bloqueos CORS
- Campo `country` corregido (la API de FF usa `country`, no `currency`)
- Banderas del calendario ahora se mapean correctamente
- Eventos de tipo `Holiday` excluidos del calendario
- Paleta de colores: cyan eléctrico `#00d4ff` + fondos azul moderno
- Botones de YouTube en rojo
- Rejilla del hero eliminada

---

## [v0.3.0] — 2026-04-06
**Commit:** `9c9b37d`

### Agregado
- Player de Kick en vivo en el hero (muestra stream cuando están en vivo)
- Badge "EN VIVO" animado con glow pulsante sobre el player
- Botones de donación bajo el player (Kick y YouTube Super Chat)
- Kick agregado a redes sociales
- Sesiones: banderas como imágenes reales (flagcdn.com) — compatible con Windows
- Sesiones: agrega Venezuela, Ecuador y México con sus horarios
- Sesiones: Chile y USA combinados por coincidir en UTC-4

### Cambiado
- Cuadritos de redes sociales: tamaño uniforme 100×100px
- Sesiones: se muestran solo banderas + horario (sin texto de zona)
- Footer: eliminado "Todas las noches" del tagline
- Calendario: solo muestra eventos desde hoy en adelante

### Eliminado
- Discord de comunidad y contacto

---

## [v0.2.0] — 2026-04-06
**Commit:** `4166c4d`

### Agregado
- Calendario económico en vivo con datos de Forex Factory (API pública)
  - Filtros por impacto: Todos / 🔴 Alto / 🟠 Medio
  - Solo muestra eventos desde el día actual en adelante
  - Fallback automático con proxies CORS si falla la conexión directa
- Mini reproductor de música flotante (esquina inferior derecha)
  - Se colapsa/expande con un click
  - Sigue al usuario durante el scroll
  - Reproduce la playlist del canal de YouTube Music
- Sección de noticias con 6 cards de acceso directo a fuentes en español
  - Investing.com (Forex, Mercados, Crypto, Análisis Técnico)
  - Forex Factory (Noticias y Calendario)
- Sesiones de mercado rediseñadas con horarios por país
  - Colombia / Perú · Chile · Argentina · USA · España
  - 3 sesiones: NY · Asia · Europa
- Logo en navbar y sección hero

### Cambiado
- Sección de música: de YouTube genérico → canal oficial de YouTube Music
- Textos del hero: enfasis en "¡Casi 21 hs al día!" y mención de Estrategia C4
- Email de contacto: `contacto@` → `info@creemoscapital.com`
- Sección comunidad: "escribinos" → "escribenos"

### Eliminado
- Sección de Ideas de Trading
- Botón y card de Discord (reemplazado por Telegram)

---

## [v0.1.0] — 2025 (inicial)
**Commit:** `b06f59d`

### Agregado
- Estructura base del sitio (HTML + Tailwind CSS + Vanilla JS)
- Navbar con scroll y menú mobile
- Hero con llamada a la acción
- Banner de sesiones en vivo (NY, Crypto, Asia, Europa)
- Sección de videos: Trading para Novatos + La Estrategia
- Ideas de Trading con cards de activos
- Sección de comunidad (Discord + Telegram)
- Player de música (YouTube Music)
- Redes sociales y contacto (WhatsApp, Telegram, Email)
- Footer con aviso legal
