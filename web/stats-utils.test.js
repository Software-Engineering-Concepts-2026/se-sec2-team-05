const test = require('node:test');
const assert = require('node:assert/strict');
const {
  LEADERBOARD_SIZE,
  overviewCards,
  leaderboard,
  myRank,
  statsLine,
  renderStatsRow,
  statsErrorMessage,
} = require('./stats-utils.js');

// GET /stats of stats-service: contributors sorted by downloads (body without owner_name)
const siteStats = {
  total_downloads: 21,
  total_notes: 9,
  top_contributors: [
    { owner_id: 4, total_downloads: 12 },
    { owner_id: 2, total_downloads: 6 },
    { owner_id: 7, total_downloads: 2 },
    { owner_id: 8, total_downloads: 1 },
    { owner_id: 9, total_downloads: 0 },
    { owner_id: 3, total_downloads: 0 },
  ],
};
const session = { token: 't', user: { id: 2, display_name: 'Somchai' } };

test('overviewCards shows the site totals from GET /stats', () => {
  const cards = overviewCards(siteStats);
  assert.deepEqual(cards.map((c) => [c.key, c.value]), [
    ['notes', '9'],
    ['downloads', '21'],
    ['contributors', '6'],
  ]);
});

test('overviewCards shows zeros when the body is missing or empty', () => {
  for (const body of [null, {}, { top_contributors: 'x' }]) {
    assert.deepEqual(overviewCards(body).map((c) => c.value), ['0', '0', '0']);
  }
});

test('leaderboard lists the first places without other people\'s account numbers', () => {
  const rows = leaderboard(siteStats, session);
  assert.equal(rows.length, LEADERBOARD_SIZE);
  assert.deepEqual(rows[0], { rank: 1, label: 'สมาชิก', downloads: 12, isYou: false });
  assert.deepEqual(rows[1], { rank: 2, label: 'คุณ', downloads: 6, isYou: true });
  assert.ok(rows.every((r) => !('owner_id' in r)));
  // logged out: nobody is "you"
  assert.ok(leaderboard(siteStats, null).every((r) => r.label === 'สมาชิก'));
  assert.deepEqual(leaderboard({}, session), []);
});

test('leaderboard shows owner_name when GET /stats sends it', () => {
  const named = { top_contributors: [
    { owner_id: 4, owner_name: 'Mind', total_downloads: 12 },
    { owner_id: 2, owner_name: 'Somchai', total_downloads: 6 },
    { owner_id: 7, owner_name: '  ', total_downloads: 2 },
  ] };
  assert.deepEqual(leaderboard(named, session).map((r) => r.label), ['Mind', 'คุณ', 'สมาชิก']);
  assert.deepEqual(leaderboard(named, null).map((r) => r.label), ['Mind', 'Somchai', 'สมาชิก']);
});

test('myRank says where the viewer stands, or null when they have not shared', () => {
  assert.deepEqual(myRank(siteStats, session), {
    rank: 2,
    total: 6,
    downloads: 6,
    text: 'คุณอยู่อันดับ 2 จาก 6 ผู้แบ่งปัน (ดาวน์โหลดรวม 6 ครั้ง)',
  });
  // someone below the leaderboard cut still gets a rank
  assert.equal(myRank(siteStats, { user: { id: 3 } }).rank, 6);
  assert.equal(myRank(siteStats, { user: { id: 99 } }), null);
  assert.equal(myRank(siteStats, null), null);
});

test('statsLine keeps views and downloads apart and adds thanks (Issue #16, US-28 AC3)', () => {
  assert.equal(statsLine({ note_id: 7, views: 12, downloads: 3, thanks: 2 }), 'เปิดดู 12 · ดาวน์โหลด 3 · ขอบคุณ 2');
  assert.equal(statsLine({}), 'เปิดดู 0 · ดาวน์โหลด 0 · ขอบคุณ 0');
});

const note = { id: 7, title: 'Linked List สรุป', subject_code: 'CS201', subject_name: 'Data Structures', lesson: 'Linked List' };

test('renderStatsRow shows loading, the numbers, or the error of one note', () => {
  assert.match(renderStatsRow(note, {}), /กำลังโหลดสถิติ/);
  const loaded = renderStatsRow(note, { stats: { views: 12, downloads: 3, thanks: 2 } });
  assert.match(loaded, /href="\/note\.html\?id=7"/);
  assert.match(loaded, /CS201 · Data Structures · Linked List/);
  assert.match(loaded, /เปิดดู 12 · ดาวน์โหลด 3 · ขอบคุณ 2/);
  assert.doesNotMatch(loaded, /is-selected|stats-error/);
  const failed = renderStatsRow(note, { error: 'ดูสถิติได้เฉพาะโน้ตที่คุณอัปโหลด' });
  assert.match(failed, /class="profile-row-stats stats-error">ดูสถิติได้เฉพาะ/);
});

test('renderStatsRow marks the note opened from the profile page (?id=)', () => {
  const html = renderStatsRow(note, {}, true);
  assert.match(html, /class="profile-row is-selected"/);
  assert.match(html, /aria-current="true"/);
});

test('renderStatsRow escapes values typed in by users', () => {
  const html = renderStatsRow({ id: 3, title: '<img src=x onerror=alert(1)>', lesson: '<b>x</b>' }, {});
  assert.doesNotMatch(html, /<img|<b>/);
  assert.match(html, /&lt;img src=x/);
});

test('statsErrorMessage goes by status because stats-service has its own error texts', () => {
  assert.match(statsErrorMessage(401, { error: 'Authentication required' }), /เข้าสู่ระบบใหม่/);
  assert.match(statsErrorMessage(403, { error: 'You can only view statistics of your own note' }), /เฉพาะโน้ตที่คุณอัปโหลด/);
  assert.match(statsErrorMessage(503, { error: 'Authentication service unavailable' }), /ไม่พร้อมใช้งาน/);
  assert.match(statsErrorMessage(404, { error: 'not_found' }), /ไม่พบโน้ตนี้แล้ว/);
  assert.match(statsErrorMessage(0, null), /เชื่อมต่อเซิร์ฟเวอร์ไม่ได้/);
  assert.match(statsErrorMessage(502, null), /HTTP 502/);
});
