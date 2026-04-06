# Changelog — Creemos Capital

Todas las versiones del sitio documentadas acá.

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
