// Pure helpers for the profile page (web/profile.html, Issue #85, wireframe 1e).
// They take and return plain values (no DOM, no fetch), so profile-utils.test.js runs them
// under `node --test`. Same loading pattern as search-utils.js: window.ProfileUtils in the
// browser, module.exports under Node. search-utils.js and upload-utils.js load first.
(function (exportTo) {
  const node = typeof module !== 'undefined' && module.exports;
  const { escapeHtml, ratingSummary, errorMessage } = node ? require('./search-utils.js') : exportTo.SearchUtils;
  const { REQUIRED_FIELDS, OPTIONAL_FIELDS } = node ? require('./upload-utils.js') : exportTo.UploadUtils;

  const EDIT_FIELDS = [...REQUIRED_FIELDS, ...OPTIONAL_FIELDS];

  function count(value) {
    return Number(value) || 0;
  }

  // summary of GET /notes/mine -> the stat cards at the top of the page. Counts every note
  // of the user, not only the page of notes that was loaded.
  function summaryCards(summary) {
    const s = summary || {};
    const ratings = count(s.rating_count);
    const average = Number(s.average_rating);
    return [
      { key: 'notes', label: 'โน้ตที่แบ่งปัน', value: String(count(s.note_count)) },
      {
        key: 'rating',
        label: ratings ? `คะแนนเฉลี่ย (${ratings} คะแนน)` : 'คะแนนเฉลี่ย',
        value: ratings && Number.isFinite(average) ? average.toFixed(1) : '–',
      },
      { key: 'downloads', label: 'ดาวน์โหลด', value: String(count(s.total_downloads)) },
      { key: 'views', label: 'เปิดดู', value: String(count(s.total_views)) },
      { key: 'thanks', label: 'คำขอบคุณ', value: String(count(s.total_thanks)) },
    ];
  }

  function noteLink(note) {
    return `<a class="note-link" href="/note.html?id=${encodeURIComponent(note.id)}">${escapeHtml(note.title)}</a>`;
  }

  function subjectLine(note) {
    return [note.subject_code, note.subject_name, note.lesson].filter(Boolean).join(' · ');
  }

  // One of the user's own notes, with edit and delete. Titles are typed in by users, so every
  // value goes through escapeHtml.
  function renderMyNoteRow(note) {
    const id = escapeHtml(note.id);
    return `<li class="profile-row" data-note-id="${id}">
  <div class="profile-row-main">
    <h3 class="profile-row-title">${noteLink(note)}</h3>
    <p class="note-sub">${escapeHtml(subjectLine(note))}</p>
    <p class="profile-row-stats">${escapeHtml(ratingSummary(note))} · ดาวน์โหลด ${count(note.download_count)} · เปิดดู ${count(note.view_count)} · ขอบคุณ ${count(note.thank_count)}</p>
  </div>
  <div class="profile-row-actions">
    <button type="button" class="secondary-btn" data-edit-note="${id}">แก้ไข</button>
    <button type="button" class="secondary-btn danger-btn" data-delete-note="${id}">ลบ</button>
  </div>
</li>`;
  }

  function renderFavoriteRow(note) {
    const id = escapeHtml(note.id);
    return `<li class="profile-row" data-note-id="${id}">
  <div class="profile-row-main">
    <h3 class="profile-row-title">${noteLink(note)}</h3>
    <p class="note-sub">${escapeHtml(subjectLine(note))} · อัปโหลดโดย ${escapeHtml(note.uploader_name)}</p>
    <p class="profile-row-stats">${escapeHtml(ratingSummary(note))}</p>
  </div>
  <div class="profile-row-actions">
    <button type="button" class="secondary-btn" data-unfavorite="${id}">เอาออกจากรายการโปรด</button>
  </div>
</li>`;
  }

  // A note from the API -> the values its edit form starts with (all strings, '' for empty).
  function editFormValues(note) {
    const values = {};
    for (const name of EDIT_FIELDS) {
      const value = note[name];
      values[name] = value === null || value === undefined ? '' : String(value);
    }
    return values;
  }

  // Only the fields the user changed, trimmed, for PATCH /notes/<id> (US-19 is a partial
  // update). A cleared optional field is sent as '' because that is how the API clears it.
  function changedFields(note, fields) {
    const before = editFormValues(note);
    const changed = {};
    for (const name of EDIT_FIELDS) {
      const after = String(fields[name] ?? '').trim();
      if (after !== before[name].trim()) changed[name] = after;
    }
    return changed;
  }

  // Errors of PATCH/DELETE /notes/<id> and the favorites call -> one line for the page.
  function profileErrorMessage(status, body) {
    const code = body && body.error;
    if (code === 'validation_failed') return 'ข้อมูลยังไม่ถูกต้อง แก้ช่องที่มีข้อความสีแดงแล้วลองใหม่';
    if (code === 'no_fields_to_update') return 'ยังไม่ได้แก้ข้อมูลช่องใด';
    if (code === 'forbidden') return 'แก้หรือลบได้เฉพาะโน้ตที่คุณอัปโหลด';
    if (code === 'unauthorized') return 'เซสชันหมดอายุหรือออกจากระบบไปแล้ว กรุณาเข้าสู่ระบบใหม่';
    if (code === 'auth_unavailable') return 'ระบบยืนยันตัวตนไม่พร้อมใช้งานตอนนี้ ลองใหม่อีกสักครู่';
    return errorMessage(status, body);
  }

  const ProfileUtils = {
    EDIT_FIELDS,
    summaryCards,
    renderMyNoteRow,
    renderFavoriteRow,
    editFormValues,
    changedFields,
    profileErrorMessage,
  };

  if (node) {
    module.exports = ProfileUtils;
  } else {
    exportTo.ProfileUtils = ProfileUtils;
  }
})(typeof window !== 'undefined' ? window : globalThis);
