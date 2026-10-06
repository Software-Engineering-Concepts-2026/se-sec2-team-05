// Note detail page wiring (web/note.html, Issue #85): loads one note with GET /notes/<id> and
// puts download, favorite, report, rating, thanks and comments on one page. The pure parts
// live in note-utils.js and search-utils.js; this file only touches the DOM and fetch.
(function () {
  const { authHeaders, clearSession, loginUrl } = window.SessionUtils;
  const { errorMessage, ratingSummary } = window.SearchUtils;
  const {
    MAX_COMMENT_LENGTH,
    MAX_REPORT_REASON_LENGTH,
    noteIdFromSearch,
    noteMetaLine,
    noteTags,
    renderComment,
    textProblem,
    markDownloaded,
    hasDownloaded,
    thanksView,
    actionErrorMessage,
  } = window.NoteUtils;
  const { storage, currentSession, fetchJson, showFieldErrors, renderNav } = window.Site;

  const byId = (id) => document.getElementById(id);
  const backLink = byId('backLink');
  const noteLoading = byId('noteLoading');
  const noteError = byId('noteError');
  const noteDetail = byId('noteDetail');
  const noteCourse = byId('noteCourse');
  const noteTitle = byId('noteTitle');
  const noteMeta = byId('noteMeta');
  const noteTagList = byId('noteTags');
  const noteDescription = byId('noteDescription');
  const previewStatus = byId('previewStatus');
  const previewImage = byId('previewImage');
  const downloadBtn = byId('downloadBtn');
  const favoriteBtn = byId('favoriteBtn');
  const reportToggle = byId('reportToggle');
  const actionStatus = byId('actionStatus');
  const reportForm = byId('reportForm');
  const reportReason = byId('reportReason');
  const reportCancel = byId('reportCancel');
  const ratingAverage = byId('ratingAverage');
  const ratingMessage = byId('ratingMessage');
  const ratingStars = byId('ratingStars');
  const ratingStarButtons = [...ratingStars.querySelectorAll('[data-rating]')];
  const submitRating = byId('submitRating');
  const ratingSubmitStatus = byId('ratingSubmitStatus');
  const thanksMessage = byId('thanksMessage');
  const thanksBtn = byId('thanksBtn');
  const commentsSection = byId('commentsSection');
  const commentsTitle = byId('commentsTitle');
  const commentsError = byId('commentsError');
  const commentsList = byId('commentsList');
  const noComments = byId('noComments');
  const commentForm = byId('commentForm');
  const commentInput = byId('commentInput');
  const commentLogin = byId('commentLogin');

  const noteId = noteIdFromSearch(window.location.search);
  const here = window.location.pathname + window.location.search;
  // edit/delete with the edit token shown after upload (US-19, US-20), no login needed
  if (noteId !== null) byId('editTokenLink').href = `/edit.html?id=${noteId}`;
  let session = currentSession();
  let note = null;
  let comments = [];
  let commentsLoaded = false;
  let selectedRating = 0;

  // Back to the search the user came from (filters and all), else to a plain search page.
  try {
    const from = new URL(document.referrer);
    if (from.origin === window.location.origin && ['/', '/index.html'].includes(from.pathname)) {
      backLink.href = from.pathname + from.search;
    }
  } catch {
    // no referrer: keep href="/"
  }

  function loginLink(text = 'เข้าสู่ระบบ') {
    const a = document.createElement('a');
    a.href = loginUrl(here);
    a.textContent = text;
    return a;
  }

  // Puts a message in a status line, with a login link after it when the action needs one.
  function say(el, message, withLogin = false) {
    el.replaceChildren(message);
    if (withLogin) el.append(' ', loginLink());
    el.hidden = !message;
  }

  // A 401 means the saved token was revoked (logout in another tab) or expired early. Forget
  // it, so the nav and every box on the page agree the user is logged out.
  function sessionEnded(el) {
    clearSession(storage());
    session = null;
    renderNav();
    renderLoginParts();
    say(el, actionErrorMessage(401, { error: 'unauthorized' }), true);
  }

  function showFailure(el, result) {
    if (result.status === 401) {
      sessionEnded(el);
      return;
    }
    say(el, actionErrorMessage(result.status, result.body));
  }

  function isOwnNote() {
    return note.thank_status === 'own_note';
  }

  // ---- Note ----

  function renderMeta() {
    noteMeta.textContent = noteMetaLine(note);
  }

  function renderNote() {
    document.title = `${note.title} - NoteShare`;
    noteCourse.textContent = note.subject_code;
    noteTitle.textContent = note.title;
    renderMeta();
    noteTagList.replaceChildren(
      ...noteTags(note).map((tag) => {
        const span = document.createElement('span');
        span.className = 'note-tag';
        span.textContent = tag;
        return span;
      })
    );
    noteDescription.textContent = note.description || '';
    noteDescription.hidden = !note.description;
    renderLoginParts();
    noteDetail.hidden = false;
    commentsSection.hidden = false;
  }

  // Everything that changes when the user logs out in the middle of using the page.
  function renderLoginParts() {
    renderFavorite();
    reportToggle.hidden = Boolean(session) && isOwnNote();
    if (!session) closeReportForm();
    renderRating();
    renderThanks();
    renderComments();
  }

  async function loadPreview() {
    // fetch instead of <img src> so a 422/404 can show the API's reason, not a broken image
    let response;
    try {
      response = await fetch(note.preview_url);
    } catch {
      previewStatus.textContent = errorMessage(0, null);
      return;
    }
    if (!response.ok) {
      let body = null;
      try {
        body = await response.json();
      } catch {
        body = null;
      }
      previewStatus.textContent = errorMessage(response.status, body);
      return;
    }
    // The object URL lives as long as the page, so it is never revoked.
    previewImage.src = URL.createObjectURL(await response.blob());
    previewImage.alt = `ตัวอย่างหน้าแรกของ ${note.title}`;
    previewImage.hidden = false;
    previewStatus.hidden = true;
  }

  async function loadNote() {
    if (noteId === null) {
      noteLoading.hidden = true;
      say(noteError, 'ลิงก์นี้ไม่มีรหัสโน้ตที่ถูกต้อง ลองค้นหาโน้ตจากหน้าค้นหาอีกครั้ง');
      return;
    }
    // Sent with the token when logged in, so the reply carries is_favorited, thank_status and
    // can_rate for this user. Opening the page counts as a view (view_count), like the preview.
    const result = await fetchJson(`/notes/${noteId}`, { headers: authHeaders(session) });
    noteLoading.hidden = true;
    if (!result.ok || !result.body) {
      say(noteError, errorMessage(result.status, result.body));
      return;
    }
    note = result.body;
    renderNote();
    loadPreview();
    loadComments();
  }

  // ---- Download (US-12) ----

  // fetch + a temporary link instead of a plain <a href>, so the request carries the token:
  // the download then counts as this user's access (rating, Issue #13) and the page knows it
  // happened, which is when the thanks button appears (US-28).
  downloadBtn.addEventListener('click', async () => {
    downloadBtn.disabled = true;
    say(actionStatus, 'กำลังดาวน์โหลด…');
    let response;
    try {
      response = await fetch(note.download_url, { headers: authHeaders(session) });
    } catch {
      downloadBtn.disabled = false;
      say(actionStatus, errorMessage(0, null));
      return;
    }
    if (!response.ok) {
      let body = null;
      try {
        body = await response.json();
      } catch {
        body = null;
      }
      downloadBtn.disabled = false;
      say(actionStatus, actionErrorMessage(response.status, body));
      return;
    }
    const url = URL.createObjectURL(await response.blob());
    const link = document.createElement('a');
    link.href = url;
    link.download = note.file_name || `note-${note.id}`;
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 10000);

    downloadBtn.disabled = false;
    note.download_count = (Number(note.download_count) || 0) + 1;
    renderMeta();
    markDownloaded(storage(), session, note.id);
    renderThanks();
    say(actionStatus, 'ดาวน์โหลดแล้ว');
  });

  // ---- Favorite (US-15) ----

  function renderFavorite() {
    const on = Boolean(session) && note.is_favorited === true;
    favoriteBtn.setAttribute('aria-pressed', String(on));
    const label = on ? 'เอาออกจากรายการโปรด' : 'บันทึกเป็นรายการโปรด';
    favoriteBtn.setAttribute('aria-label', label);
    favoriteBtn.title = label;
  }

  favoriteBtn.addEventListener('click', async () => {
    if (!session) {
      say(actionStatus, 'เข้าสู่ระบบก่อนบันทึกเป็นรายการโปรด', true);
      return;
    }
    const adding = note.is_favorited !== true;
    favoriteBtn.disabled = true;
    const result = await fetchJson(`/notes/${note.id}/favorite`, {
      method: adding ? 'POST' : 'DELETE',
      headers: authHeaders(session),
    });
    favoriteBtn.disabled = false;
    if (!result.ok) {
      showFailure(actionStatus, result);
      return;
    }
    note.is_favorited = adding;
    renderFavorite();
    say(actionStatus, adding ? 'บันทึกเป็นรายการโปรดแล้ว' : 'เอาออกจากรายการโปรดแล้ว');
  });

  // ---- Report (Issue #17) ----

  function closeReportForm() {
    reportForm.hidden = true;
    reportToggle.setAttribute('aria-expanded', 'false');
  }

  reportToggle.addEventListener('click', () => {
    if (!session) {
      say(actionStatus, 'เข้าสู่ระบบก่อนรายงานโน้ต', true);
      return;
    }
    if (!reportForm.hidden) {
      closeReportForm();
      return;
    }
    reportForm.hidden = false;
    reportToggle.setAttribute('aria-expanded', 'true');
    say(actionStatus, '');
    reportReason.focus();
  });

  reportCancel.addEventListener('click', () => {
    closeReportForm();
    reportToggle.focus();
  });

  reportForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const problem = textProblem(reportReason.value, MAX_REPORT_REASON_LENGTH);
    showFieldErrors(reportForm, { reason: problem });
    if (problem) {
      reportReason.focus();
      return;
    }
    const submit = reportForm.querySelector('[type="submit"]');
    submit.disabled = true;
    const result = await fetchJson(`/notes/${note.id}/reports`, {
      method: 'POST',
      headers: { ...authHeaders(session), 'Content-Type': 'application/json' },
      body: JSON.stringify({ reason: reportReason.value.trim() }),
    });
    submit.disabled = false;
    if (result.ok || result.status === 409) {
      reportForm.reset();
      closeReportForm();
      say(actionStatus, result.ok ? 'ส่งรายงานแล้ว ผู้ดูแลจะตรวจสอบโน้ตนี้' : actionErrorMessage(409, result.body));
      reportToggle.focus();
      return;
    }
    showFailure(actionStatus, result);
  });

  // ---- Rating (Issue #13) ----

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

  function renderRating() {
    ratingAverage.textContent = ratingSummary(note);
    ratingStars.hidden = true;
    submitRating.hidden = true;
    if (!session) {
      say(ratingMessage, 'เข้าสู่ระบบเพื่อให้คะแนนโน้ตนี้', true);
      return;
    }
    if (note.can_rate !== true) {
      say(ratingMessage, 'เปิดหรือดาวน์โหลดโน้ตขณะเข้าสู่ระบบก่อนจึงจะให้คะแนนได้');
      return;
    }
    ratingStars.hidden = false;
    submitRating.hidden = false;
    const current = Number(note.user_rating) || 0;
    showRatingSelection(current);
    say(ratingMessage, current ? `คะแนนของคุณคือ ${current} ดาว เปลี่ยนได้` : 'เลือกคะแนน 1 ถึง 5 ดาว');
  }

  ratingStars.addEventListener('click', (event) => {
    const star = event.target.closest('[data-rating]');
    if (star) showRatingSelection(Number(star.dataset.rating));
  });

  submitRating.addEventListener('click', async () => {
    if (selectedRating === 0) return;
    submitRating.disabled = true;
    say(ratingSubmitStatus, 'กำลังบันทึกคะแนน…');
    const result = await fetchJson(`/notes/${note.id}/rating`, {
      method: 'PUT',
      headers: { ...authHeaders(session), 'Content-Type': 'application/json' },
      body: JSON.stringify({ rating: selectedRating }),
    });
    submitRating.disabled = false;
    if (!result.ok || !result.body) {
      showFailure(ratingSubmitStatus, result);
      return;
    }
    note.average_rating = result.body.average_rating;
    note.rating_count = result.body.rating_count;
    note.user_rating = result.body.rating;
    renderRating();
    say(ratingSubmitStatus, 'บันทึกคะแนนแล้ว');
  });

  // ---- Thanks (US-28) ----

  function renderThanks() {
    const view = thanksView(session ? note.thank_status : null, hasDownloaded(storage(), session, note.id));
    say(thanksMessage, view.message, view.state === 'login' && !session);
    thanksBtn.hidden = view.state !== 'ready';
  }

  thanksBtn.addEventListener('click', async () => {
    thanksBtn.disabled = true;
    const result = await fetchJson(`/notes/${note.id}/thanks`, {
      method: 'POST',
      headers: authHeaders(session),
    });
    thanksBtn.disabled = false;
    if (!result.ok) {
      showFailure(thanksMessage, result);
      return;
    }
    note.thank_status = 'thanked';
    renderThanks();
    say(thanksMessage, 'ส่งคำขอบคุณถึงเจ้าของโน้ตแล้ว');
  });

  // ---- Comments (Issue #14) ----

  function renderComments() {
    commentsTitle.textContent = commentsLoaded ? `ความคิดเห็น · ${comments.length}` : 'ความคิดเห็น';
    commentsList.innerHTML = comments.map((comment) => renderComment(comment, session)).join('');
    noComments.hidden = !commentsLoaded || comments.length > 0;
    commentForm.hidden = !session;
    commentLogin.hidden = Boolean(session);
    if (!session) commentLogin.replaceChildren(loginLink(), ' เพื่อแสดงความคิดเห็น');
  }

  async function loadComments() {
    const result = await fetchJson(`/notes/${note.id}/comments`);
    if (!result.ok || !result.body || !Array.isArray(result.body.comments)) {
      say(commentsError, errorMessage(result.status, result.body));
      return;
    }
    comments = result.body.comments;
    commentsLoaded = true;
    renderComments();
  }

  commentForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const problem = textProblem(commentInput.value, MAX_COMMENT_LENGTH);
    if (problem) {
      say(commentsError, `ความคิดเห็น${problem}`);
      commentInput.focus();
      return;
    }
    const submit = commentForm.querySelector('[type="submit"]');
    submit.disabled = true;
    const result = await fetchJson(`/notes/${note.id}/comments`, {
      method: 'POST',
      headers: { ...authHeaders(session), 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: commentInput.value.trim() }),
    });
    submit.disabled = false;
    if (!result.ok || !result.body) {
      showFailure(commentsError, result);
      return;
    }
    say(commentsError, '');
    commentInput.value = '';
    // The API lists newest first, so the new comment goes on top.
    comments = [result.body, ...comments];
    renderComments();
  });

  commentsList.addEventListener('click', async (event) => {
    const button = event.target.closest('[data-delete-comment]');
    if (!button) return;
    const commentId = Number(button.dataset.deleteComment);
    button.disabled = true;
    const result = await fetchJson(`/notes/${note.id}/comments/${commentId}`, {
      method: 'DELETE',
      headers: authHeaders(session),
    });
    if (!result.ok && result.status !== 404) {
      button.disabled = false;
      showFailure(commentsError, result);
      return;
    }
    // 404 = already gone (deleted in another tab), which is what the user wanted anyway.
    say(commentsError, '');
    comments = comments.filter((comment) => comment.id !== commentId);
    renderComments();
    commentInput.focus();
  });

  loadNote();
})();
