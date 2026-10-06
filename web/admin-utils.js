// Pure helpers for the admin report review page (web/admin.html, Issues #17, #18).
// They take and return plain values (no DOM, no fetch), so admin-utils.test.js runs them
// under `node --test`. Same loading pattern as search-utils.js: window.AdminUtils in the
// browser, module.exports under Node. search-utils.js and note-utils.js load first.
(function (exportTo) {
  const node = typeof module !== 'undefined' && module.exports;
  const { escapeHtml, errorMessage } = node ? require('./search-utils.js') : exportTo.SearchUtils;
  const { noteUrl, formatThaiDateTime } = node ? require('./note-utils.js') : exportTo.NoteUtils;

  // GET /reports returns one item per report, newest first, each with its note. The page
  // shows one card per note so an admin sees every reason before deciding, in the order of
  // each note's newest report.
  function groupReports(reports) {
    const groups = new Map();
    for (const report of Array.isArray(reports) ? reports : []) {
      if (!report || !report.note) continue;
      const key = String(report.note_id);
      if (!groups.has(key)) groups.set(key, { note: report.note, reports: [] });
      const { note, ...rest } = report;
      groups.get(key).reports.push(rest);
    }
    return [...groups.values()];
  }

  // After "dismiss": the report is gone, and a note with no reports left drops off the list.
  function withoutReport(groups, reportId) {
    return groups
      .map((group) => ({ ...group, reports: group.reports.filter((r) => String(r.id) !== String(reportId)) }))
      .filter((group) => group.reports.length > 0);
  }

  // After "delete note": the service removes the note and all of its reports.
  function withoutNote(groups, noteId) {
    return groups.filter((group) => String(group.note.id) !== String(noteId));
  }

  function reportCount(groups) {
    return groups.reduce((total, group) => total + group.reports.length, 0);
  }

  function summaryLine(groups) {
    if (!groups.length) return 'ไม่มีรายงานที่รอตรวจ';
    return `รายงานที่รอตรวจ ${reportCount(groups)} รายการ จาก ${groups.length} โน้ต`;
  }

  // One reported note with every report on it. Titles, names and reasons are typed in by
  // users, so every value goes through escapeHtml.
  function renderReportGroup(group) {
    const note = group.note;
    const noteId = escapeHtml(note.id);
    const subject = [note.subject_code, note.subject_name, note.lesson].filter(Boolean).join(' · ');
    const items = group.reports
      .map(
        (report) => `<li class="report-item">
      <p class="comment-head"><strong>${escapeHtml(report.reporter_name)}</strong>
        <span class="comment-time">${escapeHtml(formatThaiDateTime(report.created_at))}</span>
        <button type="button" class="link-btn" data-dismiss-report="${escapeHtml(report.id)}">ยกเลิกรายงานนี้</button></p>
      <p class="comment-text">${escapeHtml(report.reason)}</p>
    </li>`
      )
      .join('');
    return `<li class="profile-row report-group" data-note-id="${noteId}">
  <div class="profile-row-main">
    <h3 class="profile-row-title"><a class="note-link" href="${escapeHtml(noteUrl(note.id))}">${escapeHtml(note.title)}</a></h3>
    <p class="note-sub">${escapeHtml(subject)} · อัปโหลดโดย ${escapeHtml(note.uploader_name)}</p>
    <p class="profile-row-stats">ถูกรายงาน ${group.reports.length} ครั้ง</p>
    <ul class="report-list">
    ${items}
    </ul>
  </div>
  <div class="profile-row-actions">
    <button type="button" class="secondary-btn danger-btn" data-remove-note="${noteId}">ลบโน้ตนี้</button>
  </div>
</li>`;
  }

  // Errors of GET /reports and the two DELETE calls -> one line for the page.
  function adminErrorMessage(status, body) {
    const code = body && body.error;
    if (code === 'forbidden') return 'หน้านี้สำหรับผู้ดูแลระบบเท่านั้น บัญชีนี้ไม่มีสิทธิ์ตรวจรายงาน';
    if (code === 'unauthorized') return 'เซสชันหมดอายุหรือออกจากระบบไปแล้ว กรุณาเข้าสู่ระบบใหม่';
    if (code === 'auth_unavailable') return 'ระบบยืนยันตัวตนไม่พร้อมใช้งานตอนนี้ ลองใหม่อีกสักครู่';
    if (code === 'not_found') return 'รายงานหรือโน้ตนี้ถูกจัดการไปแล้ว';
    return errorMessage(status, body);
  }

  const AdminUtils = {
    groupReports,
    withoutReport,
    withoutNote,
    reportCount,
    summaryLine,
    renderReportGroup,
    adminErrorMessage,
  };

  if (node) {
    module.exports = AdminUtils;
  } else {
    exportTo.AdminUtils = AdminUtils;
  }
})(typeof window !== 'undefined' ? window : globalThis);
