// =================================================================
//  CREEMOS CAPITAL — Promoción emergente (p. ej. Black Friday)
//  Se configura en data/promocion.json. Solo se muestra entre "desde" y "hasta"
//  (hora con zona horaria, ej. 2026-11-30T23:59:59-05:00) y se cierra sola al vencer.
//  Una promoción SIN fecha "hasta" válida nunca se muestra: así siempre caduca.
// =================================================================
(function () {
  'use strict';

  // Coordina con la alerta de noticias del día (main.js) para que no salgan dos ventanas a la vez.
  window.ccPromoEstado = 'cargando';
  function terminar() {
    window.ccPromoEstado = 'nada';
    if (window.__alertaNoticiasPendiente && typeof window.mostrarAlertaNoticias === 'function') {
      window.__alertaNoticiasPendiente = false;
      window.mostrarAlertaNoticias();
    }
  }

  const el = (tag, cls, text) => {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  };
  const urlSegura = u => typeof u === 'string' && (/^https:\/\//.test(u) || /^\.\/[\w./-]+$/.test(u));
  const dos = n => String(n).padStart(2, '0');

  function tiempoRestante(ms) {
    const s = Math.max(0, Math.floor(ms / 1000));
    const d = Math.floor(s / 86400), h = Math.floor((s % 86400) / 3600), m = Math.floor((s % 3600) / 60);
    return (d > 0 ? `${d} d ` : '') + `${dos(h)}:${dos(m)}:${dos(s % 60)}`;
  }

  async function copiar(texto, boton) {
    try {
      await navigator.clipboard.writeText(texto);
    } catch (_) {
      const t = document.createElement('textarea');           // respaldo para navegadores sin permiso de portapapeles
      t.value = texto; t.style.position = 'fixed'; t.style.opacity = '0';
      document.body.appendChild(t); t.select();
      try { document.execCommand('copy'); } catch (__) { /* sin copiar */ }
      t.remove();
    }
    const antes = boton.textContent;
    boton.textContent = '¡Código copiado!';
    setTimeout(() => { boton.textContent = antes; }, 1800);
  }

  function abrir(p, hasta) {
    window.ccPromoEstado = 'abierta';
    const foco = document.activeElement;

    const fondo = el('div', 'promo-overlay');
    fondo.setAttribute('role', 'dialog');
    fondo.setAttribute('aria-modal', 'true');
    fondo.setAttribute('aria-label', `${p.etiqueta || 'Promoción'}: ${p.titulo || ''}`);

    const tarjeta = el('div', 'promo-card');

    const cerrar = el('button', 'icon-btn promo-x');
    cerrar.type = 'button';
    cerrar.setAttribute('aria-label', 'Cerrar');
    cerrar.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>';

    const enlaceImg = el('a', 'promo-img');
    enlaceImg.href = p.enlace; enlaceImg.target = '_blank'; enlaceImg.rel = 'noopener noreferrer';
    if (urlSegura(p.imagen)) {
      const img = el('img');
      img.src = p.imagen; img.alt = p.alt || p.titulo || '';
      enlaceImg.appendChild(img);
    }

    const lado = el('div', 'promo-side');
    lado.append(el('span', 'tag', p.etiqueta || 'Promoción'));
    lado.append(el('h3', 'promo-title', p.titulo || ''));
    if (p.subtitulo) lado.append(el('p', 'promo-sub', p.subtitulo));
    if (Array.isArray(p.detalles) && p.detalles.length) {
      const ul = el('ul', 'promo-list');
      p.detalles.slice(0, 6).forEach(d => ul.appendChild(el('li', '', String(d))));
      lado.append(ul);
    }
    const cuenta = el('div', 'promo-count');
    const valor = el('b', 'num', tiempoRestante(hasta - Date.now()));
    cuenta.append(el('span', '', 'Termina en'), valor);
    lado.append(cuenta);

    if (p.codigo) {
      const caja = el('div', 'promo-code');
      caja.append(el('span', '', 'Código de descuento'));
      const fila = el('div', 'promo-code-row');
      fila.append(el('b', 'num', String(p.codigo)));
      const bCopiar = el('button', 'btn btn-ghost btn-sm', 'Copiar');
      bCopiar.type = 'button';
      bCopiar.addEventListener('click', () => copiar(String(p.codigo), bCopiar));
      fila.append(bCopiar);
      caja.append(fila);
      lado.append(caja);
    }
    const cta = el('a', 'btn btn-primary btn-block', (p.boton || 'Ver más') + ' ');
    cta.href = p.enlace; cta.target = '_blank'; cta.rel = 'noopener noreferrer';
    cta.append(el('span', 'arrow', '→'));
    lado.append(cta);
    const no = el('button', 'promo-no', 'Ahora no');
    no.type = 'button';
    lado.append(no);

    tarjeta.append(cerrar, enlaceImg, lado);
    fondo.append(tarjeta);
    document.body.appendChild(fondo);
    document.documentElement.style.overflow = 'hidden';
    requestAnimationFrame(() => fondo.classList.add('on'));
    cerrar.focus();

    let reloj = null;
    function cerrarPromo(recordar) {
      clearInterval(reloj);
      document.removeEventListener('keydown', teclas);
      if (recordar) { try { localStorage.setItem('cc-promo-' + p.id, String(Date.now())); } catch (_) { /* sin almacenamiento */ } }
      fondo.classList.remove('on');
      document.documentElement.style.overflow = '';
      setTimeout(() => fondo.remove(), 250);
      if (foco && foco.focus) foco.focus();
      terminar();
    }
    function teclas(e) {
      if (e.key === 'Escape') { cerrarPromo(true); return; }
      if (e.key !== 'Tab') return;                              // el foco se queda dentro de la ventana
      const f = [...tarjeta.querySelectorAll('a[href], button')].filter(x => !x.disabled);
      if (!f.length) return;
      const primero = f[0], ultimo = f[f.length - 1];
      if (e.shiftKey && document.activeElement === primero) { e.preventDefault(); ultimo.focus(); }
      else if (!e.shiftKey && document.activeElement === ultimo) { e.preventDefault(); primero.focus(); }
    }
    document.addEventListener('keydown', teclas);
    cerrar.addEventListener('click', () => cerrarPromo(true));
    no.addEventListener('click', () => cerrarPromo(true));
    fondo.addEventListener('click', e => { if (e.target === fondo) cerrarPromo(true); });

    // cuenta regresiva; al llegar a cero la promoción desaparece sola
    reloj = setInterval(() => {
      const falta = hasta - Date.now();
      if (falta <= 0) { cerrarPromo(false); return; }
      valor.textContent = tiempoRestante(falta);
    }, 1000);
  }

  async function iniciar() {
    let p;
    try {
      const r = await fetch('./data/promocion.json', { cache: 'no-cache' });
      if (!r.ok) return terminar();
      p = await r.json();
    } catch (_) { return terminar(); }

    const ahora = Date.now();
    const desde = p.desde ? Date.parse(p.desde) : 0;
    const hasta = Date.parse(p.hasta || '');
    const probando = /[?&]demo-promo\b/.test(location.search);
    if (!p || p.activa === false || !/^[\w-]{1,60}$/.test(p.id || '') || !urlSegura(p.enlace)) return terminar();
    if (!isFinite(hasta) || ahora >= hasta || (isFinite(desde) && ahora < desde)) return terminar();   // sin fecha de fin válida, no se muestra

    if (!probando) {
      try {
        const cerrada = Number(localStorage.getItem('cc-promo-' + p.id)) || 0;
        if (cerrada && ahora - cerrada < (Number(p.volverAMostrarHoras) || 12) * 3600 * 1000) return terminar();
      } catch (_) { /* sin almacenamiento: se muestra */ }
    }
    setTimeout(() => abrir(p, hasta), 900);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();
})();
