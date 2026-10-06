// Pure helpers for the stats page (web/stats.html, Issue #16 + US-28 AC3).
// They take and return plain values (no DOM, no fetch), so stats-utils.test.js runs them
// under `node --test`. Same loading pattern as search-utils.js: window.StatsUtils in the
// browser, module.exports under Node. search-utils.js and note-utils.js load first.
(function (exportTo) {
  const node = typeof module !== 'undefined' && module.exports;
  const { escapeHtml, errorMessage } = node ? require('./search-utils.js') : exportTo.SearchUtils;
  const { noteUrl } = node ? require('./note-utils.js') : exportTo.NoteUtils;

  const LEADERBOARD_SIZE = 5;

  function count(value) {
    return Number(value) || 0;
  }

  // GET /stats -> the cards at the top. Public, so they work without a login.
  function overviewCards(stats) {
    const s = stats || {};
    const contributors = Array.isArray(s.top_contributors) ? s.top_contributors.length : 0;
    return [
      { key: 'notes', label: 'โน้ตทั้งหมด', value: String(count(s.total_notes)) },
      { key: 'downloads', label: 'ดาวน์โหลดทั้งหมด', value: String(count(s.total_downloads)) },
      { key: 'contributors', label: 'ผู้แบ่งปัน', value: String(contributors) },
    ];
  }

  // top_contributors (already sorted by downloads) -> the first few places. The API gives only
  // owner_id, no names, so the page says "คุณ" for the viewer and "สมาชิก" for everyone else
  // instead of showing other people's account numbers.
  function leaderboard(stats, session, size = LEADERBOARD_SIZE) {
    const list = stats && Array.isArray(stats.top_contributors) ? stats.top_contributors : [];
    const me = session && session.user ? session.user.id : null;
    return list.slice(0, size).map((entry, index) => {
      const isYou = entry.owner_id === me;
      return { rank: index + 1, label: isYou ? 'คุณ' : 'สมาชิก', downloads: count(entry.total_downloads), isYou };
    });
  }

  // Where the viewer stands among everyone who shared a note, or null when they have not
  // shared any (or are not logged in).
  function myRank(stats, session) {
    const list = stats && Array.isArray(stats.top_contributors) ? stats.top_contributors : [];
    const me = session && session.user ? session.user.id : null;
    if (me === null) return null;
    const index = list.findIndex((entry) => entry.owner_id === me);
    if (index < 0) return null;
    const downloads = count(list[index].total_downloads);
    return {
      rank: index + 1,
      total: list.length,
      downloads,
      text: `คุณอยู่อันดับ ${index + 1} จาก ${list.length} ผู้แบ่งปัน (ดาวน์โหลดรวม ${downloads} ครั้ง)`,
    };
  }

  // GET /notes/<id>/stats of stats-service -> one line. Views and downloads stay separate
  // (Issue #16 AC2), and thanks is only a count (US-28 AC3).
  function statsLine(stats) {
    return `เปิดดู ${count(stats.views)} · ดาวน์โหลด ${count(stats.downloads)} · ขอบคุณ ${count(stats.thanks)}`;
  }

  // One of the viewer's notes with its numbers from stats-service. `state` is
  // {stats} when loaded, {error} when that call failed, or {} while it is loading.
  // Titles are typed in by users, so every value goes through escapeHtml.
  function renderStatsRow(note, state, selected = false) {
    const id = escapeHtml(note.id);
    const s = state || {};
    let line = 'กำลังโหลดสถิติ…';
    if (s.stats) line = statsLine(s.stats);
    else if (s.error) line = s.error;
    const subject = [note.subject_code, note.subject_name, note.lesson].filter(Boolean).join(' · ');
    return `<li class="profile-row${selected ? ' is-selected' : ''}" data-note-id="${id}"${selected ? ' aria-current="true"' : ''}>
  <div class="profile-row-main">
    <h3 class="profile-row-title"><a class="note-link" href="${escapeHtml(noteUrl(note.id))}">${escapeHtml(note.title)}</a></h3>
    <p class="note-sub">${escapeHtml(subject)}</p>
    <p class="profile-row-stats${s.error ? ' stats-error' : ''}">${escapeHtml(line)}</p>
  </div>
</li>`;
  }

  // stats-service answers errors with its own messages (not the codes notes-service uses),
  // so go by status. 404 keeps the shared "note is gone" text.
  function statsErrorMessage(status, body) {
    if (status === 401) return 'เซสชันหมดอายุหรือออกจากระบบไปแล้ว กรุณาเข้าสู่ระบบใหม่';
    if (status === 403) return 'ดูสถิติได้เฉพาะโน้ตที่คุณอัปโหลด';
    if (status === 503) return 'ระบบยืนยันตัวตนไม่พร้อมใช้งานตอนนี้ ลองใหม่อีกสักครู่';
    return errorMessage(status, body);
  }

  const StatsUtils = {
    LEADERBOARD_SIZE,
    overviewCards,
    leaderboard,
    myRank,
    statsLine,
    renderStatsRow,
    statsErrorMessage,
  };

  if (node) {
    module.exports = StatsUtils;
  } else {
    exportTo.StatsUtils = StatsUtils;
  }
})(typeof window !== 'undefined' ? window : globalThis);
