// =================================================================
//  CREEMOS CAPITAL — Datos del sitio
//  Editá este archivo para actualizar contenido sin tocar el HTML
// =================================================================

// ── VIDEOS PARA EMPEZAR (Trading para novatos) ─────────────────
// Reemplazá el "id" con el ID del video de YouTube
// Lo encontrás en la URL: youtube.com/watch?v=ESTE_ES_EL_ID
const VIDEOS_NOVATOS = [
  {
    id: "VcX1bL4lyk0",
    titulo: "Trading para Novatos — Sesión 1",
    duracion: "",
  },
  {
    id: "k2MSeeZbEaQ",
    titulo: "Trading para Novatos — Sesión 2",
    duracion: "",
  },
  {
    id: "6ZimHCukVzI",
    titulo: "Trading para Novatos — Sesión 3",
    duracion: "",
  },
];

// ── VIDEOS DE ESTRATEGIA ───────────────────────────────────────
const VIDEOS_ESTRATEGIA = [
  { id: "ySxbg7pZ0b8", titulo: "No son líneas, son Zonas — Soportes y Resistencias · Estrategia C4" },
  { id: "O-s8F1EYgZo", titulo: "Rompimiento sin volumen es sospechoso" },
  { id: "OvhAA3B6oYo", titulo: "Tendencia NO es una línea inclinada — Tendencia · Estrategia C4" },
  // Completar con los videos restantes de la playlist
  // { id: "VIDEO_ID", titulo: "Título del video" },
];

// ── IDEAS DE TRADING ───────────────────────────────────────────
// direction: "LONG" | "SHORT"
// status: "activa" | "objetivo" | "stop"
const IDEAS_TRADING = [
  {
    activo: "BTC/USDT",
    direccion: "LONG",
    entrada: "62,500",
    objetivo: "68,000",
    stop: "60,800",
    descripcion: "Ruptura de resistencia con volumen. Confluencia con media de 200 períodos.",
    fecha: "2025-03-27",
    status: "activa",
  },
  {
    activo: "EUR/USD",
    direccion: "SHORT",
    entrada: "1.0820",
    objetivo: "1.0720",
    stop: "1.0870",
    descripcion: "Rechazo en zona de oferta semanal. DXY mostrando fortaleza.",
    fecha: "2025-03-26",
    status: "activa",
  },
  {
    activo: "GBP/JPY",
    direccion: "LONG",
    entrada: "191.50",
    objetivo: "194.00",
    stop: "190.20",
    descripcion: "Tendencia alcista en H4. Retroceso a zona de demanda confirmada.",
    fecha: "2025-03-25",
    status: "objetivo",
  },
];

// ── SESIONES EN VIVO ───────────────────────────────────────────
const SESIONES = [
  { nombre: "Sesión NY",     horario: "21:00", emoji: "🇺🇸" },
  { nombre: "Sesión Crypto", horario: "22:00", emoji: "₿"  },
  { nombre: "Sesión Asia",   horario: "23:30", emoji: "🌏" },
  { nombre: "Sesión Europa", horario: "01:00", emoji: "🇪🇺" },
];

// ── MÚSICA ─────────────────────────────────────────────────────
// Playlist de YouTube Music — se muestra como player en la sección Música
const MUSICA_PLAYLIST_ID      = "PLsRZxCss4fXYvz8JclFZb_bKlJxXZGZ9j";
const MUSICA_PRIMER_VIDEO_ID  = "6ZimHCukVzI";

// ── ESTRATEGIA — playlist completa ─────────────────────────────
const ESTRATEGIA_PLAYLIST_ID     = "PLsRZxCss4fXaLnBIAu3kFtt33hve3gz06";
const ESTRATEGIA_PRIMER_VIDEO_ID = "O-s8F1EYgZo";
