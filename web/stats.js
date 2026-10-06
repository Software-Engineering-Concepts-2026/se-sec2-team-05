// Stats page wiring (web/stats.html, Issue #16 + US-28 AC3): the site overview from
// GET /stats and, when logged in, each own note (GET /notes/mine) with its numbers from
// stats-service (GET /notes/<id>/stats). ?id= marks the note the profile page linked to.
// The pure parts live in stats-utils.js; this file only touches the DOM and fetch.
(function () {
  const { authHeaders, clearSession, loginUrl } = window.SessionUtils;
  const { PAGE_SIZE, hasMore } = window.SearchUtils;
  const { noteIdFromSearch } = window.NoteUtils;
  const { overviewCards, leaderboard, myRank, renderStatsRow, statsErrorMessage } = window.StatsUtils;
  const { storage, currentSession, fetchJson, renderNav } = window.Site;

  const byId = (id) => document.getElementById(id);
  const overviewError = byId('overviewError');
  const overviewList = byId('overviewCards');
  const myRankBox = byId('myRank');
  const leaderboardList = byId('leaderboard');
  const mineStatus = byId('mineStatus');
  const mineList = byId('mineList');
  const mineMore = byId('mineMore');

  const here = window.location.pathname + window.location.search;
  const selectedId = noteIdFromSearch(window.location.search);
  let session = currentSession();
  const notes = new Map();
  const states = new Map();
  let offset = 0;

  function say(el, message) {
    el.textContent = message || '';
    el.hidden = !message;
  }

  function askToLogin(message) {
    mineStatus.replaceChildren(message, ' ');
    const link = document.createElement('a');
    link.href = loginUrl(here);
    link.textContent = 'เข้าสู่ระบบ';
    mineStatus.append(link);
    mineStatus.hidden = false;
    mineList.innerHTML = '';
    mineMore.hidden = true;
  }

  // The token stopped working (logout in another tab, revoked): the personal part asks for a
  // login again, and the overview is drawn again without "คุณ" in it.
  function sessionEnded() {
    clearSession(storage());
    session = null;
    renderNav();
    askToLogin(statsErrorMessage(401, null));
    loadOverview();
  }

  // ---- Site overview (public) ----

  async function loadOverview() {
    const result = await fetchJson('/stats');
    overviewList.setAttribute('aria-busy', 'false');
    if (!result.ok || !result.body) {
      say(overviewError, statsErrorMessage(result.status, result.body));
      return;
    }
    overviewList.replaceChildren(
      ...overviewCards(result.body).map((card) => {
        const item = document.createElement('li');
        item.className = 'stat-card';
        const value = document.createElement('span');
        value.className = 'stat-num';
        value.textContent = card.value;
        const label = document.createElement('span');
        label.className = 'stat-label';
        label.textContent = card.label;
        item.append(value, label);
        return item;
      })
    );
    const rows = leaderboard(result.body, session);
    const items = rows.map((row) => {
      const item = document.createElement('li');
      if (row.isYou) item.className = 'is-you';
      item.textContent = `${row.label} · ดาวน์โหลด ${row.downloads} ครั้ง`;
      return item;
    });
    if (!items.length) {
      const empty = document.createElement('li');
      empty.textContent = 'ยังไม่มีโน้ต';
      items.push(empty);
    }
    leaderboardList.replaceChildren(...items);
    const rank = myRank(result.body, session);
    say(myRankBox, rank ? rank.text : '');
  }

  // ---- Own notes with numbers from stats-service ----

  function rowFor(id) {
    return mineList.querySelector(`[data-note-id="${CSS.escape(String(id))}"]`);
  }

  function renderRow(id) {
    const html = renderStatsRow(notes.get(id), states.get(id), id === String(selectedId));
    const row = rowFor(id);
    if (row) row.outerHTML = html;
    else mineList.insertAdjacentHTML('beforeend', html);
  }

  async function loadStats(id) {
    const result = await fetchJson(`/notes/${encodeURIComponent(id)}/stats`, { headers: authHeaders(session) });
    if (!session) return;
    if (result.status === 401) {
      sessionEnded();
      return;
    }
    states.set(id, result.ok && result.body ? { stats: result.body } : { error: statsErrorMessage(result.status, result.body) });
    renderRow(id);
  }

  function addNote(note) {
    const id = String(note.id);
    if (notes.has(id)) {
      // the ?id= note was shown with a stand-in title before its page loaded
      notes.set(id, note);
      renderRow(id);
      return null;
    }
    notes.set(id, note);
    states.set(id, {});
    renderRow(id);
    return loadStats(id);
  }

  async function loadMine({ append = false } = {}) {
    if (!session) {
      askToLogin('เข้าสู่ระบบเพื่อดูสถิติโน้ตของคุณ');
      return;
    }
    const start = append ? offset : 0;
    mineMore.disabled = true;
    const result = await fetchJson(`/notes/mine?limit=${PAGE_SIZE}&offset=${start}`, { headers: authHeaders(session) });
    mineMore.disabled = false;
    if (result.status === 401) {
      sessionEnded();
      return;
    }
    if (!result.ok || !result.body || !Array.isArray(result.body.items)) {
      say(mineStatus, statsErrorMessage(result.status, result.body));
      return;
    }
    const items = result.body.items;
    offset = start + items.length;
    const loads = items.map(addNote);
    say(mineStatus, notes.size ? '' : 'ยังไม่ได้อัปโหลดโน้ต');
    // The profile page links every own note here, also ones past the first page. Show that
    // note on top even when it is not loaded yet; stats-service still checks ownership.
    if (!append && selectedId !== null && !notes.has(String(selectedId))) {
      notes.set(String(selectedId), { id: selectedId, title: `โน้ต #${selectedId}` });
      states.set(String(selectedId), {});
      mineList.insertAdjacentHTML('afterbegin', renderStatsRow(notes.get(String(selectedId)), {}, true));
      loads.push(loadStats(String(selectedId)));
    }
    mineMore.hidden = !hasMore(items.length);
    await Promise.all(loads);
    if (!append && selectedId !== null) {
      const row = rowFor(selectedId);
      if (row) row.scrollIntoView({ block: 'center' });
    }
  }

  mineMore.addEventListener('click', () => loadMine({ append: true }));

  loadOverview();
  loadMine();
})();
