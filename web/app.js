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
  const previewClose = document.getElementById('previewClose');

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

  async function openPreview(note, opener) {
    previewOpener = opener;
    const seq = ++previewSeq;
    releasePreviewImage();

    previewTitle.textContent = note.title;
    previewUploader.textContent = `อัปโหลดโดย ${note.uploader_name}`;
    previewSize.textContent = `${fileTypeLabel(note.content_type)} · ${formatSize(note.size_bytes)}`;
    previewDownload.href = note.download_url;
    showPreviewStatus('กำลังโหลดตัวอย่าง…');
    dialog.showModal();

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
