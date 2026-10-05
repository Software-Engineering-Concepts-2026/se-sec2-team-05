// Pure helpers for the NoteShare search page (web/index.html).
// They take and return plain values (no DOM, no fetch), so search-utils.test.js
// runs them under `node --test` without a browser.
// Same loading pattern as prototypes/sprint1/note-utils.js: one IIFE that becomes
// window.SearchUtils in the browser and module.exports under Node.
(function (exportTo) {
  // Matches the query parameters GET /notes accepts (services/notes-service/README.md).
  const TEXT_FIELDS = ['q', 'faculty', 'year_level', 'topic', 'date_from', 'date_to'];
  const FILE_TYPES = ['pdf', 'png', 'jpg'];
  const SORTS = ['new', 'old', 'class_date', 'title', 'rating'];
  const DEFAULT_SORT = 'new';
  const PAGE_SIZE = 20;

  const FILE_TYPE_LABELS = {
    'application/pdf': 'PDF',
    'image/png': 'PNG',
    'image/jpeg': 'JPG',
  };

  // Names of the fields as the search form shows them, used in error messages.
  const FIELD_LABELS = {
    q: 'คำค้นหา',
    faculty: 'คณะ',
    year_level: 'ชั้นปี',
    topic: 'หัวข้อ',
    date_from: 'วันที่เริ่ม',
    date_to: 'วันที่สิ้นสุด',
    file_type: 'ประเภทไฟล์',
    sort: 'การเรียง',
    'limit/offset': 'หน้าผลลัพธ์',
  };

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

  function emptyFilters() {
    return {
      q: '',
      faculty: '',
      year_level: '',
      topic: '',
      date_from: '',
      date_to: '',
      file_type: [],
      sort: DEFAULT_SORT,
    };
  }

  // Filters -> query string for both the page URL and GET /notes.
  // Empty fields and the default sort are left out so a plain search keeps a clean URL.
  function buildQuery(filters, page = {}) {
    const params = new URLSearchParams();
    for (const field of TEXT_FIELDS) {
      const value = String(filters[field] ?? '').trim();
      if (value) params.set(field, value);
    }
    for (const type of filters.file_type || []) {
      if (FILE_TYPES.includes(type)) params.append('file_type', type);
    }
    if (filters.sort && filters.sort !== DEFAULT_SORT) params.set('sort', filters.sort);
    if (page.limit !== undefined) params.set('limit', String(page.limit));
    if (page.offset) params.set('offset', String(page.offset));
    return params.toString();
  }

  // Page URL query -> filters, so reload and the back button restore the same search.
  // Unknown file types and sorts are dropped instead of being sent on to the API.
  function parseQuery(search) {
    const params = new URLSearchParams(search);
    const filters = emptyFilters();
    for (const field of TEXT_FIELDS) {
      filters[field] = (params.get(field) || '').trim();
    }
    filters.file_type = [...new Set(params.getAll('file_type'))].filter((t) => FILE_TYPES.includes(t));
    const sort = params.get('sort');
    if (SORTS.includes(sort)) filters.sort = sort;
    return filters;
  }

  function formatSize(bytes) {
    const size = Number(bytes) || 0;
    if (size < 1024) return `${size} B`;
    if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
    return `${(size / (1024 * 1024)).toFixed(1)} MB`;
  }

  function fileTypeLabel(contentType) {
    return FILE_TYPE_LABELS[contentType] || 'ไฟล์';
  }

  function ratingSummary(note) {
    const average = Number(note.average_rating);
    const count = Number(note.rating_count) || 0;
    if (note.average_rating === null || note.average_rating === undefined || !count || !Number.isFinite(average)) {
      return 'ยังไม่มีคะแนน';
    }
    return `เฉลี่ย ${average.toFixed(1)} / 5 (${count})`;
  }

  // Five stars for the card, filled up to the rounded average. No ratings -> five empty stars.
  function starBar(note) {
    const average = Number(note.average_rating);
    const filled = note.average_rating === null || note.average_rating === undefined || !Number.isFinite(average)
      ? 0
      : Math.max(0, Math.min(5, Math.round(average)));
    return '★'.repeat(filled) + '☆'.repeat(5 - filled);
  }

  // One result card. Every value from the API goes through escapeHtml, because titles
  // and descriptions are typed in by other users.
  // US-31 AC3: the uploader's name is on every card.
  function renderNoteCard(note) {
    const subject = [note.subject_code, note.subject_name].filter(Boolean).join(' · ');
    const tags = [note.faculty, note.year_level ? `ปี ${note.year_level}` : '', note.lesson, note.topic]
      .filter(Boolean)
      .map((tag) => `<span class="note-tag">${escapeHtml(tag)}</span>`)
      .join('');
    const classDate = note.class_date ? `<span>เรียนวันที่ ${escapeHtml(note.class_date)}</span>` : '';
    return `<article class="note-card" data-note-id="${escapeHtml(note.id)}">
  <div class="note-card-top">
    <span class="tag-course">${escapeHtml(note.subject_code)}</span>
    <span class="file-badge">${escapeHtml(fileTypeLabel(note.content_type))}</span>
  </div>
  <h2 class="note-title">${escapeHtml(note.title)}</h2>
  <p class="note-sub">${escapeHtml(subject)}</p>
  <p class="note-uploader">อัปโหลดโดย <strong>${escapeHtml(note.uploader_name)}</strong></p>
  <p class="note-rating"><span class="note-stars" aria-hidden="true">${starBar(note)}</span>
    <span class="note-rating-summary">${escapeHtml(ratingSummary(note))}</span></p>
  <div class="note-tags">${tags}</div>
  <div class="note-card-foot">
    <span>ดาวน์โหลด ${escapeHtml(Number(note.download_count) || 0)} ครั้ง</span>
    ${classDate}
    <button type="button" class="preview-link" data-preview-id="${escapeHtml(note.id)}">ดูตัวอย่าง</button>
  </div>
</article>`;
  }

  // API error -> a message for the page. `body` is the parsed JSON body, or null when
  // there was no JSON (e.g. a gateway error page or no network at all).
  function errorMessage(status, body) {
    const code = body && body.error;
    if (code === 'invalid_filter') {
      const label = FIELD_LABELS[body.field] || body.field || 'ตัวกรอง';
      return `ค่าของ "${label}" ไม่ถูกต้อง ลองแก้แล้วค้นหาใหม่`;
    }
    if (code === 'preview_unavailable') return 'โน้ตนี้สร้างภาพตัวอย่างไม่ได้ ลองดาวน์โหลดไฟล์เต็มแทน';
    if (code === 'not_found') return 'ไม่พบโน้ตนี้แล้ว อาจถูกลบไปก่อนหน้านี้';
    if (code === 'file_not_found') return 'ไม่พบไฟล์ของโน้ตนี้บนเซิร์ฟเวอร์';
    if (status === 0) return 'เชื่อมต่อเซิร์ฟเวอร์ไม่ได้ ตรวจการเชื่อมต่อแล้วลองใหม่';
    return `เกิดข้อผิดพลาดจากเซิร์ฟเวอร์ (HTTP ${status}) ลองใหม่อีกครั้ง`;
  }

  // GET /notes returns `count` for the current page only, not a total. A full page
  // means there may be more, so the page shows "load more" until a short page comes back.
  function hasMore(pageCount, limit = PAGE_SIZE) {
    return pageCount >= limit;
  }

  const SearchUtils = {
    FILE_TYPES,
    SORTS,
    DEFAULT_SORT,
    PAGE_SIZE,
    escapeHtml,
    emptyFilters,
    buildQuery,
    parseQuery,
    formatSize,
    fileTypeLabel,
    ratingSummary,
    starBar,
    renderNoteCard,
    errorMessage,
    hasMore,
  };

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = SearchUtils;
  } else {
    exportTo.SearchUtils = SearchUtils;
  }
})(typeof window !== 'undefined' ? window : globalThis);
