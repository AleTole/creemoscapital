// =================================================================
//  CREEMOS CAPITAL — Portada: terminal de mercados, directo, serie de Shorts y noticias
//  Sin librerías externas. Datos: API pública de Bitget (cotizaciones y velas) y
//  archivos de /data (serie de videos y noticias, los mantiene .github/workflows/datos.yml).
// =================================================================
(function () {
  'use strict';

  const $ = (sel, root) => (root || document).querySelector(sel);
  const el = (tag, cls, text) => {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  };

  // ───────────────────────── Terminal de mercados ─────────────────────────
  const API = 'https://api.bitget.com/api/v2/mix/market';
  const PRODUCTO = 'USDT-FUTURES';

  // Contratos perpetuos USDT de Bitget. Nota: SPXUSDT es la cripto SPX6900, no el índice; el S&P 500 va por SPY.
  const CATEGORIAS = [['cripto', 'Cripto'], ['metales', 'Metales'], ['indices', 'Índices'], ['acciones', 'Acciones']];
  const ACTIVOS = [
    { cat: 'cripto',   s: 'BTCUSDT',  c: 'BTC',   n: 'Bitcoin',   d: 'BTC · contrato perpetuo' },
    { cat: 'cripto',   s: 'ETHUSDT',  c: 'ETH',   n: 'Ethereum',  d: 'ETH · contrato perpetuo' },
    { cat: 'cripto',   s: 'SOLUSDT',  c: 'SOL',   n: 'Solana',    d: 'SOL · contrato perpetuo' },
    { cat: 'cripto',   s: 'XRPUSDT',  c: 'XRP',   n: 'XRP',       d: 'XRP · contrato perpetuo' },
    { cat: 'metales',  s: 'XAUUSDT',  c: 'XAU',   n: 'Oro',       d: 'XAU/USD · contrato perpetuo' },
    { cat: 'metales',  s: 'XAGUSDT',  c: 'XAG',   n: 'Plata',     d: 'XAG/USD · contrato perpetuo' },
    { cat: 'indices',  s: 'SPYUSDT',  c: 'SPY',   n: 'S&P 500',   d: 'ETF SPY · replica el S&P 500' },
    { cat: 'indices',  s: 'QQQUSDT',  c: 'QQQ',   n: 'Nasdaq 100', d: 'ETF QQQ · replica el Nasdaq 100' },
    { cat: 'acciones', s: 'NVDAUSDT', c: 'NVDA',  n: 'Nvidia',    d: 'NVDA · acción (contrato)' },
    { cat: 'acciones', s: 'TSLAUSDT', c: 'TSLA',  n: 'Tesla',     d: 'TSLA · acción (contrato)' },
    { cat: 'acciones', s: 'AAPLUSDT', c: 'AAPL',  n: 'Apple',     d: 'AAPL · acción (contrato)' },
    { cat: 'acciones', s: 'MSFTUSDT', c: 'MSFT',  n: 'Microsoft', d: 'MSFT · acción (contrato)' },
    { cat: 'acciones', s: 'GOOGLUSDT', c: 'GOOGL', n: 'Alphabet (Google)', d: 'GOOGL · acción (contrato)' },
    { cat: 'acciones', s: 'AMZNUSDT', c: 'AMZN',  n: 'Amazon',    d: 'AMZN · acción (contrato)' },
    { cat: 'acciones', s: 'METAUSDT', c: 'META',  n: 'Meta',      d: 'META · acción (contrato)' },
  ];
  const TEMPORALIDADES = [['5m', '5m'], ['15m', '15m'], ['1h', '1H'], ['4h', '4H'], ['1d', '1D']]; // [etiqueta, granularidad Bitget]

  const estado = { cat: 'cripto', activo: ACTIVOS[0], tf: '1h', token: 0 };

  function decimales(n) {
    const a = Math.abs(n);
    if (a >= 100) return 2;
    if (a >= 10) return 3;
    if (a >= 1) return 4;
    return 5;
  }
  function fmt(n) {
    if (!isFinite(n)) return '—';
    const d = decimales(n);
    return n.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d });
  }
  function compacto(n) {
    if (!isFinite(n)) return '—';
    return new Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 2 }).format(n);
  }

  async function pedir(url) {
    const r = await fetch(url, { cache: 'no-store' });
    if (!r.ok) throw new Error('HTTP ' + r.status);
    const j = await r.json();
    if (j.code !== '00000') throw new Error(j.msg || 'error de API');
    return j.data;
  }
  async function pedirVelas(simbolo, gran, limite) {
    const d = await pedir(`${API}/candles?symbol=${simbolo}&productType=${PRODUCTO}&granularity=${gran}&limit=${limite}`);
    return d.map(r => ({ t: +r[0], o: +r[1], h: +r[2], l: +r[3], c: +r[4] })).sort((a, b) => a.t - b.t);
  }
  async function pedirTicker(simbolo) {
    const d = await pedir(`${API}/ticker?symbol=${simbolo}&productType=${PRODUCTO}`);
    return d[0];
  }

  // ── Gráfico de velas (canvas) ──
  class Grafico {
    constructor(cont) {
      this.cont = cont;
      this.cv = cont.querySelector('canvas');
      this.ctx = this.cv.getContext('2d');
      this.tip = $('#mk-tip');
      this.datos = [];
      this.tf = '1h';
      this.hover = null;
      this.w = 0; this.h = 0; this.dpr = 1;
      new ResizeObserver(() => this.ajustar()).observe(cont);
      new MutationObserver(() => this.dibujar()).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
      this.cv.addEventListener('pointermove', e => this.mover(e));
      this.cv.addEventListener('pointerleave', () => this.salir());
      this.cv.addEventListener('pointercancel', () => this.salir());
    }
    ajustar() {
      const r = this.cont.getBoundingClientRect();
      this.dpr = window.devicePixelRatio || 1;
      this.w = r.width; this.h = r.height;
      this.cv.width = Math.round(r.width * this.dpr);
      this.cv.height = Math.round(r.height * this.dpr);
      this.dibujar();
    }
    poner(datos, tf) { this.datos = datos; this.tf = tf; this.hover = null; this.tip.classList.remove('on'); this.dibujar(); }
    fusionar(velas) {
      if (!this.datos.length) return;
      velas.forEach(v => {
        const ult = this.datos[this.datos.length - 1];
        if (v.t === ult.t) this.datos[this.datos.length - 1] = v;
        else if (v.t > ult.t) this.datos.push(v);
      });
      this.dibujar();
    }
    geometria() {
      const padL = 6, padR = 68, padT = 12, padB = 26;
      const pw = Math.max(10, this.w - padL - padR), ph = Math.max(10, this.h - padT - padB);
      const n = Math.max(10, Math.min(this.datos.length, Math.floor(pw / 7)));
      const vis = this.datos.slice(-n);
      let min = Infinity, max = -Infinity;
      vis.forEach(v => { if (v.l < min) min = v.l; if (v.h > max) max = v.h; });
      const pad = (max - min) * 0.07 || max * 0.01 || 1;
      min -= pad; max += pad;
      return { padL, padR, padT, padB, pw, ph, n, vis, min, max, paso: pw / n };
    }
    y(g, v) { return g.padT + g.ph * (1 - (v - g.min) / (g.max - g.min)); }
    etiquetaHora(ts, largo) {
      const d = new Date(ts);
      if (this.tf === '1d' || this.tf === '4h') return d.toLocaleDateString('es', { day: 'numeric', month: 'short' });
      const hora = d.toLocaleTimeString('es', { hour: '2-digit', minute: '2-digit', hour12: false });
      // si el gráfico abarca más de un día, la hora sola se repite y confunde: se añade la fecha
      return largo ? d.toLocaleDateString('es', { day: 'numeric', month: 'short' }) + ' ' + hora : hora;
    }
    dibujar() {
      const c = this.ctx;
      if (!this.w) return;
      c.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
      c.clearRect(0, 0, this.w, this.h);
      if (!this.datos.length) return;

      const cs = getComputedStyle(document.documentElement);
      const col = n => cs.getPropertyValue(n).trim();
      const up = col('--up'), down = col('--down'), linea = col('--line'), lineaFuerte = col('--line-2');
      const tenue = col('--faint'), texto = col('--text'), fondo = col('--bg');
      const g = this.g = this.geometria();
      c.font = '11px "Geist Mono", ui-monospace, monospace';
      c.textBaseline = 'middle';

      // cuadrícula + eje de precios
      c.lineWidth = 1;
      for (let k = 0; k <= 4; k++) {
        const yy = Math.round(g.padT + (g.ph * k) / 4) + 0.5;
        c.strokeStyle = linea;
        c.beginPath(); c.moveTo(g.padL, yy); c.lineTo(this.w - g.padR, yy); c.stroke();
        c.fillStyle = tenue; c.textAlign = 'left';
        c.fillText(fmt(g.max - ((g.max - g.min) * k) / 4), this.w - g.padR + 8, yy);
      }
      // eje de tiempo
      c.textAlign = 'center'; c.fillStyle = tenue;
      const marcas = Math.max(2, Math.min(6, Math.floor(g.pw / 120)));
      const abarcaDias = g.vis[g.n - 1].t - g.vis[0].t > 20 * 3600 * 1000;
      for (let k = 0; k < marcas; k++) {
        const i = Math.round(((g.n - 1) * (k + 0.5)) / marcas);
        c.fillText(this.etiquetaHora(g.vis[i].t, abarcaDias), g.padL + g.paso * (i + 0.5), this.h - g.padB / 2 + 2);
      }
      // velas
      const cuerpo = Math.max(1, Math.floor(g.paso * 0.66));
      g.vis.forEach((v, i) => {
        const x = g.padL + g.paso * (i + 0.5);
        const subio = v.c >= v.o;
        c.strokeStyle = c.fillStyle = subio ? up : down;
        c.beginPath(); c.moveTo(Math.round(x) + 0.5, this.y(g, v.h)); c.lineTo(Math.round(x) + 0.5, this.y(g, v.l)); c.stroke();
        const yo = this.y(g, v.o), yc = this.y(g, v.c);
        c.fillRect(Math.round(x - cuerpo / 2), Math.min(yo, yc), cuerpo, Math.max(1, Math.abs(yc - yo)));
      });
      // último precio
      const ult = g.vis[g.vis.length - 1];
      const yu = Math.round(this.y(g, ult.c)) + 0.5;
      const colUlt = ult.c >= ult.o ? up : down;
      c.setLineDash([4, 4]); c.strokeStyle = colUlt; c.beginPath(); c.moveTo(g.padL, yu); c.lineTo(this.w - g.padR, yu); c.stroke(); c.setLineDash([]);
      this.etiquetaEje(c, g, yu, fmt(ult.c), colUlt, fondo);

      // cruz del cursor
      if (this.hover != null) {
        const i = Math.max(0, Math.min(g.n - 1, this.hover.i));
        const v = g.vis[i];
        const x = Math.round(g.padL + g.paso * (i + 0.5)) + 0.5;
        c.strokeStyle = lineaFuerte; c.setLineDash([3, 3]);
        c.beginPath(); c.moveTo(x, g.padT); c.lineTo(x, g.padT + g.ph); c.stroke();
        if (this.hover.y >= g.padT && this.hover.y <= g.padT + g.ph) {
          c.beginPath(); c.moveTo(g.padL, this.hover.y); c.lineTo(this.w - g.padR, this.hover.y); c.stroke();
          const precio = g.max - ((this.hover.y - g.padT) / g.ph) * (g.max - g.min);
          c.setLineDash([]);
          this.etiquetaEje(c, g, this.hover.y, fmt(precio), texto, fondo);
        }
        c.setLineDash([]);
        const fecha = new Date(v.t).toLocaleString('es', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', hour12: false });
        const cls = v.c >= v.o ? 'up' : 'down';
        this.tip.innerHTML = `<em>${fecha}</em><br>A ${fmt(v.o)} · M ${fmt(v.h)}<br>m ${fmt(v.l)} · C <span class="${cls}">${fmt(v.c)}</span>`;
        this.tip.classList.add('on');
      }
    }
    etiquetaEje(c, g, yy, texto, color, fondo) {
      const wTxt = c.measureText(texto).width + 12;
      c.fillStyle = color;
      c.beginPath();
      if (c.roundRect) c.roundRect(this.w - g.padR + 2, yy - 10, Math.min(wTxt, g.padR - 2), 20, 6); else c.rect(this.w - g.padR + 2, yy - 10, Math.min(wTxt, g.padR - 2), 20);
      c.fill();
      c.fillStyle = fondo; c.textAlign = 'left';
      c.fillText(texto, this.w - g.padR + 8, yy);
    }
    mover(e) {
      if (!this.g || !this.datos.length) return;
      const r = this.cv.getBoundingClientRect();
      const x = e.clientX - r.left, y = e.clientY - r.top;
      this.hover = { i: Math.floor((x - this.g.padL) / this.g.paso), y };
      this.dibujar();
    }
    salir() { this.hover = null; this.tip.classList.remove('on'); this.dibujar(); }
  }

  // ── Pantalla del terminal ──
  let grafico = null;

  function estadoGrafico(texto) { $('#mk-state').textContent = texto || ''; }

  function pintarCategorias() {
    const cont = $('#mk-cats');
    cont.textContent = '';
    CATEGORIAS.forEach(([id, nombre]) => {
      const b = el('button', '', nombre);
      b.type = 'button'; b.dataset.cat = id;
      b.setAttribute('aria-pressed', String(id === estado.cat));
      cont.appendChild(b);
    });
  }
  function pintarActivos() {
    const cont = $('#mk-assets');
    cont.textContent = '';
    ACTIVOS.filter(a => a.cat === estado.cat).forEach(a => {
      const b = el('button', 'chip');
      b.type = 'button'; b.dataset.s = a.s;
      b.setAttribute('aria-pressed', String(a.s === estado.activo.s));
      b.append(el('span', '', a.c), el('small', '', a.n));
      cont.appendChild(b);
    });
  }
  function pintarTemporalidades() {
    const cont = $('#mk-tf');
    cont.textContent = '';
    TEMPORALIDADES.forEach(([id, gran]) => {
      const b = el('button', '', id);
      b.type = 'button'; b.dataset.tf = id; b.title = gran;
      b.setAttribute('aria-pressed', String(id === estado.tf));
      cont.appendChild(b);
    });
  }
  function pintarCabecera() {
    $('#mk-name').textContent = estado.activo.n;
    $('#mk-sub').textContent = estado.activo.d;
  }
  function pintarCotizacion(t) {
    const precio = parseFloat(t.lastPr), cambio = parseFloat(t.change24h) * 100;
    $('#mk-price').textContent = fmt(precio);
    const chg = $('#mk-chg');
    chg.textContent = (cambio >= 0 ? '+' : '−') + Math.abs(cambio).toFixed(2) + ' %';
    chg.className = 'chg num ' + (cambio >= 0 ? 'up' : 'down');
    $('#mk-hi').textContent = fmt(parseFloat(t.high24h));
    $('#mk-lo').textContent = fmt(parseFloat(t.low24h));
    $('#mk-vol').textContent = compacto(parseFloat(t.usdtVolume)) + ' USDT';
  }
  const granularidad = () => (TEMPORALIDADES.find(x => x[0] === estado.tf) || TEMPORALIDADES[2])[1];

  async function cargarGrafico() {
    const token = ++estado.token;
    estadoGrafico('Cargando gráfico…');
    try {
      const [velas, t] = await Promise.all([
        pedirVelas(estado.activo.s, granularidad(), 300),
        pedirTicker(estado.activo.s),
      ]);
      if (token !== estado.token) return;
      if (!velas.length) throw new Error('sin datos');
      grafico.poner(velas, estado.tf);
      pintarCotizacion(t);
      estadoGrafico('');
    } catch (_) {
      if (token !== estado.token) return;
      grafico.poner([], estado.tf);
      estadoGrafico('No pudimos cargar este activo ahora mismo. Inténtalo de nuevo en unos segundos.');
    }
  }
  async function refrescarGrafico() {
    if (document.hidden || !grafico.datos.length) return;
    const token = estado.token;
    try {
      const [velas, t] = await Promise.all([pedirVelas(estado.activo.s, granularidad(), 2), pedirTicker(estado.activo.s)]);
      if (token !== estado.token) return;
      grafico.fusionar(velas);
      pintarCotizacion(t);
    } catch (_) { /* se reintenta en el próximo ciclo */ }
  }

  function iniciarTerminal() {
    const cont = $('#mk-chart');
    if (!cont) return;
    grafico = new Grafico(cont);
    pintarCategorias(); pintarActivos(); pintarTemporalidades(); pintarCabecera();

    $('#mk-cats').addEventListener('click', e => {
      const b = e.target.closest('button'); if (!b) return;
      estado.cat = b.dataset.cat;
      estado.activo = ACTIVOS.find(a => a.cat === estado.cat);
      pintarCategorias(); pintarActivos(); pintarCabecera(); cargarGrafico();
    });
    $('#mk-assets').addEventListener('click', e => {
      const b = e.target.closest('button'); if (!b) return;
      estado.activo = ACTIVOS.find(a => a.s === b.dataset.s) || estado.activo;
      pintarActivos(); pintarCabecera(); cargarGrafico();
    });
    $('#mk-tf').addEventListener('click', e => {
      const b = e.target.closest('button'); if (!b) return;
      estado.tf = b.dataset.tf;
      pintarTemporalidades(); cargarGrafico();
    });
    cargarGrafico();
    setInterval(refrescarGrafico, 6000);
  }

  // ───────────────────────── Estado del directo (Kick) ─────────────────────────
  const KICK_API = 'https://kick.com/api/v2/channels/creemoscapital';
  const TITULO = document.title;
  let enVivo = null;

  function aplicarDirecto(live) {
    if (live === enVivo) return;
    enVivo = live;
    const bloque = $('#live-block'), pastilla = $('#nav-live'), player = $('#live-player');
    if (bloque) bloque.hidden = !live;
    if (pastilla) pastilla.hidden = !live;
    if (player) {
      if (live && !player.firstChild) {
        const f = document.createElement('iframe');
        f.src = 'https://player.kick.com/creemoscapital';
        f.title = 'Directo de Creemos Capital en Kick';
        f.allow = 'autoplay; fullscreen';
        f.allowFullscreen = true;
        f.setAttribute('scrolling', 'no');
        player.appendChild(f);
      } else if (!live) {
        player.textContent = '';              // se descarga el reproductor al terminar el directo
      }
    }
    document.title = live ? '🔴 Sesión en vivo · ' + TITULO : TITULO;
  }
  async function revisarDirecto() {
    if (/[?&]demo-live\b/.test(location.search)) return aplicarDirecto(true);   // para probar el aviso
    try {
      const r = await fetch(KICK_API, { cache: 'no-store', credentials: 'omit' });
      if (!r.ok) return;                     // sin respuesta fiable: no se cambia nada
      const j = await r.json();
      aplicarDirecto(!!(j && j.livestream));
    } catch (_) { /* si Kick no responde se mantiene el estado anterior (por defecto, sin aviso) */ }
  }

  // ───────────────────────── Serie "Día N de 33 operando con Bitget" ─────────────────────────
  const ID_VIDEO = /^[\w-]{11}$/;
  let reproduciendo = null;

  function logoBitget() {
    const i = el('img', 'bg-ico');
    i.src = './img/bitget.webp'; i.alt = ''; i.width = 16; i.height = 16;
    return i;
  }
  function iconoPlay() {
    const ns = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('viewBox', '0 0 24 24');
    const p = document.createElementNS(ns, 'path');
    p.setAttribute('d', 'M8 5v14l11-7z');
    svg.appendChild(p);
    return svg;
  }
  function tarjetaShort(v, esUltimo, total) {
    const b = el('button', 'short');
    b.type = 'button';
    b.setAttribute('aria-label', `Reproducir: Día ${v.dia} de ${total} operando con Bitget`);
    const img = el('img');
    img.src = `https://i.ytimg.com/vi/${v.id}/hqdefault.jpg`;
    img.alt = ''; img.loading = 'lazy'; img.decoding = 'async';
    const play = el('span', 'play'); play.appendChild(iconoPlay());
    b.append(img, el('span', 'day', `Día ${v.dia}`));
    if (esUltimo) b.appendChild(el('span', 'new', 'Último'));
    const pie = el('span', 'cap', `Día ${v.dia} de ${total} operando con Bitget`);
    pie.appendChild(logoBitget());
    b.append(play, pie);
    b.addEventListener('click', () => reproducir(b, v, esUltimo, total));
    return b;
  }
  function reproducir(tarjeta, v, esUltimo, total) {
    if (reproduciendo && reproduciendo.nodo !== tarjeta) {       // solo uno a la vez: se restaura el anterior
      const prev = reproduciendo;
      prev.nodo.replaceWith(tarjetaShort(prev.v, prev.esUltimo, prev.total));
    }
    if (tarjeta.classList.contains('playing')) return;
    tarjeta.classList.add('playing');
    tarjeta.textContent = '';
    const f = document.createElement('iframe');
    f.src = `https://www.youtube-nocookie.com/embed/${v.id}?autoplay=1&rel=0&playsinline=1`;
    f.title = `Día ${v.dia} de ${total} operando con Bitget`;
    f.allow = 'autoplay; encrypted-media; picture-in-picture';
    f.allowFullscreen = true;
    tarjeta.appendChild(f);
    reproduciendo = { nodo: tarjeta, v, esUltimo, total };
  }
  async function cargarSerie() {
    const pista = $('#serie-track');
    if (!pista) return;
    let datos;
    try {
      const r = await fetch('./data/serie-bitget.json', { cache: 'no-cache' });
      if (!r.ok) throw new Error('HTTP ' + r.status);
      datos = await r.json();
    } catch (_) {
      pista.appendChild(el('div', 'serie-empty', 'Los videos del reto no están disponibles por ahora. Míralos en nuestro canal de YouTube.'));
      pista.style.display = 'block';
      return;
    }
    const total = Number(datos.total) || 33;
    const videos = (datos.videos || [])
      .filter(v => Number.isInteger(v.dia) && ID_VIDEO.test(v.id || ''))
      .sort((a, b) => b.dia - a.dia);
    if (!videos.length) { pista.appendChild(el('div', 'serie-empty', 'Muy pronto: el primer video del reto.')); pista.style.display = 'block'; return; }

    const ultimo = videos[0].dia;
    $('#serie-dia').textContent = `Día ${ultimo} `;
    $('#serie-dia').appendChild(el('small', '', `de ${total}`));
    $('#serie-pct').textContent = `${Math.min(100, Math.round((ultimo / total) * 100))} % del reto`;
    $('#serie-progress').hidden = false;
    requestAnimationFrame(() => { $('#serie-bar').style.width = Math.min(100, (ultimo / total) * 100) + '%'; });

    videos.forEach((v, i) => pista.appendChild(tarjetaShort(v, i === 0, total)));
    const paso = () => Math.max(200, pista.clientWidth * 0.8);
    $('#serie-prev').addEventListener('click', () => pista.scrollBy({ left: -paso(), behavior: 'smooth' }));
    $('#serie-next').addEventListener('click', () => pista.scrollBy({ left: paso(), behavior: 'smooth' }));
  }

  // ───────────────────────── Noticias del día ─────────────────────────
  let noticias = null;
  let categoriaNoticias = 'mercados';

  function hace(iso) {
    const t = Date.parse(iso);
    if (isNaN(t)) return '';
    const min = Math.max(0, Math.round((Date.now() - t) / 60000));
    if (min < 1) return 'ahora';
    if (min < 60) return `hace ${min} min`;
    const h = Math.round(min / 60);
    if (h < 24) return `hace ${h} h`;
    return `hace ${Math.round(h / 24)} d`;
  }
  function tarjetaNoticia(n) {
    const a = el('a', 'news');
    a.href = n.enlace; a.target = '_blank'; a.rel = 'noopener noreferrer';
    const meta = el('div', 'news-meta');
    const clase = ['bitget', 'okx'].includes(String(n.fuente).toLowerCase()) ? ' ' + String(n.fuente).toLowerCase() : '';
    const origen = el('span', 'news-src' + clase);
    if (clase === ' bitget') origen.appendChild(logoBitget());     // lo que llega de Bitget lleva su logo
    origen.appendChild(document.createTextNode(n.fuente));
    meta.append(origen, el('span', '', hace(n.fecha)));
    a.append(meta, el('h4', '', n.titulo), el('span', 'go', 'Leer →'));
    return a;
  }
  function pintarNoticias() {
    const grid = $('#news-grid');
    if (!grid) return;
    grid.textContent = '';
    const items = ((noticias && noticias[categoriaNoticias]) || []).filter(n => /^https?:\/\//.test(n.enlace || ''));
    if (!items.length) {
      grid.appendChild(el('div', 'news-empty', noticias
        ? 'Aún no hay noticias en esta categoría. Vuelve en unos minutos.'
        : 'Las noticias no están disponibles ahora mismo. Mientras tanto, consulta las fuentes de abajo.'));
      return;
    }
    items.slice(0, 9).forEach(n => grid.appendChild(tarjetaNoticia(n)));
  }
  async function cargarNoticias() {
    const tabs = $('#news-tabs');
    if (!tabs) return;
    tabs.addEventListener('click', e => {
      const b = e.target.closest('button'); if (!b) return;
      categoriaNoticias = b.dataset.cat;
      tabs.querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
      pintarNoticias();
    });
    try {
      const r = await fetch('./data/noticias.json', { cache: 'no-cache' });
      if (!r.ok) throw new Error('HTTP ' + r.status);
      noticias = await r.json();
      const upd = $('#news-upd');
      if (upd && noticias.generado) upd.textContent = 'Actualizado ' + hace(noticias.generado);
    } catch (_) { noticias = null; }
    pintarNoticias();
  }

  // ───────────────────────── Inicio ─────────────────────────
  function iniciar() {
    iniciarTerminal();
    revisarDirecto();
    setInterval(revisarDirecto, 60000);
    document.addEventListener('visibilitychange', () => { if (!document.hidden) revisarDirecto(); });
    cargarSerie();
    cargarNoticias();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();
})();
