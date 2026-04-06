// =================================================================
//  CREEMOS CAPITAL — Lógica del sitio
// =================================================================

// ── NAVBAR scroll ─────────────────────────────────────────────
window.addEventListener('scroll', () => {
  document.getElementById('navbar').classList.toggle('scrolled', window.scrollY > 60);
});
if (window.scrollY > 60) document.getElementById('navbar').classList.add('scrolled');

// ── MENÚ MOBILE ───────────────────────────────────────────────
function toggleMenu() {
  document.getElementById('mobile-menu').classList.toggle('hidden');
}
function closeMenu() {
  document.getElementById('mobile-menu').classList.add('hidden');
}

// ── SESIONES ──────────────────────────────────────────────────
function flagImg(code) {
  return `<img src="https://flagcdn.com/20x15/${code}.png" width="20" height="15" alt="${code}" style="border-radius:2px;display:inline-block;">`;
}

function renderSesiones() {
  const cont = document.getElementById('sesiones-grid');
  if (!cont) return;
  cont.innerHTML = SESIONES.map(s => `
    <div class="sesion-card">
      <div class="sesion-header">
        ${flagImg(s.icono)}
        <span class="sesion-nombre">${s.nombre}</span>
      </div>
      <div class="sesion-horarios">
        ${s.horarios.map(h => `
          <div class="sesion-tz">
            <span class="sesion-tz-flags">${h.banderas.map(flagImg).join('')}</span>
            <span class="sesion-tz-hora">${h.hora}</span>
          </div>
        `).join('')}
      </div>
    </div>
  `).join('');
}

// ── VIDEOS ────────────────────────────────────────────────────
function videoCard(v) {
  const thumb = `https://img.youtube.com/vi/${v.id}/hqdefault.jpg`;
  return `
    <a href="https://www.youtube.com/watch?v=${v.id}" target="_blank" rel="noopener" class="video-card">
      <div class="video-thumb">
        <img src="${thumb}" alt="${v.titulo}" loading="lazy">
        <div class="video-play">
          <svg viewBox="0 0 24 24" fill="white"><path d="M8 5v14l11-7z"/></svg>
        </div>
        <span class="video-duracion">${v.duracion}</span>
      </div>
      <p class="video-titulo">${v.titulo}</p>
    </a>
  `;
}

function renderVideos() {
  const novatos = document.getElementById('grid-novatos');
  const estrategia = document.getElementById('grid-estrategia');
  if (novatos) novatos.innerHTML = VIDEOS_NOVATOS.map(videoCard).join('');
  if (estrategia) estrategia.innerHTML = VIDEOS_ESTRATEGIA.map(videoCard).join('');
}

// ── CALENDARIO FOREX FACTORY ──────────────────────────────────
const PAISES = {
  USD: { nombre: 'EE.UU.',      bandera: '🇺🇸' },
  EUR: { nombre: 'Eurozona',    bandera: '🇪🇺' },
  GBP: { nombre: 'Reino Unido', bandera: '🇬🇧' },
  JPY: { nombre: 'Japón',       bandera: '🇯🇵' },
  CAD: { nombre: 'Canadá',      bandera: '🇨🇦' },
  AUD: { nombre: 'Australia',   bandera: '🇦🇺' },
  NZD: { nombre: 'N. Zelanda',  bandera: '🇳🇿' },
  CHF: { nombre: 'Suiza',       bandera: '🇨🇭' },
  CNY: { nombre: 'China',       bandera: '🇨🇳' },
  SEK: { nombre: 'Suecia',      bandera: '🇸🇪' },
  NOK: { nombre: 'Noruega',     bandera: '🇳🇴' },
  MXN: { nombre: 'México',      bandera: '🇲🇽' },
  BRL: { nombre: 'Brasil',      bandera: '🇧🇷' },
  ALL: { nombre: 'Global',      bandera: '🌐'  },
};

const DIAS_ES = ['Dom','Lun','Mar','Mié','Jue','Vie','Sáb'];
const MESES_ES = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];

let _calEventos = [];
let _calFiltro  = 'todos';

function formatoHora(fechaStr) {
  const d = new Date(fechaStr);
  if (isNaN(d)) return '—';
  return d.toLocaleTimeString('es', { hour: '2-digit', minute: '2-digit' });
}

function formatoDia(fechaStr) {
  const d = new Date(fechaStr);
  return `${DIAS_ES[d.getDay()]} ${d.getDate()} ${MESES_ES[d.getMonth()]}`;
}

function claseActual(actual, forecast, impact) {
  if (!actual || actual === '') return 'pendiente';
  const a = parseFloat(actual.replace(/[^0-9.\-]/g, ''));
  const f = parseFloat((forecast || '').replace(/[^0-9.\-]/g, ''));
  if (isNaN(a) || isNaN(f)) return 'igual';
  if (impact === 'High') return a > f ? 'mejor' : a < f ? 'peor' : 'igual';
  return a < f ? 'mejor' : a > f ? 'peor' : 'igual';
}

function renderCalendario() {
  const cont = document.getElementById('ff-calendar');
  if (!cont) return;

  const filtrados = _calEventos.filter(e => {
    if (_calFiltro === 'alto')  return e.impact === 'High';
    if (_calFiltro === 'medio') return e.impact === 'Medium';
    return e.impact === 'High' || e.impact === 'Medium';
  });

  if (filtrados.length === 0) {
    cont.innerHTML = '<p class="text-center text-slate-600 text-sm py-10">Sin eventos para mostrar.</p>';
    return;
  }

  // Agrupar por día
  const porDia = {};
  filtrados.forEach(e => {
    const dia = formatoDia(e.date);
    if (!porDia[dia]) porDia[dia] = [];
    porDia[dia].push(e);
  });

  cont.innerHTML = Object.entries(porDia).map(([dia, eventos]) => `
    <div class="cal-day-header">${dia}</div>
    ${eventos.map(e => {
      const code   = (e.currency || e.country || '').toUpperCase().trim();
      const pais   = PAISES[code] || { nombre: code || '—', bandera: '🌐' };
      const imp    = e.impact === 'High' ? 'alto' : e.impact === 'Medium' ? 'medio' : 'bajo';
      const actual = e.actual || '';
      const cls    = actual ? claseActual(actual, e.forecast, e.impact) : 'pendiente';
      return `
      <div class="cal-row">
        <span class="cal-time">${formatoHora(e.date)}</span>
        <span class="cal-pais" title="${pais.nombre}"><span class="cal-impacto"><span class="imp-${imp}"></span></span>${pais.bandera}</span>
        <span class="cal-evento">${e.title}</span>
        <span class="cal-num cal-forecast">${e.forecast || '—'}</span>
        <span class="cal-num cal-prev">${e.previous || '—'}</span>
        <span class="cal-num cal-actual ${cls}">${actual || '·'}</span>
      </div>`;
    }).join('')}
  `).join('');
}

function filtrarCalendario(filtro) {
  _calFiltro = filtro;
  document.querySelectorAll('.cal-btn').forEach(b => b.classList.remove('cal-btn-active'));
  document.getElementById(`btn-${filtro}`).classList.add('cal-btn-active');
  renderCalendario();
}

async function cargarCalendario() {
  const loading = document.getElementById('ff-calendar-loading');
  const FF_URL  = 'https://nfs.faireconomy.media/ff_calendar_thisweek.json?timezone=America%2FBogota';
  const PROXIES = [
    FF_URL,
    `https://corsproxy.io/?url=${encodeURIComponent(FF_URL)}`,
    `https://api.allorigins.win/raw?url=${encodeURIComponent(FF_URL)}`,
  ];
  for (const url of PROXIES) {
    try {
      const res  = await fetch(url);
      const data = await res.json();
      if (!Array.isArray(data)) continue;
      const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);
    _calEventos = data.filter(e => {
      const fecha = new Date(e.date);
      return fecha >= hoy && (e.impact === 'High' || e.impact === 'Medium' || e.impact === 'Low');
    });
      if (loading) loading.style.display = 'none';
      renderCalendario();
      return;
    } catch (_) { continue; }
  }
  if (loading) loading.innerHTML = `
    <div class="text-center py-4">
      <p class="text-red-400 text-sm mb-3">No se pudo cargar el calendario.</p>
      <a href="https://www.forexfactory.com/calendar" target="_blank" rel="noopener"
         class="text-sky-500 text-sm hover:underline">Ver calendario en Forex Factory →</a>
    </div>`;
}

// ── MINI PLAYER ───────────────────────────────────────────────
function toggleMiniPlayer() {
  document.getElementById('mini-player').classList.toggle('collapsed');
}

// ── PLAYERS ───────────────────────────────────────────────────
function renderPlayers() {
  const musicaSrc = `https://www.youtube.com/embed/${MUSICA_PRIMER_VIDEO_ID}?list=${MUSICA_PLAYLIST_ID}&rel=0&autoplay=0`;

  const musica = document.getElementById('iframe-musica');
  if (musica) musica.src = musicaSrc;

  const miniMusica = document.getElementById('iframe-mini-musica');
  if (miniMusica) miniMusica.src = musicaSrc;

}

// ── INIT ──────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  renderSesiones();
  renderVideos();
  renderPlayers();
  cargarCalendario();
});
