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
const navbar = document.getElementById('navbar');
function marcarNavbar() { if (navbar) navbar.classList.toggle('scrolled', window.scrollY > 10); }
window.addEventListener('scroll', marcarNavbar, { passive: true });
marcarNavbar();

// ── MENÚ MOBILE ───────────────────────────────────────────────
function setMenu(abierto) {
  const menu = document.getElementById('mobile-menu');
  const btn = document.getElementById('menu');
  if (!menu) return;
  menu.classList.toggle('open', abierto);
  if (btn) btn.setAttribute('aria-expanded', String(abierto));
}
const btnMenu = document.getElementById('menu');
if (btnMenu) btnMenu.addEventListener('click', () => {
  setMenu(!document.getElementById('mobile-menu').classList.contains('open'));
});
document.querySelectorAll('#mobile-menu a').forEach(a => a.addEventListener('click', () => setMenu(false)));

// ── TEMA CLARO / OSCURO ───────────────────────────────────────
const btnTema = document.getElementById('theme');
if (btnTema) btnTema.addEventListener('click', () => {
  const root = document.documentElement;
  const siguiente = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  root.setAttribute('data-theme', siguiente);
  try { localStorage.setItem('cc-theme', siguiente); } catch (e) {}
});

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
  USD: { nombre: 'EE.UU.',      iso: 'us' },
  EUR: { nombre: 'Eurozona',    iso: 'eu' },
  GBP: { nombre: 'Reino Unido', iso: 'gb' },
  JPY: { nombre: 'Japón',       iso: 'jp' },
  CAD: { nombre: 'Canadá',      iso: 'ca' },
  AUD: { nombre: 'Australia',   iso: 'au' },
  NZD: { nombre: 'N. Zelanda',  iso: 'nz' },
  CHF: { nombre: 'Suiza',       iso: 'ch' },
  CNY: { nombre: 'China',       iso: 'cn' },
  SEK: { nombre: 'Suecia',      iso: 'se' },
  NOK: { nombre: 'Noruega',     iso: 'no' },
  MXN: { nombre: 'México',      iso: 'mx' },
  BRL: { nombre: 'Brasil',      iso: 'br' },
  ALL: { nombre: 'Global',      iso: null },
};

const GLOBO = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M3.6 9h16.8M3.6 15h16.8M12 3a14.5 14.5 0 010 18M12 3a14.5 14.5 0 000 18"/></svg>';
function banderaPais(pais) {
  return pais.iso ? flagImg(pais.iso) : GLOBO;
}

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
    cont.innerHTML = '<div class="cal-state">Sin eventos para mostrar.</div>';
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
      const pais   = PAISES[code] || { nombre: code || '—', iso: null };
      const imp    = e.impact === 'High' ? 'alto' : e.impact === 'Medium' ? 'medio' : 'bajo';
      const actual = e.actual || '';
      const cls    = actual ? claseActual(actual, e.forecast, e.impact) : 'pendiente';
      return `
      <div class="cal-row">
        <span class="cal-time">${formatoHora(e.date)}</span>
        <span class="cal-pais" title="${pais.nombre}"><span class="cal-impacto"><span class="imp-${imp}"></span></span>${banderaPais(pais)}</span>
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
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>
    <p>El calendario no está disponible en este momento.</p>
    <a class="btn btn-ghost btn-sm" href="https://www.forexfactory.com/calendar" target="_blank" rel="noopener">Ver calendario en Forex Factory →</a>`;
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
    const pais = PAISES[code] || { nombre: code || '—', iso: null };
    const activos = (ACTIVOS_POR_MONEDA[code] || 'Revisar el par correspondiente').split(',').map(a => a.trim());
    const nivel = e.impact === 'High' ? 'alto' : 'medio';
    return `
      <div class="alert-item ${nivel}">
        <div class="alert-item-top">
          <span class="badge ${nivel}">${nivel === 'alto' ? 'Alto' : 'Medio'}</span>
          <span class="alert-hora">${formatoHora(e.date)}</span>
          ${banderaPais(pais)}
        </div>
        <div class="alert-titulo">${esc(e.title)}</div>
        <div class="chips">${activos.map(a => `<span>${esc(a)}</span>`).join('')}</div>
      </div>`;
  }).join('');

  overlay.style.display = 'flex';
  localStorage.setItem(key, '1');
}

function cerrarAlertaNoticias() {
  const overlay = document.getElementById('noticias-alerta-overlay');
  if (overlay) overlay.style.display = 'none';
}

// ── TICKER BITGET ─────────────────────────────────────────────
// API pública de Bitget (sin clave, con CORS abierto). Bitget Token (BGB) primero.
const TICKER_PARES = ['BGB','BTC','ETH','SOL','XRP','BNB','DOGE','ADA','AVAX','LINK','TRX'];

function fmtPrecio(n) {
  if (n >= 1000) return n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  if (n >= 1)    return n.toFixed(3);
  return n.toFixed(5);
}

function renderTicker(data) {
  const cont = document.getElementById('ticker-items');
  if (!cont) return;
  const mapa = {};
  data.forEach(t => { mapa[t.symbol] = t; });

  const html = TICKER_PARES.map(base => {
    const t = mapa[base + 'USDT'];
    if (!t) return '';
    const precio = parseFloat(t.lastPr);
    const pct    = parseFloat(t.change24h) * 100;   // Bitget entrega el cambio 24h como fracción
    if (isNaN(precio) || isNaN(pct)) return '';
    const pos = pct >= 0;
    return `<div class="tk-item">
      <span class="tk-name">${base}</span>
      <span class="tk-price">$${fmtPrecio(precio)}</span>
      <span class="tk-pct ${pos ? 'tk-pos' : 'tk-neg'}">${pos ? '▲' : '▼'} ${Math.abs(pct).toFixed(2)}%</span>
    </div>`;
  }).filter(Boolean).join('<span class="tk-sep">·</span>');

  if (!html) return;
  // Duplicar para scroll infinito
  cont.innerHTML = html + '<span class="tk-sep" style="padding:0 2rem;"></span>' + html;
}

async function cargarTicker() {
  if (!document.getElementById('ticker-items')) return;
  const URL_API = 'https://api.bitget.com/api/v2/spot/market/tickers';
  async function leer() {
    const res  = await fetch(URL_API, { cache: 'no-store' });
    const json = await res.json();
    if (json.code !== '00000' || !Array.isArray(json.data)) throw new Error('respuesta inesperada');
    renderTicker(json.data);
  }
  try {
    await leer();
    setInterval(() => { leer().catch(() => {}); }, 15000);
  } catch (_) {
    const cont = document.getElementById('ticker-items');
    if (cont) cont.innerHTML = '<span class="ticker-empty">Precios no disponibles por ahora.</span>';
  }
}

// ── ANIMACIONES (aparecer al hacer scroll, titular rotatorio, línea de pasos) ──
const reducirMovimiento = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function iniciarReveal() {
  const items = document.querySelectorAll('.reveal');
  if (!('IntersectionObserver' in window)) { items.forEach(el => el.classList.add('in')); return; }
  const io = new IntersectionObserver(entries => {
    entries.forEach(en => { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
  items.forEach(el => io.observe(el));
}

function iniciarRotator() {
  const palabras = document.querySelectorAll('.rotator span');
  if (palabras.length < 2 || reducirMovimiento) return;
  let i = 0;
  setInterval(() => {
    const actual = palabras[i];
    i = (i + 1) % palabras.length;
    const siguiente = palabras[i];
    actual.classList.remove('on'); actual.classList.add('out');
    siguiente.classList.remove('out'); siguiente.classList.add('on');
    setTimeout(() => { actual.classList.remove('out'); }, 750);
  }, 2600);
}

function iniciarPasos() {
  const cont = document.getElementById('steps');
  if (!cont) return;
  const pasos = cont.querySelectorAll('.step');
  function actualizar() {
    const r = cont.getBoundingClientRect();
    const centro = window.innerHeight * 0.55;
    const p = Math.min(1, Math.max(0, (centro - r.top) / r.height));
    cont.style.setProperty('--p', p.toFixed(3));
    pasos.forEach(el => {
      const b = el.getBoundingClientRect();
      el.classList.toggle('lit', b.top + 30 < centro);
    });
  }
  window.addEventListener('scroll', actualizar, { passive: true });
  window.addEventListener('resize', actualizar);
  actualizar();
}

function iniciarSpotlight() {
  document.querySelectorAll('.card, .link-card').forEach(el => {
    el.addEventListener('pointermove', e => {
      const r = el.getBoundingClientRect();
      el.style.setProperty('--mx', (e.clientX - r.left) + 'px');
      el.style.setProperty('--my', (e.clientY - r.top) + 'px');
    });
  });
}

// ── INIT ──────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.body.classList.remove('no-js');
  renderSesiones();
  renderVideos();
  cargarCalendario();
  cargarTicker();
  iniciarReveal();
  iniciarRotator();
  iniciarPasos();
  iniciarSpotlight();
});
