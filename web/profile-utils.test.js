const test = require('node:test');
const assert = require('node:assert/strict');
const {
  EDIT_FIELDS,
  summaryCards,
  renderMyNoteRow,
  renderFavoriteRow,
  editFormValues,
  changedFields,
  profileErrorMessage,
} = require('./profile-utils.js');

const myNote = {
  id: 7,
  title: 'Linked List สรุป',
  subject_name: 'Data Structures',
  subject_code: 'CS201',
  faculty: 'ICT',
  year_level: 2,
  lesson: 'Linked List',
  topic: null,
  class_date: '2026-08-20',
  description: null,
  uploader_name: 'Somchai',
  average_rating: 4.25,
  rating_count: 4,
  download_count: 3,
  view_count: 12,
  thank_count: 2,
};

test('summaryCards shows every total from GET /notes/mine', () => {
  const cards = summaryCards({
    note_count: 3,
    total_views: 40,
    total_downloads: 9,
    total_thanks: 2,
    average_rating: 4.33,
    rating_count: 6,
  });
  assert.deepEqual(
    cards.map((c) => [c.key, c.value]),
    [['notes', '3'], ['rating', '4.3'], ['downloads', '9'], ['views', '40'], ['thanks', '2']]
  );
  assert.equal(cards[1].label, 'คะแนนเฉลี่ย (6 คะแนน)');
});

test('summaryCards handles a user with no notes or no ratings', () => {
  const cards = summaryCards({ note_count: 0, average_rating: null, rating_count: 0 });
  assert.deepEqual(cards.map((c) => c.value), ['0', '–', '0', '0', '0']);
  assert.equal(cards[1].label, 'คะแนนเฉลี่ย');
  assert.deepEqual(summaryCards(undefined).map((c) => c.value), ['0', '–', '0', '0', '0']);
});

test('renderMyNoteRow links to the note page and offers edit and delete', () => {
  const html = renderMyNoteRow(myNote);
  assert.match(html, /<a class="note-link" href="\/note\.html\?id=7">Linked List สรุป<\/a>/);
  assert.match(html, /<a class="secondary-btn" href="\/stats\.html\?id=7">สถิติ<\/a>/);
  assert.match(html, /data-edit-note="7"/);
  assert.match(html, /data-delete-note="7"/);
  assert.match(html, /CS201 · Data Structures · Linked List/);
  assert.match(html, /เฉลี่ย 4\.3 \/ 5 \(4\) · ดาวน์โหลด 3 · เปิดดู 12 · ขอบคุณ 2/);
});

test('renderFavoriteRow names the uploader and offers only removal', () => {
  const html = renderFavoriteRow({ ...myNote, uploader_name: 'Kittamet' });
  assert.match(html, /อัปโหลดโดย Kittamet/);
  assert.match(html, /data-unfavorite="7"/);
  assert.doesNotMatch(html, /data-edit-note|data-delete-note/);
});

test('profile rows escape values typed in by users', () => {
  const evil = { ...myNote, title: '<img src=x onerror=alert(1)>', uploader_name: '<b>x</b>' };
  for (const html of [renderMyNoteRow(evil), renderFavoriteRow(evil)]) {
    assert.doesNotMatch(html, /<img|<b>/);
    assert.match(html, /&lt;img/);
  }
});

test('editFormValues fills every edit field with text, empty for missing values', () => {
  const values = editFormValues(myNote);
  assert.deepEqual(Object.keys(values), EDIT_FIELDS);
  assert.equal(values.year_level, '2');
  assert.equal(values.topic, '');
  assert.equal(values.description, '');
  assert.equal(values.class_date, '2026-08-20');
});

test('changedFields sends only what the user changed, trimmed (US-19 partial update)', () => {
  const fields = { ...editFormValues(myNote), title: '  Linked List ฉบับใหม่ ', topic: 'Pointers' };
  assert.deepEqual(changedFields(myNote, fields), { title: 'Linked List ฉบับใหม่', topic: 'Pointers' });
  assert.deepEqual(changedFields(myNote, editFormValues(myNote)), {});
  // whitespace only around the same text is not a change
  assert.deepEqual(changedFields(myNote, { ...editFormValues(myNote), lesson: ' Linked List ' }), {});
});

test('changedFields sends "" for a cleared optional field, which the API clears', () => {
  assert.deepEqual(changedFields(myNote, { ...editFormValues(myNote), class_date: '' }), { class_date: '' });
});

test('profileErrorMessage covers PATCH/DELETE errors', () => {
  assert.match(profileErrorMessage(400, { error: 'validation_failed', fields: {} }), /สีแดง/);
  assert.match(profileErrorMessage(400, { error: 'no_fields_to_update' }), /ยังไม่ได้แก้/);
  assert.match(profileErrorMessage(403, { error: 'forbidden' }), /เฉพาะโน้ตที่คุณอัปโหลด/);
  assert.match(profileErrorMessage(401, { error: 'unauthorized' }), /เข้าสู่ระบบใหม่/);
  assert.match(profileErrorMessage(503, { error: 'auth_unavailable' }), /ไม่พร้อมใช้งาน/);
  assert.match(profileErrorMessage(404, { error: 'not_found' }), /ไม่พบโน้ตนี้แล้ว/);
  assert.match(profileErrorMessage(0, null), /เชื่อมต่อเซิร์ฟเวอร์ไม่ได้/);
});
