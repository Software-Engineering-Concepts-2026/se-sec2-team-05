const test = require('node:test');
const assert = require('node:assert/strict');
const { escapeHtml, formatStars, compareNotes, RATING_SCALE } = require('./note-utils.js');

test('escapeHtml escapes HTML special characters', () => {
  assert.equal(escapeHtml('<script>alert(1)</script>'), '&lt;script&gt;alert(1)&lt;/script&gt;');
  assert.equal(escapeHtml('Tom & Jerry "best"'), 'Tom &amp; Jerry &quot;best&quot;');
});

test('escapeHtml treats null/undefined as empty string', () => {
  assert.equal(escapeHtml(null), '');
  assert.equal(escapeHtml(undefined), '');
});

test('formatStars rounds and fills the rest with empty stars', () => {
  assert.equal(formatStars(4.2), '★★★★☆');
  assert.equal(formatStars(4.8), '★★★★★');
});

test('formatStars clamps out-of-range ratings to 0..RATING_SCALE', () => {
  assert.equal(formatStars(-3), '☆☆☆☆☆');
  assert.equal(formatStars(10), '★'.repeat(RATING_SCALE));
});

test('compareNotes sorts by rating when sortMode is "rating"', () => {
  const a = { rating: 4.2, downloads: 100, createdAt: 1 };
  const b = { rating: 4.8, downloads: 50, createdAt: 2 };
  assert.ok(compareNotes(a, b, 'rating') > 0);
});

test('compareNotes sorts by downloads when sortMode is "download"', () => {
  const a = { rating: 4.8, downloads: 50, createdAt: 1 };
  const b = { rating: 4.2, downloads: 100, createdAt: 2 };
  assert.ok(compareNotes(a, b, 'download') > 0);
});

test('compareNotes falls back to newest-first for unknown sortMode', () => {
  const a = { rating: 4.8, downloads: 100, createdAt: 1 };
  const b = { rating: 4.2, downloads: 50, createdAt: 5 };
  assert.ok(compareNotes(a, b, 'anything-else') > 0);
});
