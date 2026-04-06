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
function renderSesiones() {
  const cont = document.getElementById('sesiones-grid');
  if (!cont) return;
  cont.innerHTML = SESIONES.map(s => `
    <div class="sesion-card">
      <span class="sesion-emoji">${s.emoji}</span>
      <span class="sesion-nombre">${s.nombre}</span>
      <span class="sesion-horario">${s.horario} hs</span>
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

// ── IDEAS DE TRADING ──────────────────────────────────────────
function ideaCard(idea) {
  const isLong = idea.direccion === 'LONG';
  const statusLabel = { activa: 'Activa', objetivo: '✓ Objetivo', stop: '✗ Stop' }[idea.status];
  const statusClass = { activa: 'status-activa', objetivo: 'status-objetivo', stop: 'status-stop' }[idea.status];
  return `
    <div class="idea-card">
      <div class="idea-header">
        <span class="idea-activo">${idea.activo}</span>
        <span class="idea-dir ${isLong ? 'long' : 'short'}">${idea.direccion}</span>
      </div>
      <p class="idea-desc">${idea.descripcion}</p>
      <div class="idea-niveles">
        <div class="nivel"><span class="nivel-label">Entrada</span><span class="nivel-val">${idea.entrada}</span></div>
        <div class="nivel"><span class="nivel-label">Objetivo</span><span class="nivel-val target">${idea.objetivo}</span></div>
        <div class="nivel"><span class="nivel-label">Stop</span><span class="nivel-val stop">${idea.stop}</span></div>
      </div>
      <div class="idea-footer">
        <span class="idea-fecha">${idea.fecha}</span>
        <span class="${statusClass}">${statusLabel}</span>
      </div>
    </div>
  `;
}

function renderIdeas() {
  const cont = document.getElementById('ideas-grid');
  if (cont) cont.innerHTML = IDEAS_TRADING.map(ideaCard).join('');
}

// ── PLAYERS DE YOUTUBE ────────────────────────────────────────
function renderPlayers() {
  const musica = document.getElementById('iframe-musica');
  if (musica)
    musica.src = `https://www.youtube.com/embed/${MUSICA_PRIMER_VIDEO_ID}?list=${MUSICA_PLAYLIST_ID}&rel=0`;

  const estrategia = document.getElementById('iframe-estrategia');
  if (estrategia)
    estrategia.src = `https://www.youtube.com/embed/${ESTRATEGIA_PRIMER_VIDEO_ID}?list=${ESTRATEGIA_PLAYLIST_ID}&rel=0`;
}

// ── INIT ──────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  renderSesiones();
  renderVideos();
  renderIdeas();
  renderPlayers();
});
