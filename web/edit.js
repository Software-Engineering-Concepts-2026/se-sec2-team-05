// Edit-by-token page wiring (web/edit.html, US-19 + US-20, ADR-004): loads the note, checks
// the edit token with an empty PATCH, then edits (PATCH, only changed fields) or deletes
// (DELETE) with X-Note-Token. No login needed. The token stays in a variable of this page
// and is gone on reload. The pure parts live in edit-utils.js and profile-utils.js.
(function () {
  const { fieldErrors } = window.SessionUtils;
  const { validateMetadata } = window.UploadUtils;
  const { noteIdFromSearch, noteUrl } = window.NoteUtils;
  const { editFormValues, changedFields } = window.ProfileUtils;
  const { tokenProblem, tokenHeaders, tokenCheckResult, editErrorMessage } = window.EditUtils;
  const { fetchJson, showFieldErrors } = window.Site;

  const byId = (id) => document.getElementById(id);
  const backLink = byId('backLink');
  const editLoading = byId('editLoading');
  const pageError = byId('pageError');
  const pageStatus = byId('pageStatus');
  const noteSummary = byId('noteSummary');
  const summaryTitle = byId('summaryTitle');
  const summaryMeta = byId('summaryMeta');
  const tokenForm = byId('tokenForm');
  const editForm = byId('editForm');
  const deleteOpen = byId('deleteOpen');
  const deletedBox = byId('deletedBox');
  const deletedNoteTitle = byId('deletedNoteTitle');
  const deletedTitle = byId('deletedTitle');
  const deleteDialog = byId('deleteDialog');
  const deleteForm = byId('deleteForm');
  const deleteNoteTitle = byId('deleteNoteTitle');
  const deleteError = byId('deleteError');

  const noteId = noteIdFromSearch(window.location.search);
  let note = null;
  let token = '';

  function say(el, message) {
    el.textContent = message || '';
    el.hidden = !message;
  }

  function showSummary() {
    summaryTitle.textContent = note.title;
    summaryMeta.textContent = [note.subject_code, note.subject_name, note.lesson, `อัปโหลดโดย ${note.uploader_name}`]
      .filter(Boolean)
      .join(' · ');
    noteSummary.hidden = false;
  }

  // The note is gone (deleted elsewhere): nothing on this page can work any more.
  function noteGone() {
    tokenForm.hidden = true;
    editForm.hidden = true;
    noteSummary.hidden = true;
    say(pageError, editErrorMessage(404, { error: 'not_found' }));
  }

  // ---- Load the note ----
  // Plain GET /notes/<id> without Authorization, like a visitor. It counts as a view, the
  // same as opening the note page.

  async function loadNote() {
    if (noteId === null) {
      editLoading.hidden = true;
      say(pageError, 'ลิงก์ไม่ถูกต้อง ไม่มีเลขโน้ต ลองเปิดจากหน้าโน้ตอีกครั้ง');
      return;
    }
    backLink.href = noteUrl(noteId);
    const result = await fetchJson(`/notes/${noteId}`);
    editLoading.hidden = true;
    if (!result.ok || !result.body) {
      say(pageError, editErrorMessage(result.status, result.body));
      return;
    }
    note = result.body;
    document.title = `แก้ไข ${note.title} - NoteShare`;
    showSummary();
    tokenForm.hidden = false;
    tokenForm.elements.token.focus();
  }

  // ---- Step 1: check the token ----

  tokenForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    say(pageError, '');
    const typed = tokenForm.elements.token.value;
    const problem = tokenProblem(typed);
    if (showFieldErrors(tokenForm, { token: problem })) {
      tokenForm.elements.token.focus();
      return;
    }
    const submit = tokenForm.querySelector('[type="submit"]');
    submit.disabled = true;
    const result = await fetchJson(`/notes/${noteId}`, {
      method: 'PATCH',
      headers: { ...tokenHeaders(typed), 'Content-Type': 'application/x-www-form-urlencoded' },
      body: '',
    });
    submit.disabled = false;

    const answer = tokenCheckResult(result.status, result.body);
    if (answer === 'wrong') {
      showFieldErrors(tokenForm, { token: editErrorMessage(403, { error: 'forbidden' }) });
      tokenForm.elements.token.focus();
      return;
    }
    if (answer === 'gone') {
      noteGone();
      return;
    }
    if (answer !== 'valid') {
      say(pageError, editErrorMessage(result.status, result.body));
      return;
    }

    token = typed.trim();
    tokenForm.reset();
    tokenForm.hidden = true;
    for (const [name, value] of Object.entries(editFormValues(note))) editForm.elements[name].value = value;
    showFieldErrors(editForm, {});
    editForm.hidden = false;
    say(pageStatus, 'รหัสถูกต้อง แก้ข้อมูลแล้วกดบันทึก หรือลบโน้ตนี้ได้');
    editForm.elements.title.focus();
  });

  // ---- Step 2a: edit (US-19) ----

  function readEditForm() {
    const fields = {};
    for (const [name, value] of new FormData(editForm).entries()) fields[name] = String(value);
    return fields;
  }

  editForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    say(pageStatus, '');
    say(pageError, '');
    const fields = readEditForm();
    const first = showFieldErrors(editForm, validateMetadata(fields));
    if (first) {
      say(pageError, editErrorMessage(400, { error: 'validation_failed' }));
      first.focus();
      return;
    }
    const changed = changedFields(note, fields);
    if (Object.keys(changed).length === 0) {
      say(pageError, editErrorMessage(400, { error: 'no_fields_to_update' }));
      return;
    }

    const submit = editForm.querySelector('[type="submit"]');
    submit.disabled = true;
    // PATCH /notes/<id> reads form fields (request.form), like POST /notes
    const result = await fetchJson(`/notes/${noteId}`, {
      method: 'PATCH',
      headers: { ...tokenHeaders(token), 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams(changed),
    });
    submit.disabled = false;

    if (result.status === 404) {
      noteGone();
      return;
    }
    if (!result.ok || !result.body) {
      const serverFirst = showFieldErrors(editForm, fieldErrors(result.body));
      say(pageError, editErrorMessage(result.status, result.body));
      if (serverFirst) serverFirst.focus();
      return;
    }
    note = { ...note, ...result.body };
    showSummary();
    say(pageStatus, 'บันทึกการแก้ไขแล้ว');
    pageStatus.focus();
  });

  // ---- Step 2b: delete (US-20) ----

  // Focus goes back right away instead of waiting for the 'close' event, which the browser
  // may deliver late (same as the profile page). The listener still covers Esc.
  function closeDialog() {
    deleteDialog.close();
    if (deleteOpen.isConnected && !editForm.hidden) deleteOpen.focus({ preventScroll: true });
  }

  deleteOpen.addEventListener('click', () => {
    deleteNoteTitle.textContent = note.title;
    say(deleteError, '');
    say(pageStatus, '');
    deleteDialog.showModal();
  });

  deleteDialog.addEventListener('click', (event) => {
    if (event.target === deleteDialog || event.target.closest('[data-close-dialog]')) closeDialog();
  });

  deleteForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const submit = deleteForm.querySelector('[type="submit"]');
    submit.disabled = true;
    const result = await fetchJson(`/notes/${noteId}`, { method: 'DELETE', headers: tokenHeaders(token) });
    submit.disabled = false;
    // 404 = already deleted (another tab), which is what the user asked for
    if (!result.ok && result.status !== 404) {
      say(deleteError, editErrorMessage(result.status, result.body));
      return;
    }
    deleteDialog.close();
    token = '';
    editForm.hidden = true;
    noteSummary.hidden = true;
    backLink.hidden = true;
    deletedNoteTitle.textContent = note.title;
    deletedBox.hidden = false;
    deletedTitle.focus();
  });

  loadNote();
})();
