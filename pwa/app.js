const DATA_URL = './data/current.json';
let deferredInstallPrompt;
let waitingServiceWorker;
let payload = { meta: {}, matches: [], engines: [] };
let activeView = 'predictions';

const $ = (id) => document.getElementById(id);
const escapeHtml = (value = '') => String(value).replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
const unique = (items) => [...new Set(items.filter(Boolean))].sort();
const formatDate = (value) => value ? new Intl.DateTimeFormat('it-IT',{weekday:'short',day:'2-digit',month:'short'}).format(new Date(`${value}T12:00:00`)) : 'Oggi';

async function loadData() {
  $('statusMessage').hidden = true;
  try {
    const response = await fetch(`${DATA_URL}?v=${Date.now()}`, { cache: 'no-store' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    payload = await response.json();
    payload.matches ??= [];
    payload.engines ??= [];
    hydrateFilters();
    render();
  } catch (error) {
    $('statusMessage').textContent = `Dati non disponibili: ${error.message}. Riprova tra poco.`;
    $('statusMessage').hidden = false;
    payload = { meta: {}, matches: [], engines: [] };
    render();
  }
}

function hydrateFilters() {
  const dates = unique(payload.matches.map(x => x.match_date));
  const selectedDate = $('dateFilter').value || payload.meta.match_date || dates.at(-1) || '';
  $('dateFilter').innerHTML = dates.length ? dates.map(d => `<option value="${escapeHtml(d)}" ${d===selectedDate?'selected':''}>${escapeHtml(formatDate(d))}</option>`).join('') : '<option value="">Oggi</option>';
  const engines = unique([...payload.matches.map(x => x.engine), ...payload.engines.map(x => x.name)]);
  const currentEngine = $('engineFilter').value;
  $('engineFilter').innerHTML = '<option value="">Tutti</option>' + engines.map(e => `<option ${e===currentEngine?'selected':''}>${escapeHtml(e)}</option>`).join('');
}

function filteredMatches() {
  const date = $('dateFilter').value, engine = $('engineFilter').value, band = $('bandFilter').value;
  return payload.matches.filter(x => {
    const bandMatch = !band || x.band === band;
    return (!date || x.match_date === date) && (!engine || x.engine === engine) && bandMatch;
  });
}

function render() {
  const rows = filteredMatches();
  const resultRows = rows.filter(x => ['OK','KO'].includes(x.result));
  $('pageTitle').textContent = activeView === 'results' ? 'Risultati' : activeView === 'engines' ? 'Rendimento engine' : 'Partite di oggi';
  $('lastUpdate').textContent = payload.meta.updated_at ? `Ultimo aggiornamento: ${payload.meta.updated_at}` : 'In attesa della prima generazione automatica';
  $('matchesKpi').textContent = new Set(rows.map(x => `${x.match_date}|${x.league_id}|${x.home}|${x.away}`)).size;
  $('highKpi').textContent = rows.filter(x => x.band === 'ALTA').length;
  $('okKpi').textContent = resultRows.filter(x => x.result === 'OK').length;
  $('koKpi').textContent = resultRows.filter(x => x.result === 'KO').length;
  if (activeView === 'engines') return renderEngines();
  const visible = activeView === 'results' ? resultRows : rows;
  $('content').innerHTML = visible.length ? visible.map(renderMatch).join('') : '<div class="empty">Nessun dato disponibile per i filtri selezionati.</div>';
}

function renderMatch(m) {
  const bandClass = (m.band || 'BASSA').toLowerCase().replace(/[^a-z]/g,'');
  const result = m.result ? `<strong class="status-${m.result.toLowerCase()}">${escapeHtml(m.result)}</strong>` : '<span class="muted">Da giocare</span>';
  const finalScore = Number.isFinite(m.home_goals) && Number.isFinite(m.away_goals) ? `<span class="score">${m.home_goals}–${m.away_goals}</span>` : '';
  const prediction = Number.isFinite(m.score) ? `<span class="engine">Score ${Number(m.score).toFixed(1)}</span>` : '';
  return `<article class="match-card"><div class="card-top"><span class="league">${escapeHtml(m.league_id)}</span><span class="time">${escapeHtml(m.start_time || '—')}</span></div><div class="teams"><span>${escapeHtml(m.home)}</span><span class="versus">VS</span><span class="away">${escapeHtml(m.away)}</span></div><div class="card-bottom"><div><span class="pill ${bandClass}">${escapeHtml(m.band || '—')}</span> <span class="engine">${escapeHtml(m.engine || '')}</span> ${prediction}</div><div>${finalScore} ${result}</div></div></article>`;
}

function renderEngines() {
  const engines = [...payload.engines].sort((a,b) => (b.hit_rate || 0) - (a.hit_rate || 0));
  $('content').innerHTML = engines.length ? engines.map(e => `<article class="engine-card"><div><strong>${escapeHtml(e.name)}</strong><br><small>${e.ok || 0} OK · ${e.ko || 0} KO · ${e.total || 0} totali</small></div><strong class="${(e.hit_rate||0)>=80?'ok':''}">${Number(e.hit_rate||0).toFixed(1)}%</strong></article>`).join('') : '<div class="empty">Le statistiche degli engine compariranno dopo il primo aggiornamento.</div>';
}

document.querySelectorAll('.tabs button').forEach(button => button.addEventListener('click', () => { document.querySelectorAll('.tabs button').forEach(x => x.classList.remove('active')); button.classList.add('active'); activeView = button.dataset.view; render(); }));
['dateFilter','engineFilter','bandFilter'].forEach(id => $(id).addEventListener('change', render));
$('refreshButton').addEventListener('click', loadData);
window.addEventListener('beforeinstallprompt', event => { event.preventDefault(); deferredInstallPrompt = event; $('installButton').hidden = false; });
$('installButton').addEventListener('click', async () => { if (!deferredInstallPrompt) return; deferredInstallPrompt.prompt(); await deferredInstallPrompt.userChoice; deferredInstallPrompt = null; $('installButton').hidden = true; });
$('updateButton').addEventListener('click', () => {
  if (!waitingServiceWorker) return;
  $('updateButton').textContent = 'Aggiornamento…';
  $('updateButton').disabled = true;
  waitingServiceWorker.postMessage({ type: 'SKIP_WAITING' });
});
window.addEventListener('appinstalled', () => { $('installButton').hidden = true; });
if ('serviceWorker' in navigator) {
  let refreshing = false;
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    if (refreshing) return;
    refreshing = true;
    window.location.reload();
  });
  window.addEventListener('load', async () => {
    const registration = await navigator.serviceWorker.register('./sw.js');
    const offerUpdate = worker => {
      waitingServiceWorker = worker;
      $('updateButton').hidden = false;
    };
    if (registration.waiting && navigator.serviceWorker.controller) offerUpdate(registration.waiting);
    registration.addEventListener('updatefound', () => {
      const worker = registration.installing;
      if (!worker) return;
      worker.addEventListener('statechange', () => {
        if (worker.state === 'installed' && navigator.serviceWorker.controller) offerUpdate(worker);
      });
    });
    registration.update().catch(() => {});
  });
}
loadData();
