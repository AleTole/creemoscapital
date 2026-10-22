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
  const cont = document.getElementById('ff-calendar');
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
  document.querySelectorAll('.cal-btn').forEach(b => b.classList.remove('cal-btn-active'));
  const btnActivo = document.getElementById(`btn-${filtro}`);
  if (btnActivo) btnActivo.classList.add('cal-btn-active');
  renderCalendario();
}

async function cargarCalendario() {
  const loading = document.getElementById('ff-calendar-loading');
  const FF_URL  = 'https://nfs.faireconomy.media/ff_calendar_thisweek.json?timezone=America%2FBogota';
  const PROXIES = [
    '/calendar-proxy.php',
    FF_URL,
    `https://api.allorigins.win/raw?url=${encodeURIComponent(FF_URL)}`,
    `https://corsproxy.io/?${encodeURIComponent(FF_URL)}`,
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
      if (loading) loading.style.display = 'none';
      renderCalendario();
      mostrarAlertaNoticias();
      return;
    } catch (e) { errores.push(`${url} → ${e.message}`); continue; }
  }
  if (loading) loading.innerHTML = `
    <div class="text-center py-10">
      <div style="font-size:2rem;margin-bottom:0.75rem;">📅</div>
      <p style="color:#64748b;font-size:0.9rem;margin-bottom:1.25rem;">El calendario no está disponible en este momento.</p>
      <a href="https://www.forexfactory.com/calendar" target="_blank" rel="noopener"
         style="display:inline-flex;align-items:center;gap:0.5rem;padding:0.6rem 1.4rem;border:1px solid rgba(0,212,255,0.35);border-radius:6px;color:#00d4ff;font-size:0.85rem;text-decoration:none;">
        Ver calendario en Forex Factory →
      </a>
    </div>`;
}

// ── ALERTA DE NOTICIAS DEL DÍA ──────────────────────────────────
const ACTIVOS_POR_MONEDA = {
  USD: 'Dólar (DXY), todos los pares con USD, oro, índices US30/NAS100/SPX500',
  EUR: 'EUR/USD, EUR/GBP, EUR/JPY',
  GBP: 'GBP/USD, EUR/GBP, GBP/JPY',
  JPY: 'USD/JPY, EUR/JPY, GBP/JPY',
  CAD: 'USD/CAD, CAD/JPY, petróleo (WTI)',
  AUD: 'AUD/USD, AUD/JPY, AUD/NZD',
  NZD: 'NZD/USD, AUD/NZD',
  CHF: 'USD/CHF, EUR/CHF',
  CNY: 'USD/CNY, mercados asiáticos, cobre',
};

function mostrarAlertaNoticias() {
  const ahora = new Date();
  const hoy = new Date(ahora);
  hoy.setHours(0, 0, 0, 0);
  const manana = new Date(hoy);
  manana.setDate(manana.getDate() + 1);

  const key = `noticias_alerta_${hoy.toISOString().slice(0, 10)}`;
  if (localStorage.getItem(key)) return;

  const deHoy = _calEventos
    .filter(e => {
      const f = new Date(e.date);
      return f >= ahora && f < manana && (e.impact === 'High' || e.impact === 'Medium');
    })
    .sort((a, b) => new Date(a.date) - new Date(b.date));

  if (deHoy.length === 0) return;

  const cont = document.getElementById('noticias-alerta-lista');
  const overlay = document.getElementById('noticias-alerta-overlay');
  if (!cont || !overlay) return;

  cont.innerHTML = deHoy.map(e => {
    const code = (e.country || e.currency || '').toUpperCase().trim();
    const pais = PAISES[code] || { nombre: code || '—', bandera: '🌐' };
    const activos = (ACTIVOS_POR_MONEDA[code] || 'Revisar el par correspondiente').split(',').map(a => a.trim());
    const esAlto = e.impact === 'High';
    const color = esAlto ? '#ef4444' : '#f97316';
    const bg    = esAlto ? 'rgba(239,68,68,0.06)' : 'rgba(249,115,22,0.06)';
    const border= esAlto ? 'rgba(239,68,68,0.25)' : 'rgba(249,115,22,0.25)';
    return `
      <div style="background:${bg};border:1px solid ${border};border-radius:10px;padding:0.85rem 1rem;">
        <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.4rem;flex-wrap:wrap;">
          <span style="font-size:0.65rem;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;color:${color};background:rgba(255,255,255,0.06);border:1px solid ${border};border-radius:999px;padding:0.15rem 0.55rem;">${esAlto ? 'Alto' : 'Medio'}</span>
          <span style="font-size:0.75rem;color:#94a3b8;font-weight:600;">${formatoHora(e.date)}</span>
          <span style="font-size:0.9rem;">${pais.bandera}</span>
        </div>
        <div style="font-size:0.88rem;color:#f1f5f9;font-weight:600;margin-bottom:0.5rem;">${esc(e.title)}</div>
        <div style="display:flex;flex-wrap:wrap;gap:0.35rem;">
          ${activos.map(a => `<span style="font-size:0.68rem;color:#94a3b8;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:6px;padding:0.2rem 0.5rem;">${esc(a)}</span>`).join('')}
        </div>
      </div>`;
  }).join('');

  overlay.style.display = 'flex';
  localStorage.setItem(key, '1');
}

function cerrarAlertaNoticias() {
  const overlay = document.getElementById('noticias-alerta-overlay');
  if (overlay) overlay.style.display = 'none';
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

  // Spotify iframe carga con src fijo (no requiere Observer)
});
