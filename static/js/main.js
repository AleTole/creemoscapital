// =================================================================
//  CREEMOS CAPITAL — Lógica del sitio
// =================================================================

// ── UTILIDADES ────────────────────────────────────────────────
function esc(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

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
        <span class="video-duracion">${v.duracion || ''}</span>
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
  ALL: { nombre: 'Global',      bandera: 'gl'  },
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
  const cont = document.getElementById('calendario-content') || document.getElementById('ff-calendar');
  if (!cont) return;

  const filtrados = _calEventos.filter(e => {
    if (_calFiltro === 'alto')  return e.impact === 'High';
    if (_calFiltro === 'medio') return e.impact === 'Medium';
    if (_calFiltro === 'bajo')  return e.impact === 'Low';
    return true;
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
      const code   = (e.country || e.currency || '').toUpperCase().trim();
      const pais   = PAISES[code] || { nombre: code || '—', bandera: '🌐' };
      const imp    = e.impact === 'High' ? 'alto' : e.impact === 'Medium' ? 'medio' : 'bajo';
      const actual = e.actual || '';
      const cls    = actual ? claseActual(actual, e.forecast, e.impact) : 'pendiente';
      return `
      <div class="cal-row">
        <span class="cal-time">${formatoHora(e.date)}</span>
        <span class="cal-pais" title="${pais.nombre}"><span class="cal-impacto"><span class="imp-${imp}"></span></span>${pais.bandera}</span>
        <span class="cal-evento">${esc(e.title)}</span>
        <span class="cal-num cal-forecast">${esc(e.forecast) || '—'}</span>
        <span class="cal-num cal-prev">${esc(e.previous) || '—'}</span>
        <span class="cal-num cal-actual ${cls}">${esc(actual) || '·'}</span>
      </div>`;
    }).join('')}
  `).join('');
}

function filtrarCalendario(filtro) {
  _calFiltro = filtro;
  document.querySelectorAll('.cal-btn').forEach(b => {
    b.classList.toggle('cal-btn-active', b.dataset.filter === filtro);
  });
  renderCalendario();
}

async function cargarCalendario() {
  const spinner = document.getElementById('calendario-spinner');
  const content = document.getElementById('calendario-content');
  const container = document.getElementById('calendario-content');
  const FF_URL  = 'https://nfs.faireconomy.media/ff_calendar_thisweek.json?timezone=America%2FBogota';
  const DJANGO_PROXY = window.CALENDARIO_API_URL || '/api/calendario/';
  const PROXIES = [
    DJANGO_PROXY,
    `https://corsproxy.io/?${encodeURIComponent(FF_URL)}`,
    `https://api.allorigins.win/raw?url=${encodeURIComponent(FF_URL)}`,
    FF_URL,
  ];
  const errores = [];
  for (const url of PROXIES) {
    try {
      const res  = await fetch(url);
      const text = await res.text();
      let data;
      try { data = JSON.parse(text); } catch(e) { errores.push(`${url} → JSON inválido: ${text.substring(0,80)}`); continue; }
      if (!Array.isArray(data)) { errores.push(`${url} → No es array: ${text.substring(0,80)}`); continue; }
      const hoy = new Date();
      hoy.setHours(0, 0, 0, 0);
      _calEventos = data.filter(e => {
        const fecha = new Date(e.date);
        return fecha >= hoy && e.impact !== 'Holiday';
      });
      if (spinner) spinner.style.display = 'none';
      if (content) content.style.display = 'block';
      renderCalendario();
      return;
    } catch (e) { errores.push(`${url} → ${e.message}`); continue; }
  }
  if (spinner) spinner.innerHTML = `
    <div class="text-center py-10">
      <div style="font-size:2rem;margin-bottom:0.75rem;">📅</div>
      <p style="color:#64748b;font-size:0.9rem;margin-bottom:1.25rem;">El calendario no está disponible en este momento.</p>
      <a href="https://www.forexfactory.com/calendar" target="_blank" rel="noopener"
         style="display:inline-flex;align-items:center;gap:0.5rem;padding:0.6rem 1.4rem;border:1px solid rgba(0,212,255,0.35);border-radius:6px;color:#00d4ff;font-size:0.85rem;text-decoration:none;">
        Ver calendario en Forex Factory →
      </a>
    </div>`;
}

// ── MODAL MÚSICA ──────────────────────────────────────────────
function showMusicModal() {
  const overlay = document.getElementById('music-modal-overlay');
  if (overlay && !sessionStorage.getItem('music-decided')) {
    overlay.style.display = 'flex';
  }
}

function cerrarModal() {
  sessionStorage.setItem('music-decided', 'true');
  const overlay = document.getElementById('music-modal-overlay');
  if (overlay) overlay.style.display = 'none';
}

// ── MUSIC PLAYER (YouTube IFrame API) ─────────────────────────
let _ytPlayer      = null;
let _ytReady       = false;
let _ytAutoplay    = false;
let _progressTimer = null;

function onYouTubeIframeAPIReady() {
  _ytPlayer = new YT.Player('yt-player-hidden', {
    height: '1', width: '1',
    playerVars: { listType: 'playlist', list: window.YOUTUBE_PLAYLIST_ID || 'UUv4ma-yTMOqYYF_Ii5kv0zQ', rel: 0, autoplay: 0 },
    events: {
      onReady: (e) => {
        _ytReady = true;
        e.target.setVolume(80);
        if (_ytAutoplay) e.target.playVideo();
      },
      onStateChange: (e) => {
        const playing = e.data === YT.PlayerState.PLAYING;
        const playIcon = document.getElementById('music-play-icon');
        if (playIcon) {
          playIcon.innerHTML = playing
            ? '<path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>'
            : '<path d="M8 5v14l11-7z"/>';
        }
        if (playing) { _startProgress(); _updateTitle(); }
        else clearInterval(_progressTimer);
      },
    },
  });
}

function _updateTitle() {
  if (!_ytPlayer || !_ytPlayer.getVideoData) return;
  const data = _ytPlayer.getVideoData();
  const el = document.getElementById('music-title');
  if (el && data && data.title) el.textContent = data.title;
}

function _startProgress() {
  clearInterval(_progressTimer);
  _progressTimer = setInterval(() => {
    if (!_ytPlayer || !_ytPlayer.getDuration) return;
    const dur = _ytPlayer.getDuration();
    const cur = _ytPlayer.getCurrentTime();
    const bar = document.getElementById('music-progress');
    if (bar && dur > 0) bar.style.width = (cur / dur * 100) + '%';
  }, 1000);
}

function musicTogglePlay() {
  if (!_ytReady || !_ytPlayer) return;
  const state = _ytPlayer.getPlayerState();
  if (state === YT.PlayerState.PLAYING) _ytPlayer.pauseVideo();
  else _ytPlayer.playVideo();
}

function musicNext() {
  if (!_ytReady || !_ytPlayer) return;
  _ytPlayer.nextVideo();
  setTimeout(_updateTitle, 1200);
}

function musicPrev() {
  if (!_ytReady || !_ytPlayer) return;
  _ytPlayer.previousVideo();
  setTimeout(_updateTitle, 1200);
}

function musicVolume(val) {
  if (!_ytReady || !_ytPlayer) return;
  _ytPlayer.setVolume(parseInt(val));
}

function toggleMusicDropdown() {
  const dropdown = document.getElementById('music-dropdown');
  const chevron  = document.getElementById('music-nav-chevron');
  const isOpen   = dropdown.style.display === 'block';
  dropdown.style.display = isOpen ? 'none' : 'block';
  if (chevron) chevron.style.transform = isOpen ? '' : 'rotate(180deg)';
}

function activarMusica() {
  cerrarModal();
  const dropdown = document.getElementById('music-dropdown');
  const chevron  = document.getElementById('music-nav-chevron');
  dropdown.style.display = 'block';
  if (chevron) chevron.style.transform = 'rotate(180deg)';
  if (_ytReady && _ytPlayer) _ytPlayer.playVideo();
  else _ytAutoplay = true;
}

// ── OKX TICKER ────────────────────────────────────────────────
const OKX_PARES = ['BTC-USDT','ETH-USDT','SOL-USDT','XRP-USDT','BNB-USDT','DOGE-USDT','ADA-USDT','AVAX-USDT','LINK-USDT','TON-USDT'];

function fmtPrecio(n) {
  if (n >= 1000) return n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  if (n >= 1)    return n.toFixed(3);
  return n.toFixed(5);
}

function renderTickerOKX(data) {
  const cont = document.getElementById('okx-ticker-items');
  if (!cont) return;
  const mapa = {};
  data.forEach(t => { mapa[t.instId] = t; });

  const html = OKX_PARES.map(par => {
    const t = mapa[par];
    if (!t) return '';
    const precio = parseFloat(t.last);
    const open   = parseFloat(t.sodUtc8);
    const pct    = open > 0 ? ((precio - open) / open * 100) : 0;
    const pos    = pct >= 0;
    const base   = par.split('-')[0];
    return `<div class="okx-item">
      <span class="okx-name">${base}</span>
      <span class="okx-price">$${fmtPrecio(precio)}</span>
      <span class="okx-pct ${pos ? 'okx-pos' : 'okx-neg'}">${pos ? '▲' : '▼'} ${Math.abs(pct).toFixed(2)}%</span>
    </div>`;
  }).join('<span class="okx-sep">·</span>');

  // Duplicar para scroll infinito
  cont.innerHTML = html + '<span class="okx-sep" style="padding:0 2rem;"></span>' + html;
}

async function cargarTickerOKX() {
  const OKX_API = 'https://www.okx.com/api/v5/market/tickers?instType=SPOT';
  const urls = [
    OKX_API,
    `https://corsproxy.io/?${encodeURIComponent(OKX_API)}`,
  ];
  for (const url of urls) {
    try {
      const res  = await fetch(url, { cache: 'no-store' });
      const json = await res.json();
      if (json.code === '0' && Array.isArray(json.data)) {
        renderTickerOKX(json.data);
        setInterval(async () => {
          try {
            const r = await fetch(url, { cache: 'no-store' });
            const j = await r.json();
            if (j.code === '0') renderTickerOKX(j.data);
          } catch(_) {}
        }, 15000);
        return;
      }
    } catch(_) { continue; }
  }
}

// ── INIT ──────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  renderSesiones();
  renderVideos();
  cargarCalendario();
  cargarTickerOKX();

  document.querySelectorAll('.cal-btn').forEach(btn => {
    btn.addEventListener('click', () => filtrarCalendario(btn.dataset.filter));
  });

  const MUSICA_PLAYLIST_ID = window.YOUTUBE_PLAYLIST_ID || 'UUv4ma-yTMOqYYF_Ii5kv0zQ';
});
