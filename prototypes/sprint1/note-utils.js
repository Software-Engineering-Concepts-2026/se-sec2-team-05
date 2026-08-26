// Pure helper functions shared by the NoteShare prototypes.
// Extracted out of inline <script> blocks so they can be unit tested
// (see note-utils.test.js) without a browser/DOM.
// Wrapped in an IIFE so loading this as a plain <script src> does not leak
// escapeHtml/formatStars/etc. as globals that could clash with page scripts.
(function (exportTo) {
  const RATING_SCALE = 5;

  const HTML_ESCAPES = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  };

  function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, (ch) => HTML_ESCAPES[ch]);
  }

  function formatStars(rating) {
    const safeRating = Math.max(0, Math.min(RATING_SCALE, Math.round(Number(rating) || 0)));
    return '★'.repeat(safeRating) + '☆'.repeat(RATING_SCALE - safeRating);
  }

  const SORT_COMPARATORS = {
    rating: (a, b) => b.rating - a.rating,
    download: (a, b) => b.downloads - a.downloads,
    new: (a, b) => b.createdAt - a.createdAt,
  };

  function compareNotes(a, b, sortMode) {
    const comparator = SORT_COMPARATORS[sortMode] || SORT_COMPARATORS.new;
    return comparator(a, b);
  }

  const NoteUtils = { RATING_SCALE, escapeHtml, formatStars, compareNotes };

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = NoteUtils;
  } else {
    exportTo.NoteUtils = NoteUtils;
  }
})(typeof window !== 'undefined' ? window : globalThis);
