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
// Agregá más videos acá — aparecen automáticamente como miniaturas
const VIDEOS_ESTRATEGIA = [
  { id: "O-s8F1EYgZo",   titulo: "Rompimiento sin volumen es sospechoso" },
  { id: "SyskCkiNby8",   titulo: "Vela Bonita VS Rechazo Real — Acción del precio" },
  { id: "ezvbivW95X4",   titulo: "Sin estructura no hay tendencia" },
  { id: "mCSDxA4bjMA",   titulo: "Si el precio no reacciona antes, no es soporte" },
  { id: "l2HCP4BVG3s",   titulo: "Precio sin Volumen no convence" },
  { id: "7xrAUPnKfFc",   titulo: "Una vela NO es señal — Acción del precio" },
  { id: "OvhAA3B6oYo",   titulo: "Tendencia NO es una línea inclinada" },
  { id: "ySxbg7pZ0b8",   titulo: "No son líneas, son Zonas — Soportes y Resistencias" },
];

// ── SESIONES DE MERCADO ────────────────────────────────────────
// Horarios por zona horaria para cada sesión de mercado
// banderas: códigos ISO 3166-1 alpha-2 en minúsculas (flagcdn.com)
// Zonas horarias (UTC verano): COL/PER/ECU -5 | MEX -6 | VEN/CHL/USA -4 | ARG -3 | GB/IC +1 | ESP +2
const SESIONES = [
  {
    nombre: "Sesión NY",
    icono: "us",
    horarios: [
      { banderas: ["co","pe","ec"],  zona: "COL / PER / ECU",    hora: "08:00 – 16:00" },
      { banderas: ["ve","cl","us"],  zona: "VEN / Chile / USA",   hora: "09:00 – 17:00" },
      { banderas: ["mx"],            zona: "México (CDT)",        hora: "07:00 – 15:00" },
      { banderas: ["ar"],            zona: "Argentina",           hora: "10:00 – 18:00" },
      { banderas: ["gb"],            zona: "UK (BST)",            hora: "14:00 – 22:00" },
      { banderas: ["es"],            zona: "España (CEST)",       hora: "15:00 – 23:00" },
    ],
  },
  {
    nombre: "Sesión Asia",
    icono: "jp",
    horarios: [
      { banderas: ["co","pe","ec"],  zona: "COL / PER / ECU",    hora: "19:00 – 01:00" },
      { banderas: ["ve","cl","us"],  zona: "VEN / Chile / USA",   hora: "20:00 – 02:00" },
      { banderas: ["mx"],            zona: "México (CDT)",        hora: "18:00 – 00:00" },
      { banderas: ["ar"],            zona: "Argentina",           hora: "21:00 – 03:00" },
      { banderas: ["gb"],            zona: "UK (BST)",            hora: "01:00 – 07:00" },
      { banderas: ["es"],            zona: "España (CEST)",       hora: "02:00 – 08:00" },
    ],
  },
  {
    nombre: "Sesión Europa",
    icono: "eu",
    horarios: [
      { banderas: ["co","pe","ec"],  zona: "COL / PER / ECU",    hora: "01:00 – 07:00" },
      { banderas: ["ve","cl","us"],  zona: "VEN / Chile / USA",   hora: "02:00 – 08:00" },
      { banderas: ["mx"],            zona: "México (CDT)",        hora: "00:00 – 06:00" },
      { banderas: ["ar"],            zona: "Argentina",           hora: "03:00 – 09:00" },
      { banderas: ["gb"],            zona: "UK (BST)",            hora: "07:00 – 13:00" },
      { banderas: ["es"],            zona: "España (CEST)",       hora: "08:00 – 14:00" },
    ],
  },
];

// ── MÚSICA ─────────────────────────────────────────────────────
// Canal de YouTube Music — UCv4ma-yTMOqYYF_Ii5kv0zQ
// La playlist de uploads es el channel ID con UC → UU
const MUSICA_PLAYLIST_ID     = "UUv4ma-yTMOqYYF_Ii5kv0zQ";
const MUSICA_PRIMER_VIDEO_ID = "videoseries";

