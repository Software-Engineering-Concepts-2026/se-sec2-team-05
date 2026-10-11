// Pure helpers for the note detail page (web/note.html, Issue #85).
// They take and return plain values (no DOM, no fetch), so note-utils.test.js runs them
// under `node --test`. Storage is passed in, like session-utils.js.
// Same loading pattern as search-utils.js: window.NoteUtils in the browser, module.exports
// under Node. escapeHtml and errorMessage come from search-utils.js, which every page that
// uses this file loads first.
(function (exportTo) {
  const { escapeHtml, errorMessage } =
    typeof module !== 'undefined' && module.exports ? require('./search-utils.js') : exportTo.SearchUtils;

  // Same limits as services/notes-service/app.py (MAX_COMMENT_LENGTH, MAX_REPORT_REASON_LENGTH).
  const MAX_COMMENT_LENGTH = 1000;
  const MAX_REPORT_REASON_LENGTH = 500;

  // Notes downloaded in this tab, so the thanks button can wait until after a download
  // (US-28: the API does not check this, the page does). Kept per user in sessionStorage.
  const DOWNLOADED_KEY = 'noteshare.downloaded';
  const MAX_DOWNLOADED = 200;

  const THAI_MONTHS = ['ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.', 'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.'];
  const BANGKOK_OFFSET_MS = 7 * 60 * 60 * 1000;

  // ?id= -> note id, or null for anything that is not a plain positive whole number.
  function noteIdFromSearch(search) {
    const raw = new URLSearchParams(search).get('id');
    return raw && /^[1-9]\d{0,9}$/.test(raw) ? Number(raw) : null;
  }

  function noteUrl(id) {
    return `/note.html?id=${encodeURIComponent(id)}`;
  }

  // API timestamps are UTC. Shown in Thai time (UTC+7, no daylight saving) with the
  // Buddhist year, without relying on the browser's locale data.
  // On SQLite the service sends them without an offset ("2026-10-05T03:24:00"), which
  // Date.parse would read as the browser's local time, so a missing offset means UTC.
  function formatThaiDateTime(iso) {
    const text = String(iso ?? '');
    const hasZone = /(?:Z|[+-]\d{2}:?\d{2})$/i.test(text);
    const time = Date.parse(/T\d/.test(text) && !hasZone ? `${text}Z` : text);
    if (Number.isNaN(time)) return '';
    const local = new Date(time + BANGKOK_OFFSET_MS);
    const hh = String(local.getUTCHours()).padStart(2, '0');
    const mm = String(local.getUTCMinutes()).padStart(2, '0');
    return `${local.getUTCDate()} ${THAI_MONTHS[local.getUTCMonth()]} ${local.getUTCFullYear() + 543} ${hh}:${mm}`;
  }

  // The line under the title: who shared it, the subject, and how much it was used.
  function noteMetaLine(note) {
    const subject = [note.subject_code, note.subject_name].filter(Boolean).join(' ');
    return [
      `อัปโหลดโดย ${note.uploader_name}`,
      subject,
      `ดาวน์โหลด ${Number(note.download_count) || 0} ครั้ง`,
      `เปิดดู ${Number(note.view_count) || 0} ครั้ง`,
    ]
      .filter(Boolean)
      .join(' · ');
  }

  function noteTags(note) {
    return [
      note.faculty,
      note.year_level ? `ปี ${note.year_level}` : '',
      note.lesson,
      note.topic,
      note.class_date ? `เรียนวันที่ ${note.class_date}` : '',
    ].filter(Boolean);
  }

  function isOwnComment(comment, session) {
    return Boolean(session && session.user && comment && session.user.id === comment.user_id);
  }

  // "คุณ" for the viewer's own comments, else the author's display name. Comments posted
  // before the API kept author_name have none, so they still say "สมาชิก".
  function commentAuthor(comment, session) {
    if (isOwnComment(comment, session)) return 'คุณ';
    const name = comment && typeof comment.author_name === 'string' ? comment.author_name.trim() : '';
    return name || 'สมาชิก';
  }

  // One comment. The text and the author's name are typed in by other users, so both go
  // through escapeHtml.
  function renderComment(comment, session) {
    const own = isOwnComment(comment, session);
    const remove = own
      ? `<button type="button" class="link-btn" data-delete-comment="${escapeHtml(comment.id)}">ลบ</button>`
      : '';
    return `<li class="comment-item${own ? ' own' : ''}">
  <p class="comment-head"><strong>${escapeHtml(commentAuthor(comment, session))}</strong>
    <span class="comment-time">${escapeHtml(formatThaiDateTime(comment.created_at))}</span>${remove}</p>
  <p class="comment-text">${escapeHtml(comment.content)}</p>
</li>`;
  }

  // '' when the text can be sent, else the reason. Mirrors the API (trimmed, not empty,
  // max length) so a bad comment or report never leaves the page.
  function textProblem(value, max) {
    const text = String(value ?? '').trim();
    if (!text) return 'ต้องไม่ว่าง';
    if (text.length > max) return `ยาวเกิน ${max} ตัวอักษร`;
    return '';
  }

  function downloadKey(session, noteId) {
    return `${session.user.id}:${noteId}`;
  }

  function readDownloaded(storage) {
    try {
      const list = JSON.parse(storage.getItem(DOWNLOADED_KEY) || '[]');
      return Array.isArray(list) ? list.map(String) : [];
    } catch {
      return [];
    }
  }

  function markDownloaded(storage, session, noteId) {
    if (!session) return;
    const key = downloadKey(session, noteId);
    const list = readDownloaded(storage).filter((k) => k !== key);
    list.push(key);
    try {
      storage.setItem(DOWNLOADED_KEY, JSON.stringify(list.slice(-MAX_DOWNLOADED)));
    } catch {
      // storage off or full: the thanks button just waits for the next download
    }
  }

  function hasDownloaded(storage, session, noteId) {
    return Boolean(session) && readDownloaded(storage).includes(downloadKey(session, noteId));
  }

  // thank_status from GET /notes/<id> (null when not logged in) -> what the thanks box shows.
  // US-28: thank after downloading, never your own note, only once.
  function thanksView(thankStatus, downloaded) {
    if (thankStatus === 'own_note') return { state: 'own', message: 'นี่คือโน้ตของคุณ' };
    if (thankStatus === 'thanked') return { state: 'thanked', message: 'คุณขอบคุณเจ้าของโน้ตนี้แล้ว' };
    if (thankStatus !== 'can_thank') {
      return { state: 'login', message: 'เข้าสู่ระบบแล้วดาวน์โหลดโน้ต เพื่อขอบคุณเจ้าของโน้ต' };
    }
    if (!downloaded) return { state: 'need_download', message: 'ดาวน์โหลดโน้ตก่อน แล้วจึงขอบคุณเจ้าของได้' };
    return { state: 'ready', message: 'โน้ตนี้ช่วยคุณไหม? ส่งคำขอบคุณให้เจ้าของได้ครั้งเดียว' };
  }

  // API error from the detail page's actions -> one line for the page.
  function actionErrorMessage(status, body) {
    const code = body && body.error;
    if (code === 'unauthorized') return 'เซสชันหมดอายุหรือออกจากระบบไปแล้ว กรุณาเข้าสู่ระบบใหม่';
    if (code === 'auth_unavailable') return 'ระบบยืนยันตัวตนไม่พร้อมใช้งานตอนนี้ ลองใหม่อีกสักครู่';
    if (code === 'already_reported') return 'คุณรายงานโน้ตนี้ไปแล้ว ผู้ดูแลจะตรวจสอบให้';
    if (code === 'own_note') return 'ขอบคุณโน้ตของตัวเองไม่ได้';
    if (code === 'not_eligible') return 'เปิดหรือดาวน์โหลดโน้ตขณะเข้าสู่ระบบก่อนจึงจะให้คะแนนได้';
    if (code === 'forbidden') return 'คุณไม่มีสิทธิ์ทำรายการนี้';
    if (code === 'validation_failed') {
      const fields = (body && body.fields) || {};
      if (fields.content) return `ความคิดเห็นต้องไม่ว่างและยาวไม่เกิน ${MAX_COMMENT_LENGTH} ตัวอักษร`;
      if (fields.reason) return `เหตุผลต้องไม่ว่างและยาวไม่เกิน ${MAX_REPORT_REASON_LENGTH} ตัวอักษร`;
      if (fields.rating) return 'คะแนนต้องเป็น 1 ถึง 5 ดาว';
      return 'ข้อมูลยังไม่ถูกต้อง ลองใหม่อีกครั้ง';
    }
    return errorMessage(status, body);
  }

  const NoteUtils = {
    MAX_COMMENT_LENGTH,
    MAX_REPORT_REASON_LENGTH,
    DOWNLOADED_KEY,
    noteIdFromSearch,
    noteUrl,
    formatThaiDateTime,
    noteMetaLine,
    noteTags,
    commentAuthor,
    renderComment,
    textProblem,
    markDownloaded,
    hasDownloaded,
    thanksView,
    actionErrorMessage,
  };

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = NoteUtils;
  } else {
    exportTo.NoteUtils = NoteUtils;
  }
})(typeof window !== 'undefined' ? window : globalThis);
