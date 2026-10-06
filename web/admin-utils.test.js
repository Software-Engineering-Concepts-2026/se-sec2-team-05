const test = require('node:test');
const assert = require('node:assert/strict');
const {
  groupReports,
  withoutReport,
  withoutNote,
  reportCount,
  summaryLine,
  renderReportGroup,
  adminErrorMessage,
} = require('./admin-utils.js');

const linkedList = { id: 7, title: 'Linked List สรุป', subject_code: 'CS201', subject_name: 'Data Structures', lesson: 'Linked List', uploader_name: 'Somchai' };
const sorting = { id: 9, title: 'Sorting', subject_code: 'CS301', subject_name: 'Algorithms', lesson: 'Sorting', uploader_name: 'Suda' };

// GET /reports order: newest report first
const reports = [
  { id: 5, note_id: 7, reporter_id: 3, reporter_name: 'Mana', reason: 'ไม่ตรงชื่อ', created_at: '2026-10-06T03:00:00+00:00', note: linkedList },
  { id: 4, note_id: 9, reporter_id: 2, reporter_name: 'Piti', reason: 'สแปม', created_at: '2026-10-05T03:00:00+00:00', note: sorting },
  { id: 2, note_id: 7, reporter_id: 2, reporter_name: 'Piti', reason: 'มีข้อมูลส่วนตัว', created_at: '2026-10-04T03:00:00+00:00', note: linkedList },
];

test('groupReports puts every report under its note, newest reported note first', () => {
  const groups = groupReports(reports);
  assert.deepEqual(groups.map((g) => g.note.id), [7, 9]);
  assert.deepEqual(groups[0].reports.map((r) => r.id), [5, 2]);
  assert.deepEqual(groups[1].reports.map((r) => r.id), [4]);
  // the note object is kept once per group, not copied into each report
  assert.equal(groups[0].reports[0].note, undefined);
  assert.equal(groups[0].note.title, 'Linked List สรุป');
});

test('groupReports copes with an empty or broken list', () => {
  assert.deepEqual(groupReports([]), []);
  assert.deepEqual(groupReports(undefined), []);
  assert.deepEqual(groupReports([null, { id: 1, note_id: 3 }]), []);
});

test('withoutReport drops one report and the note once no reports are left', () => {
  const groups = groupReports(reports);
  const afterOne = withoutReport(groups, 5);
  assert.deepEqual(afterOne.map((g) => g.note.id), [7, 9]);
  assert.deepEqual(afterOne[0].reports.map((r) => r.id), [2]);
  const afterTwo = withoutReport(afterOne, '2');
  assert.deepEqual(afterTwo.map((g) => g.note.id), [9]);
  // the old list is not changed in place
  assert.equal(groups[0].reports.length, 2);
});

test('withoutNote drops the note with all of its reports', () => {
  const groups = withoutNote(groupReports(reports), '7');
  assert.deepEqual(groups.map((g) => g.note.id), [9]);
  assert.equal(reportCount(groups), 1);
});

test('summaryLine counts reports and notes, or says nothing is waiting', () => {
  const groups = groupReports(reports);
  assert.equal(reportCount(groups), 3);
  assert.equal(summaryLine(groups), 'รายงานที่รอตรวจ 3 รายการ จาก 2 โน้ต');
  assert.equal(summaryLine([]), 'ไม่มีรายงานที่รอตรวจ');
});

test('renderReportGroup shows the note, every reason and both actions', () => {
  const html = renderReportGroup(groupReports(reports)[0]);
  assert.match(html, /href="\/note\.html\?id=7"/);
  assert.match(html, /CS201 · Data Structures · Linked List · อัปโหลดโดย Somchai/);
  assert.match(html, /ถูกรายงาน 2 ครั้ง/);
  assert.match(html, /ไม่ตรงชื่อ/);
  assert.match(html, /มีข้อมูลส่วนตัว/);
  assert.match(html, /data-dismiss-report="5"/);
  assert.match(html, /data-dismiss-report="2"/);
  assert.match(html, /data-remove-note="7"/);
  // report time in Thai time with the Buddhist year (03:00 UTC = 10:00 in Bangkok)
  assert.match(html, /6 ต\.ค\. 2569 10:00/);
});

test('renderReportGroup escapes values typed in by users', () => {
  const html = renderReportGroup(
    groupReports([
      {
        id: 1,
        note_id: 3,
        reporter_name: '<b>x</b>',
        reason: '<script>alert(1)</script>',
        created_at: null,
        note: { id: 3, title: '<img src=x onerror=alert(1)>', uploader_name: '"q"' },
      },
    ])[0]
  );
  assert.doesNotMatch(html, /<img|<script|<b>/);
  assert.match(html, /&lt;img src=x/);
  assert.match(html, /&lt;script&gt;/);
  assert.match(html, /&quot;q&quot;/);
});

test('adminErrorMessage covers the errors of the admin calls', () => {
  assert.match(adminErrorMessage(403, { error: 'forbidden' }), /ผู้ดูแลระบบเท่านั้น/);
  assert.match(adminErrorMessage(401, { error: 'unauthorized' }), /เข้าสู่ระบบใหม่/);
  assert.match(adminErrorMessage(503, { error: 'auth_unavailable' }), /ไม่พร้อมใช้งาน/);
  assert.match(adminErrorMessage(404, { error: 'not_found' }), /ถูกจัดการไปแล้ว/);
  assert.match(adminErrorMessage(0, null), /เชื่อมต่อเซิร์ฟเวอร์ไม่ได้/);
  assert.match(adminErrorMessage(500, null), /HTTP 500/);
});
