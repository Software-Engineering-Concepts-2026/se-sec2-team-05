// Profile page wiring (web/profile.html, Issue #85): stat cards and "my notes" from
// GET /notes/mine, edit (PATCH) and delete (DELETE) by login (ADR-008), and the favorites list
// from GET /notes/favorites. The pure parts live in profile-utils.js; this file only touches
// the DOM and fetch.
(function () {
  const { authHeaders, clearSession, loginUrl, fieldErrors } = window.SessionUtils;
  const { PAGE_SIZE, hasMore } = window.SearchUtils;
  const { validateMetadata } = window.UploadUtils;
  const {
    summaryCards,
    renderMyNoteRow,
    renderFavoriteRow,
    editFormValues,
    changedFields,
    profileErrorMessage,
  } = window.ProfileUtils;
  const { storage, currentSession, fetchJson, showFieldErrors, renderNav } = window.Site;

  const loginPage = loginUrl('/profile.html');
  const session = currentSession();
  if (!session) {
    window.location.replace(loginPage);
    return;
  }

  const byId = (id) => document.getElementById(id);
  const profileName = byId('profileName');
  const profileEmail = byId('profileEmail');
  const adminLink = byId('adminLink');
  const profileError = byId('profileError');
  const profileStatus = byId('profileStatus');
  const profileStats = byId('profileStats');
  const myNotesStatus = byId('myNotesStatus');
  const myNotesList = byId('myNotesList');
  const myNotesMore = byId('myNotesMore');
  const favoritesStatus = byId('favoritesStatus');
  const favoritesList = byId('favoritesList');
  const favoritesMore = byId('favoritesMore');
  const editDialog = byId('editDialog');
  const editForm = byId('editForm');
  const editError = byId('editError');
  const deleteDialog = byId('deleteDialog');
  const deleteForm = byId('deleteForm');
  const deleteNoteTitle = byId('deleteNoteTitle');
  const deleteError = byId('deleteError');

  const myNotes = new Map();
  const favorites = new Map();
  let myOffset = 0;
  let favoritesOffset = 0;
  let editing = null;
  let deleting = null;
  let dialogOpener = null;

  function say(el, message) {
    el.textContent = message || '';
    el.hidden = !message;
  }

  // The token stopped working (logout in another tab, revoked). The lists need a login, so go
  // to the login page; it brings the user back here afterwards.
  function loginAgain() {
    clearSession(storage());
    window.location.replace(loginPage);
  }

  // Inside a dialog the user may have typed changes, so offer a link instead of leaving.
  function sessionEnded(el) {
    clearSession(storage());
    renderNav();
    el.replaceChildren(profileErrorMessage(401, { error: 'unauthorized' }), ' ');
    const link = document.createElement('a');
    link.href = loginPage;
    link.textContent = 'เข้าสู่ระบบ';
    el.append(link);
    el.hidden = false;
  }

  function renderStats(summary) {
    profileStats.replaceChildren(
      ...summaryCards(summary).map((card) => {
        const item = document.createElement('li');
        item.className = 'stat-card';
        const value = document.createElement('span');
        value.className = 'stat-num';
        value.textContent = card.value;
        const label = document.createElement('span');
        label.className = 'stat-label';
        label.textContent = card.label;
        item.append(value, label);
        return item;
      })
    );
    profileStats.setAttribute('aria-busy', 'false');
  }

  // ---- My notes (Issue #82 API) ----

  async function loadMyNotes({ append = false } = {}) {
    const offset = append ? myOffset : 0;
    myNotesMore.disabled = true;
    const result = await fetchJson(`/notes/mine?limit=${PAGE_SIZE}&offset=${offset}`, {
      headers: authHeaders(session),
    });
    myNotesMore.disabled = false;
    if (result.status === 401) {
      loginAgain();
      return;
    }
    if (!result.ok || !result.body || !Array.isArray(result.body.items)) {
      say(myNotesStatus, profileErrorMessage(result.status, result.body));
      return;
    }
    if (!append) {
      myNotes.clear();
      myNotesList.innerHTML = '';
    }
    renderStats(result.body.summary);
    const items = result.body.items;
    for (const note of items) myNotes.set(String(note.id), note);
    myNotesList.insertAdjacentHTML('beforeend', items.map(renderMyNoteRow).join(''));
    myOffset = offset + items.length;
    say(myNotesStatus, myNotes.size ? '' : 'ยังไม่ได้อัปโหลดโน้ต');
    myNotesMore.hidden = !hasMore(items.length);
  }

  // ---- Favorites (US-15) ----

  async function loadFavorites({ append = false } = {}) {
    const offset = append ? favoritesOffset : 0;
    favoritesMore.disabled = true;
    const result = await fetchJson(`/notes/favorites?limit=${PAGE_SIZE}&offset=${offset}`, {
      headers: authHeaders(session),
    });
    favoritesMore.disabled = false;
    if (result.status === 401) {
      loginAgain();
      return;
    }
    if (!result.ok || !result.body || !Array.isArray(result.body.items)) {
      say(favoritesStatus, profileErrorMessage(result.status, result.body));
      return;
    }
    if (!append) {
      favorites.clear();
      favoritesList.innerHTML = '';
    }
    const items = result.body.items;
    for (const note of items) favorites.set(String(note.id), note);
    favoritesList.insertAdjacentHTML('beforeend', items.map(renderFavoriteRow).join(''));
    favoritesOffset = offset + items.length;
    showFavoritesEmpty();
    favoritesMore.hidden = !hasMore(items.length);
  }

  function showFavoritesEmpty() {
    say(favoritesStatus, favorites.size ? '' : 'ยังไม่มีรายการโปรด กดปุ่มบันทึกในหน้าโน้ตเพื่อเก็บไว้ที่นี่');
  }

  function removeRow(list, id) {
    const row = list.querySelector(`[data-note-id="${CSS.escape(id)}"]`);
    if (row) row.remove();
  }

  favoritesList.addEventListener('click', async (event) => {
    const button = event.target.closest('[data-unfavorite]');
    if (!button) return;
    const id = button.dataset.unfavorite;
    button.disabled = true;
    const result = await fetchJson(`/notes/${encodeURIComponent(id)}/favorite`, {
      method: 'DELETE',
      headers: authHeaders(session),
    });
    if (result.status === 401) {
      loginAgain();
      return;
    }
    // 404 = the note itself is gone, so it is no longer a favorite either
    if (!result.ok && result.status !== 404) {
      button.disabled = false;
      say(profileError, profileErrorMessage(result.status, result.body));
      return;
    }
    favorites.delete(id);
    removeRow(favoritesList, id);
    favoritesOffset = Math.max(0, favoritesOffset - 1);
    showFavoritesEmpty();
    say(profileStatus, 'เอาออกจากรายการโปรดแล้ว');
  });

  // ---- Dialogs ----

  function openDialog(dialog, opener) {
    dialogOpener = opener;
    say(profileStatus, '');
    say(profileError, '');
    dialog.showModal();
  }

  function restoreFocus() {
    if (dialogOpener && dialogOpener.isConnected) dialogOpener.focus({ preventScroll: true });
    dialogOpener = null;
  }

  // Focus goes back right away instead of waiting for the 'close' event, which the browser
  // may deliver late. The listener still covers Esc, which closes the dialog by itself.
  function closeDialog(dialog) {
    dialog.close();
    restoreFocus();
  }

  for (const dialog of [editDialog, deleteDialog]) {
    dialog.addEventListener('click', (event) => {
      // the backdrop click lands on the <dialog> itself
      if (event.target === dialog || event.target.closest('[data-close-dialog]')) closeDialog(dialog);
    });
    dialog.addEventListener('close', restoreFocus);
  }

  // ---- Edit (US-19, by login per ADR-008) ----

  myNotesList.addEventListener('click', (event) => {
    const editButton = event.target.closest('[data-edit-note]');
    if (editButton) {
      editing = myNotes.get(editButton.dataset.editNote);
      if (!editing) return;
      const values = editFormValues(editing);
      for (const [name, value] of Object.entries(values)) editForm.elements[name].value = value;
      showFieldErrors(editForm, {});
      say(editError, '');
      openDialog(editDialog, editButton);
      editForm.elements.title.focus();
      return;
    }
    const deleteButton = event.target.closest('[data-delete-note]');
    if (deleteButton) {
      deleting = myNotes.get(deleteButton.dataset.deleteNote);
      if (!deleting) return;
      deleteNoteTitle.textContent = deleting.title;
      say(deleteError, '');
      openDialog(deleteDialog, deleteButton);
    }
  });

  function readEditForm() {
    const fields = {};
    for (const [name, value] of new FormData(editForm).entries()) fields[name] = String(value);
    return fields;
  }

  editForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const fields = readEditForm();
    const first = showFieldErrors(editForm, validateMetadata(fields));
    if (first) {
      say(editError, profileErrorMessage(400, { error: 'validation_failed' }));
      first.focus();
      return;
    }
    const changed = changedFields(editing, fields);
    if (Object.keys(changed).length === 0) {
      say(editError, profileErrorMessage(400, { error: 'no_fields_to_update' }));
      return;
    }

    const submit = editForm.querySelector('[type="submit"]');
    submit.disabled = true;
    // PATCH /notes/<id> reads form fields (request.form), like POST /notes
    const result = await fetchJson(`/notes/${editing.id}`, {
      method: 'PATCH',
      headers: { ...authHeaders(session), 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams(changed),
    });
    submit.disabled = false;

    if (result.status === 401) {
      sessionEnded(editError);
      return;
    }
    if (!result.ok || !result.body) {
      const serverFirst = showFieldErrors(editForm, fieldErrors(result.body));
      say(editError, profileErrorMessage(result.status, result.body));
      if (serverFirst) serverFirst.focus();
      return;
    }

    const id = String(editing.id);
    const updated = { ...editing, ...result.body };
    myNotes.set(id, updated);
    const row = myNotesList.querySelector(`[data-note-id="${CSS.escape(id)}"]`);
    if (row) row.outerHTML = renderMyNoteRow(updated);
    if (favorites.has(id)) {
      favorites.set(id, { ...favorites.get(id), ...result.body });
      const favoriteRow = favoritesList.querySelector(`[data-note-id="${CSS.escape(id)}"]`);
      if (favoriteRow) favoriteRow.outerHTML = renderFavoriteRow(favorites.get(id));
    }
    // the old row (and its button) was replaced, so return focus to the new one
    dialogOpener = myNotesList.querySelector(`[data-edit-note="${CSS.escape(id)}"]`);
    closeDialog(editDialog);
    say(profileStatus, 'บันทึกการแก้ไขแล้ว');
  });

  // ---- Delete (US-20, by login per ADR-008) ----

  deleteForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const submit = deleteForm.querySelector('[type="submit"]');
    submit.disabled = true;
    const result = await fetchJson(`/notes/${deleting.id}`, {
      method: 'DELETE',
      headers: authHeaders(session),
    });
    submit.disabled = false;
    if (result.status === 401) {
      sessionEnded(deleteError);
      return;
    }
    // 404 = already deleted (another tab), which is what the user asked for
    if (!result.ok && result.status !== 404) {
      say(deleteError, profileErrorMessage(result.status, result.body));
      return;
    }
    const id = String(deleting.id);
    dialogOpener = null;
    closeDialog(deleteDialog);
    if (favorites.has(id)) {
      favorites.delete(id);
      removeRow(favoritesList, id);
      showFavoritesEmpty();
    }
    say(profileStatus, `ลบโน้ต "${deleting.title}" แล้ว`);
    // reload from the top: the summary counts change and the next page shifts by one
    await loadMyNotes();
    profileStatus.focus();
  });

  // ---- Link to the admin page (Issues #17, #18) ----

  // Who is an admin is set on the server (ADMIN_USER_IDS of notes-service) and no API says it,
  // so ask GET /reports once: only admins get 200. Everyone else gets 403 and sees no link.
  async function showAdminLink() {
    const result = await fetchJson('/reports', { headers: authHeaders(session) });
    adminLink.hidden = !result.ok;
  }

  myNotesMore.addEventListener('click', () => loadMyNotes({ append: true }));
  favoritesMore.addEventListener('click', () => loadFavorites({ append: true }));

  profileName.textContent = session.user.display_name;
  profileEmail.textContent = session.user.email || '';
  document.title = `${session.user.display_name} - NoteShare`;
  loadMyNotes();
  loadFavorites();
  showAdminLink();
})();
