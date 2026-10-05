// Search page wiring: reads the form, calls GET /notes through the gateway, and opens the
// preview dialog. The pure parts (query building, card markup, error text) live in
// search-utils.js so they can be unit tested; this file only touches the DOM and fetch.
// The page is served from the same origin as the APIs (web/nginx.conf), so relative
// URLs such as /notes and /notes/7/preview work without CORS.
(function () {
  const {
    PAGE_SIZE,
    buildQuery,
    parseQuery,
    emptyFilters,
    renderNoteCard,
    errorMessage,
    hasMore,
    formatSize,
    fileTypeLabel,
    ratingSummary,
    starBar,
  } = window.SearchUtils;

  const form = document.getElementById('searchForm');
  const resetBtn = document.getElementById('resetBtn');
  const resultsCount = document.getElementById('resultsCount');
  const searchError = document.getElementById('searchError');
  const resultsList = document.getElementById('resultsList');
  const noResults = document.getElementById('noResults');
  const loadMoreBtn = document.getElementById('loadMoreBtn');

  const dialog = document.getElementById('previewDialog');
  const previewTitle = document.getElementById('previewTitle');
  const previewUploader = document.getElementById('previewUploader');
  const previewStatus = document.getElementById('previewStatus');
  const previewImage = document.getElementById('previewImage');
  const previewSize = document.getElementById('previewSize');
  const previewDownload = document.getElementById('previewDownload');
  const previewDetail = document.getElementById('previewDetail');
  const previewClose = document.getElementById('previewClose');
  const previewRatingAverage = document.getElementById('previewRatingAverage');
  const previewRatingMessage = document.getElementById('previewRatingMessage');
  const previewRatingStars = document.getElementById('previewRatingStars');
  const ratingStarButtons = [...previewRatingStars.querySelectorAll('[data-rating]')];
  const submitRating = document.getElementById('submitRating');
  const ratingSubmitStatus = document.getElementById('ratingSubmitStatus');

  const notesById = new Map();
  let currentFilters = emptyFilters();
  let nextOffset = 0;
  // A slow response for an old search must not overwrite the results of a newer one.
  let searchSeq = 0;

  function readForm() {
    const data = new FormData(form);
    const filters = emptyFilters();
    for (const field of ['q', 'faculty', 'year_level', 'topic', 'date_from', 'date_to', 'sort']) {
      filters[field] = String(data.get(field) || '').trim();
    }
    filters.file_type = data.getAll('file_type').map(String);
    return filters;
  }

  function fillForm(filters) {
    for (const field of ['q', 'faculty', 'year_level', 'topic', 'date_from', 'date_to', 'sort']) {
      form.elements[field].value = filters[field];
    }
    for (const box of form.querySelectorAll('input[name="file_type"]')) {
      box.checked = filters.file_type.includes(box.value);
    }
    // The filter panel starts folded. A search opened from a link with filters in it
    // unfolds the panel, so the user can see what is narrowing the results.
    const panel = form.querySelector('.filter-panel');
    const defaults = emptyFilters();
    const filtered = filters.file_type.length > 0 ||
      ['faculty', 'year_level', 'topic', 'date_from', 'date_to', 'sort'].some((f) => filters[f] !== defaults[f]);
    if (panel && filtered) panel.open = true;
  }

  async function fetchJson(url) {
    let response;
    try {
      response = await fetch(url, { headers: { Accept: 'application/json' } });
    } catch {
      return { ok: false, status: 0, body: null };
    }
    let body = null;
    try {
      body = await response.json();
    } catch {
      body = null;
    }
    return { ok: response.ok, status: response.status, body };
  }

  function showSearchError(message) {
    searchError.textContent = message;
    searchError.hidden = false;
  }

  async function runSearch({ append = false } = {}) {
    const seq = ++searchSeq;
    const offset = append ? nextOffset : 0;
    loadMoreBtn.disabled = true;
    if (!append) resultsCount.textContent = 'กำลังค้นหา…';

    const query = buildQuery(currentFilters, { limit: PAGE_SIZE, offset });
    const result = await fetchJson(`/notes?${query}`);
    if (seq !== searchSeq) return;
    loadMoreBtn.disabled = false;

    if (!result.ok || !result.body || !Array.isArray(result.body.items)) {
      showSearchError(errorMessage(result.status, result.body));
      if (!append) {
        resultsList.innerHTML = '';
        notesById.clear();
        resultsCount.textContent = '';
        noResults.hidden = true;
        loadMoreBtn.hidden = true;
      }
      return;
    }

    searchError.hidden = true;
    const items = result.body.items;
    if (!append) {
      resultsList.innerHTML = '';
      notesById.clear();
    }
    for (const note of items) notesById.set(String(note.id), note);
    resultsList.insertAdjacentHTML('beforeend', items.map(renderNoteCard).join(''));
    nextOffset = offset + items.length;

    resultsCount.textContent = `แสดง ${notesById.size} รายการ`;
    noResults.hidden = notesById.size > 0;
    loadMoreBtn.hidden = !hasMore(items.length);
  }

  // Keep the search in the page URL, so reload and the back button bring it back.
  function searchFromForm() {
    currentFilters = readForm();
    const query = buildQuery(currentFilters);
    const url = query ? `?${query}` : window.location.pathname;
    if (window.location.search !== (query ? `?${query}` : '')) {
      window.history.pushState(null, '', url);
    }
    runSearch();
  }

  function searchFromUrl() {
    currentFilters = parseQuery(window.location.search);
    fillForm(currentFilters);
    runSearch();
  }

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    searchFromForm();
  });

  // Choices that are picked rather than typed search straight away. Text fields wait for
  // Enter or the button, so the page does not fire a request on every key press.
  form.addEventListener('change', (event) => {
    if (event.target.matches('select, input[type="checkbox"], input[type="date"]')) {
      searchFromForm();
    }
  });

  resetBtn.addEventListener('click', () => {
    fillForm(emptyFilters());
    searchFromForm();
  });

  loadMoreBtn.addEventListener('click', () => runSearch({ append: true }));
  window.addEventListener('popstate', searchFromUrl);

  // ---- Preview dialog (US-11) ----

  let previewOpener = null;
  let previewObjectUrl = null;
  let previewSeq = 0;
  let selectedRating = 0;
  let activeRatingNote = null;

  function releasePreviewImage() {
    previewImage.hidden = true;
    previewImage.removeAttribute('src');
    if (previewObjectUrl) {
      URL.revokeObjectURL(previewObjectUrl);
      previewObjectUrl = null;
    }
  }

  function showPreviewStatus(message) {
    previewStatus.textContent = message;
    previewStatus.hidden = false;
  }

  function showRatingSelection(value) {
    selectedRating = value;
    for (const star of ratingStarButtons) {
      const selected = Number(star.dataset.rating) <= value;
      star.textContent = selected ? '★' : '☆';
      star.classList.toggle('selected', selected);
      star.setAttribute('aria-pressed', String(Number(star.dataset.rating) === value));
    }
    submitRating.disabled = value === 0;
  }

  function setAverageRating(note) {
    previewRatingAverage.textContent = ratingSummary(note);
    const cardRating = resultsList.querySelector(
      `[data-note-id="${note.id}"] .note-rating-summary`
    );
    if (cardRating) cardRating.textContent = ratingSummary(note);
    const cardStars = resultsList.querySelector(`[data-note-id="${note.id}"] .note-stars`);
    if (cardStars) cardStars.textContent = starBar(note);
  }

  async function loadRatingState(note, seq) {
    const session = window.Site.currentSession();
    const result = await window.Site.fetchJson(`/notes/${note.id}`, {
      headers: window.SessionUtils.authHeaders(session),
    });
    if (seq !== previewSeq) return;

    if (!result.ok || !result.body) {
      previewRatingMessage.textContent =
        result.status === 503
          ? 'ระบบยืนยันตัวตนไม่พร้อมใช้งาน ลองโหลดข้อมูลคะแนนอีกครั้ง'
          : 'โหลดข้อมูลคะแนนไม่สำเร็จ ลองเปิดตัวอย่างอีกครั้ง';
      return;
    }

    activeRatingNote = { ...note, ...result.body };
    setAverageRating(activeRatingNote);
    if (!session) {
      previewRatingMessage.textContent = 'เข้าสู่ระบบ แล้วเปิดหรือดาวน์โหลดโน้ตขณะเข้าสู่ระบบเพื่อให้คะแนน';
      return;
    }
    if (result.body.can_rate !== true) {
      previewRatingMessage.textContent = 'เปิดหรือดาวน์โหลดโน้ตขณะเข้าสู่ระบบก่อนจึงจะให้คะแนนได้';
      return;
    }

    previewRatingStars.hidden = false;
    submitRating.hidden = false;
    const currentRating = Number(result.body.user_rating) || 0;
    showRatingSelection(currentRating);
    previewRatingMessage.textContent = currentRating
      ? `คะแนนปัจจุบันของคุณคือ ${currentRating} ดาว คุณสามารถแก้ไขได้`
      : 'คุณเปิดโน้ตนี้ขณะเข้าสู่ระบบแล้ว เลือกคะแนนเพื่อให้คะแนนโน้ต';
  }

  async function submitNoteRating() {
    if (!activeRatingNote || selectedRating === 0) return;
    const session = window.Site.currentSession();
    if (!session) {
      previewRatingMessage.textContent = 'กรุณาเข้าสู่ระบบก่อนให้คะแนน';
      return;
    }

    submitRating.disabled = true;
    ratingSubmitStatus.textContent = 'กำลังบันทึกคะแนน…';
    const result = await window.Site.fetchJson(`/notes/${activeRatingNote.id}/rating`, {
      method: 'PUT',
      headers: {
        ...window.SessionUtils.authHeaders(session),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ rating: selectedRating }),
    });

    if (!result.ok || !result.body) {
      submitRating.disabled = selectedRating === 0;
      ratingSubmitStatus.textContent =
        result.status === 401
          ? 'เซสชันหมดอายุ กรุณาเข้าสู่ระบบใหม่'
          : result.status === 403
            ? 'เปิดหรือดาวน์โหลดโน้ตขณะเข้าสู่ระบบก่อนให้คะแนน'
            : result.status === 503
              ? 'ระบบยืนยันตัวตนไม่พร้อมใช้งาน ลองอีกครั้ง'
              : 'บันทึกคะแนนไม่สำเร็จ ลองอีกครั้ง';
      return;
    }

    activeRatingNote.average_rating = result.body.average_rating;
    activeRatingNote.rating_count = result.body.rating_count;
    setAverageRating(activeRatingNote);
    ratingSubmitStatus.textContent = 'บันทึกคะแนนแล้ว';
    previewRatingMessage.textContent = `คะแนนปัจจุบันของคุณคือ ${result.body.rating} ดาว คุณสามารถแก้ไขได้`;
    submitRating.disabled = false;
  }

  async function openPreview(note, opener) {
    previewOpener = opener;
    const seq = ++previewSeq;
    releasePreviewImage();
    activeRatingNote = null;
    previewRatingStars.hidden = true;
    submitRating.hidden = true;
    submitRating.disabled = true;
    previewRatingMessage.textContent = '';
    ratingSubmitStatus.textContent = '';
    previewRatingAverage.textContent = ratingSummary(note);
    showRatingSelection(0);

    previewTitle.textContent = note.title;
    previewUploader.textContent = `อัปโหลดโดย ${note.uploader_name}`;
    previewSize.textContent = `${fileTypeLabel(note.content_type)} · ${formatSize(note.size_bytes)}`;
    previewDownload.href = note.download_url;
    previewDetail.href = `/note.html?id=${encodeURIComponent(note.id)}`;
    showPreviewStatus('กำลังโหลดตัวอย่าง…');
    dialog.showModal();
    loadRatingState(note, seq);

    // fetch instead of <img src> so a 422/404 can show the API's reason, not a broken image
    let response;
    try {
      response = await fetch(note.preview_url);
    } catch {
      if (seq === previewSeq) showPreviewStatus(errorMessage(0, null));
      return;
    }
    if (seq !== previewSeq) return;

    if (!response.ok) {
      let body = null;
      try {
        body = await response.json();
      } catch {
        body = null;
      }
      if (seq === previewSeq) showPreviewStatus(errorMessage(response.status, body));
      return;
    }

    const blob = await response.blob();
    if (seq !== previewSeq) return;
    previewObjectUrl = URL.createObjectURL(blob);
    previewImage.src = previewObjectUrl;
    previewImage.alt = `ตัวอย่างหน้าแรกของ ${note.title}`;
    previewImage.hidden = false;
    previewStatus.hidden = true;
  }

  resultsList.addEventListener('click', (event) => {
    const button = event.target.closest('[data-preview-id]');
    if (!button) return;
    const note = notesById.get(button.dataset.previewId);
    if (note) openPreview(note, button);
  });

  previewRatingStars.addEventListener('click', (event) => {
    const star = event.target.closest('[data-rating]');
    if (star) showRatingSelection(Number(star.dataset.rating));
  });
  submitRating.addEventListener('click', submitNoteRating);

  previewClose.addEventListener('click', () => dialog.close());

  // A click on the backdrop lands on the <dialog> itself; clicks inside hit .preview-body.
  dialog.addEventListener('click', (event) => {
    if (event.target === dialog) dialog.close();
  });

  // Esc, the close button and the backdrop all end here. The results under the dialog
  // were never touched, and focus goes back to the button that opened it without scrolling.
  dialog.addEventListener('close', () => {
    previewSeq++;
    releasePreviewImage();
    if (previewOpener) previewOpener.focus({ preventScroll: true });
    previewOpener = null;
  });

  searchFromUrl();
})();
