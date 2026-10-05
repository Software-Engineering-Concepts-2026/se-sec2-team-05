const test = require('node:test');
const assert = require('node:assert/strict');
const {
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
} = require('./note-utils.js');

// Plain object standing in for sessionStorage, like session-utils.test.js.
function memoryStorage() {
  const data = new Map();
  return {
    getItem: (key) => (data.has(key) ? data.get(key) : null),
    setItem: (key, value) => data.set(key, String(value)),
    removeItem: (key) => data.delete(key),
  };
}

const alice = { token: 't', expiresAt: '2026-10-05T18:00:00Z', user: { id: 1, display_name: 'Alice' } };
const bob = { token: 'u', expiresAt: '2026-10-05T18:00:00Z', user: { id: 2, display_name: 'Bob' } };

const sampleNote = {
  id: 7,
  title: 'Linked List สรุป',
  subject_name: 'Data Structures',
  subject_code: 'CS201',
  faculty: 'ICT',
  year_level: 2,
  lesson: 'Linked List',
  topic: 'Pointers',
  class_date: '2026-08-20',
  uploader_name: 'Somchai',
  download_count: 3,
  view_count: 12,
};

test('noteIdFromSearch reads a plain positive id and rejects anything else', () => {
  assert.equal(noteIdFromSearch('?id=7'), 7);
  assert.equal(noteIdFromSearch('?q=x&id=120'), 120);
  for (const search of ['', '?id=', '?id=0', '?id=-3', '?id=7abc', '?id=1.5', '?id=%20 7', '?id=99999999999']) {
    assert.equal(noteIdFromSearch(search), null, search);
  }
});

test('noteUrl points at the detail page', () => {
  assert.equal(noteUrl(7), '/note.html?id=7');
});

test('formatThaiDateTime shows Thai time and the Buddhist year', () => {
  // 17:30 UTC = 00:30 the next day in Bangkok
  assert.equal(formatThaiDateTime('2026-10-04T17:30:00+00:00'), '5 ต.ค. 2569 00:30');
  assert.equal(formatThaiDateTime('2026-01-01T02:05:00Z'), '1 ม.ค. 2569 09:05');
  // SQLite gives no offset: still UTC, not the browser's local time. Run this part as if the
  // browser were in Thailand, or a CI machine on UTC would pass even without the fix.
  const savedTz = process.env.TZ;
  process.env.TZ = 'Asia/Bangkok';
  assert.equal(formatThaiDateTime('2026-10-05T03:24:10.123456'), '5 ต.ค. 2569 10:24');
  assert.equal(formatThaiDateTime('2026-10-05T03:24:10-02:00'), '5 ต.ค. 2569 12:24');
  if (savedTz === undefined) delete process.env.TZ;
  else process.env.TZ = savedTz;
  assert.equal(formatThaiDateTime('not a date'), '');
  assert.equal(formatThaiDateTime(null), '');
});

test('noteMetaLine names the uploader, the subject and the counts', () => {
  assert.equal(
    noteMetaLine(sampleNote),
    'อัปโหลดโดย Somchai · CS201 Data Structures · ดาวน์โหลด 3 ครั้ง · เปิดดู 12 ครั้ง'
  );
  assert.match(noteMetaLine({ ...sampleNote, download_count: null, view_count: undefined }), /ดาวน์โหลด 0 ครั้ง · เปิดดู 0 ครั้ง/);
});

test('noteTags skips empty optional fields', () => {
  assert.deepEqual(noteTags(sampleNote), ['ICT', 'ปี 2', 'Linked List', 'Pointers', 'เรียนวันที่ 2026-08-20']);
  assert.deepEqual(noteTags({ ...sampleNote, topic: null, class_date: null }), ['ICT', 'ปี 2', 'Linked List']);
});

test('commentAuthor says "คุณ" only for the viewer\'s own comments', () => {
  const comment = { id: 3, user_id: 1, content: 'ดีมาก' };
  assert.equal(commentAuthor(comment, alice), 'คุณ');
  assert.equal(commentAuthor(comment, bob), 'สมาชิก');
  assert.equal(commentAuthor(comment, null), 'สมาชิก');
});

test('renderComment offers delete only on the viewer\'s own comment', () => {
  const comment = { id: 3, user_id: 1, content: 'ดีมาก', created_at: '2026-10-04T03:00:00+00:00' };
  const own = renderComment(comment, alice);
  assert.match(own, /data-delete-comment="3"/);
  assert.match(own, /<strong>คุณ<\/strong>/);
  assert.match(own, /4 ต\.ค\. 2569 10:00/);
  assert.doesNotMatch(renderComment(comment, bob), /data-delete-comment/);
  assert.doesNotMatch(renderComment(comment, null), /data-delete-comment/);
});

test('renderComment escapes the comment text', () => {
  const html = renderComment({ id: 4, user_id: 2, content: '<img src=x onerror=alert(1)>' }, alice);
  assert.doesNotMatch(html, /<img/);
  assert.match(html, /&lt;img src=x onerror=alert\(1\)&gt;/);
});

test('textProblem uses the same rules as the API (trim, not empty, max length)', () => {
  assert.equal(textProblem('  ดีมาก  ', MAX_COMMENT_LENGTH), '');
  assert.equal(textProblem('   ', MAX_COMMENT_LENGTH), 'ต้องไม่ว่าง');
  assert.equal(textProblem(undefined, MAX_REPORT_REASON_LENGTH), 'ต้องไม่ว่าง');
  assert.equal(textProblem('ก'.repeat(1000), MAX_COMMENT_LENGTH), '');
  assert.equal(textProblem('ก'.repeat(1001), MAX_COMMENT_LENGTH), 'ยาวเกิน 1000 ตัวอักษร');
  assert.equal(textProblem(` ${'x'.repeat(500)} `, MAX_REPORT_REASON_LENGTH), '');
  assert.equal(textProblem('x'.repeat(501), MAX_REPORT_REASON_LENGTH), 'ยาวเกิน 500 ตัวอักษร');
});

test('markDownloaded remembers a download per user and per note', () => {
  const storage = memoryStorage();
  assert.equal(hasDownloaded(storage, alice, 7), false);
  markDownloaded(storage, alice, 7);
  markDownloaded(storage, alice, 7);
  assert.equal(hasDownloaded(storage, alice, 7), true);
  assert.equal(hasDownloaded(storage, alice, 8), false);
  assert.equal(hasDownloaded(storage, bob, 7), false);
  assert.equal(hasDownloaded(storage, null, 7), false);
  assert.deepEqual(JSON.parse(storage.getItem(DOWNLOADED_KEY)), ['1:7']);
});

test('markDownloaded survives broken or blocked storage', () => {
  const storage = memoryStorage();
  storage.setItem(DOWNLOADED_KEY, '{not json');
  assert.equal(hasDownloaded(storage, alice, 7), false);
  markDownloaded(storage, alice, 7);
  assert.equal(hasDownloaded(storage, alice, 7), true);

  const blocked = {
    getItem() {
      throw new Error('blocked');
    },
    setItem() {
      throw new Error('blocked');
    },
  };
  assert.doesNotThrow(() => markDownloaded(blocked, alice, 7));
  assert.equal(hasDownloaded(blocked, alice, 7), false);
});

test('markDownloaded keeps only the latest 200 downloads', () => {
  const storage = memoryStorage();
  for (let id = 1; id <= 205; id += 1) markDownloaded(storage, alice, id);
  assert.equal(JSON.parse(storage.getItem(DOWNLOADED_KEY)).length, 200);
  assert.equal(hasDownloaded(storage, alice, 5), false);
  assert.equal(hasDownloaded(storage, alice, 205), true);
});

test('thanksView shows the button only after a download, never for your own note (US-28)', () => {
  assert.equal(thanksView(null, false).state, 'login');
  assert.equal(thanksView(undefined, true).state, 'login');
  assert.equal(thanksView('own_note', true).state, 'own');
  assert.equal(thanksView('thanked', true).state, 'thanked');
  assert.equal(thanksView('can_thank', false).state, 'need_download');
  assert.equal(thanksView('can_thank', true).state, 'ready');
  assert.match(thanksView('can_thank', false).message, /ดาวน์โหลดโน้ตก่อน/);
});

test('actionErrorMessage covers the errors of every action on the page', () => {
  assert.match(actionErrorMessage(401, { error: 'unauthorized' }), /เข้าสู่ระบบใหม่/);
  assert.match(actionErrorMessage(503, { error: 'auth_unavailable' }), /ไม่พร้อมใช้งาน/);
  assert.match(actionErrorMessage(409, { error: 'already_reported' }), /รายงานโน้ตนี้ไปแล้ว/);
  assert.match(actionErrorMessage(403, { error: 'own_note' }), /โน้ตของตัวเอง/);
  assert.match(actionErrorMessage(403, { error: 'not_eligible' }), /ก่อนจึงจะให้คะแนนได้/);
  assert.match(actionErrorMessage(403, { error: 'forbidden' }), /ไม่มีสิทธิ์/);
  assert.match(actionErrorMessage(400, { error: 'validation_failed', fields: { content: 'x' } }), /ความคิดเห็น.*1000/);
  assert.match(actionErrorMessage(400, { error: 'validation_failed', fields: { reason: 'required' } }), /เหตุผล.*500/);
  assert.match(actionErrorMessage(400, { error: 'validation_failed', fields: { rating: 'x' } }), /1 ถึง 5/);
  // anything else falls back to the search page's messages
  assert.match(actionErrorMessage(404, { error: 'not_found' }), /ไม่พบโน้ตนี้แล้ว/);
  assert.match(actionErrorMessage(404, { error: 'file_not_found' }), /ไม่พบไฟล์/);
  assert.match(actionErrorMessage(0, null), /เชื่อมต่อเซิร์ฟเวอร์ไม่ได้/);
  assert.match(actionErrorMessage(500, null), /HTTP 500/);
});
