const test = require('node:test');
const assert = require('node:assert/strict');
const {
  buildQuery,
  parseQuery,
  emptyFilters,
  escapeHtml,
  formatSize,
  fileTypeLabel,
  ratingSummary,
  starBar,
  renderNoteCard,
  errorMessage,
  hasMore,
  PAGE_SIZE,
} = require('./search-utils.js');

const sampleNote = {
  id: 7,
  title: 'Linked List สรุป',
  subject_name: 'Data Structures',
  subject_code: 'CS201',
  faculty: 'ICT',
  year_level: 2,
  lesson: 'Linked List',
  topic: 'Doubly linked',
  class_date: '2026-08-20',
  content_type: 'application/pdf',
  uploader_name: 'Somchai',
  download_count: 3,
  average_rating: 4.25,
  rating_count: 4,
  preview_url: '/notes/7/preview',
  download_url: '/notes/7/download',
};

test('buildQuery leaves out empty fields and the default sort', () => {
  assert.equal(buildQuery(emptyFilters()), '');
  assert.equal(buildQuery({ ...emptyFilters(), q: '  ', faculty: '' }), '');
});

test('buildQuery trims text and keeps every API filter', () => {
  const query = buildQuery({
    ...emptyFilters(),
    q: ' CS201 ',
    faculty: 'ICT',
    year_level: '2',
    topic: 'tree',
    date_from: '2026-08-01',
    date_to: '2026-08-31',
    sort: 'title',
  });
  assert.equal(
    query,
    'q=CS201&faculty=ICT&year_level=2&topic=tree&date_from=2026-08-01&date_to=2026-08-31&sort=title'
  );
});

test('buildQuery repeats file_type for each selected type and drops unknown ones', () => {
  const query = buildQuery({ ...emptyFilters(), file_type: ['pdf', 'jpeg', 'png'] });
  assert.equal(query, 'file_type=pdf&file_type=png');
});

test('buildQuery adds paging only when asked', () => {
  assert.equal(buildQuery({ ...emptyFilters(), q: 'x' }, { limit: 20, offset: 0 }), 'q=x&limit=20');
  assert.equal(buildQuery(emptyFilters(), { limit: 20, offset: 40 }), 'limit=20&offset=40');
});

test('parseQuery reverses buildQuery', () => {
  const filters = {
    ...emptyFilters(),
    q: 'graph',
    faculty: 'ICT',
    year_level: '3',
    file_type: ['jpg', 'pdf'],
    sort: 'class_date',
  };
  assert.deepEqual(parseQuery(buildQuery(filters)), filters);
});

test('parseQuery falls back to defaults for unknown sort and file types', () => {
  const filters = parseQuery('?sort=rating&file_type=docx&file_type=pdf&file_type=pdf');
  assert.equal(filters.sort, 'new');
  assert.deepEqual(filters.file_type, ['pdf']);
  assert.equal(filters.q, '');
});

test('escapeHtml escapes markup and treats null as empty', () => {
  assert.equal(escapeHtml('<img src=x onerror="a()">'), '&lt;img src=x onerror=&quot;a()&quot;&gt;');
  assert.equal(escapeHtml(null), '');
});

test('formatSize picks a readable unit', () => {
  assert.equal(formatSize(512), '512 B');
  assert.equal(formatSize(2048), '2.0 KB');
  assert.equal(formatSize(3 * 1024 * 1024), '3.0 MB');
});

test('fileTypeLabel names the three accepted types', () => {
  assert.equal(fileTypeLabel('application/pdf'), 'PDF');
  assert.equal(fileTypeLabel('image/jpeg'), 'JPG');
  assert.equal(fileTypeLabel('text/plain'), 'ไฟล์');
});

test('renderNoteCard always shows the uploader name (US-31 AC3)', () => {
  const html = renderNoteCard(sampleNote);
  assert.match(html, /อัปโหลดโดย <strong>Somchai<\/strong>/);
  assert.match(html, /data-preview-id="7"/);
  assert.match(html, /CS201 · Data Structures/);
  assert.match(html, /ดาวน์โหลด 3 ครั้ง/);
  assert.match(html, /เฉลี่ย 4\.3 \/ 5 \(4\)/);
});

test('renderNoteCard escapes values typed in by other users', () => {
  const html = renderNoteCard({
    ...sampleNote,
    title: '<script>alert(1)</script>',
    uploader_name: '"><img src=x>',
  });
  assert.doesNotMatch(html, /<script>/);
  assert.doesNotMatch(html, /<img/);
  assert.match(html, /&lt;script&gt;/);
});

test('renderNoteCard skips missing optional fields', () => {
  const html = renderNoteCard({ ...sampleNote, topic: null, class_date: null });
  assert.doesNotMatch(html, /null/);
  assert.doesNotMatch(html, /เรียนวันที่/);
});

test('ratingSummary handles notes without ratings and rounds for display', () => {
  assert.equal(ratingSummary({ average_rating: null, rating_count: 0 }), 'ยังไม่มีคะแนน');
  assert.equal(ratingSummary({ average_rating: 3.66, rating_count: 3 }), 'เฉลี่ย 3.7 / 5 (3)');
});

test('starBar fills stars up to the rounded average', () => {
  assert.equal(starBar({ average_rating: null, rating_count: 0 }), '☆☆☆☆☆');
  assert.equal(starBar({ average_rating: 4.3, rating_count: 4 }), '★★★★☆');
  assert.equal(starBar({ average_rating: 4.5, rating_count: 2 }), '★★★★★');
  assert.equal(starBar({ average_rating: 1, rating_count: 1 }), '★☆☆☆☆');
});

test('renderNoteCard shows the course tag and the stars', () => {
  const html = renderNoteCard(sampleNote);
  assert.match(html, /<span class="tag-course">CS201<\/span>/);
  assert.match(html, /<a class="note-link" href="\/note\.html\?id=7">Linked List สรุป<\/a>/);
  assert.match(html, /<span class="note-stars" aria-hidden="true">★★★★☆<\/span>/);
});

test('errorMessage names the field for invalid_filter', () => {
  assert.match(errorMessage(400, { error: 'invalid_filter', field: 'date_to' }), /วันที่สิ้นสุด/);
});

test('errorMessage covers preview, missing note and network failures', () => {
  assert.match(errorMessage(422, { error: 'preview_unavailable' }), /ภาพตัวอย่าง/);
  assert.match(errorMessage(404, { error: 'not_found' }), /ไม่พบโน้ต/);
  assert.match(errorMessage(0, null), /เชื่อมต่อ/);
  assert.match(errorMessage(502, null), /HTTP 502/);
});

test('hasMore is true only for a full page', () => {
  assert.equal(hasMore(PAGE_SIZE), true);
  assert.equal(hasMore(PAGE_SIZE - 1), false);
  assert.equal(hasMore(0), false);
});
