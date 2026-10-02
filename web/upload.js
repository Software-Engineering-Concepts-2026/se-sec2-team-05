// Upload page wiring (US-08 #8, US-31 #31). Checks the login with GET /auth/me, checks the
// form with UploadUtils.validateUpload, sends it to POST /notes as multipart, then shows
// the one-time edit token.
(function () {
  const { authHeaders, clearSession, loginUrl, fieldErrors } = window.SessionUtils;
  const { validateUpload, uploadFields, uploadErrorMessage, searchUrlFor } = window.UploadUtils;
  const { storage, currentSession, fetchJson, showFieldErrors, renderNav } = window.Site;

  const form = document.getElementById('uploadForm');
  const uploaderLine = document.getElementById('uploaderLine');
  const errorBox = document.getElementById('uploadError');
  const done = document.getElementById('uploadDone');
  const doneTitle = document.getElementById('doneTitle');
  const doneNoteTitle = document.getElementById('doneNoteTitle');
  const doneUploader = document.getElementById('doneUploader');
  const doneSearchLink = document.getElementById('doneSearchLink');
  const tokenInput = document.getElementById('editToken');
  const copyButton = document.getElementById('copyToken');
  const copyStatus = document.getElementById('copyStatus');
  const submitButton = form.querySelector('button[type="submit"]');

  const loginPage = loginUrl('/upload.html');

  // Clears the session and offers a login link. Used when the token stops working.
  function sessionEnded(message) {
    clearSession(storage());
    renderNav();
    errorBox.replaceChildren(`${message} `);
    const link = document.createElement('a');
    link.href = loginPage;
    link.textContent = 'เข้าสู่ระบบ';
    errorBox.append(link);
    errorBox.hidden = false;
  }

  function showError(message) {
    errorBox.textContent = message || '';
    errorBox.hidden = !message;
  }

  // US-31: the note is credited to the account, so say whose name it will carry.
  function showUploader(user) {
    uploaderLine.replaceChildren('โน้ตจะแสดงชื่อผู้อัปโหลดเป็น ');
    const name = document.createElement('strong');
    name.textContent = user.display_name;
    uploaderLine.append(name, ' ตามบัญชีที่เข้าสู่ระบบ');
  }

  async function start() {
    const session = currentSession();
    if (!session) {
      window.location.replace(loginPage);
      return;
    }

    // The saved session may already be revoked (logout in another tab) or expired early.
    const me = await fetchJson('/auth/me', { headers: authHeaders(session) });
    if (me.status === 401) {
      clearSession(storage());
      window.location.replace(loginPage);
      return;
    }
    // auth-service down: still show the form; POST /notes will give the real answer.
    showUploader(me.ok && me.body ? me.body : session.user);
    form.hidden = false;
  }

  function readFields() {
    const data = new FormData(form);
    const fields = {};
    for (const [name, value] of data.entries()) {
      if (typeof value === 'string') fields[name] = value;
    }
    return fields;
  }

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    showError('');
    const fields = readFields();
    const file = form.elements.file.files[0] || null;

    const errors = validateUpload(fields, file);
    const first = showFieldErrors(form, errors);
    if (first) {
      showError('ข้อมูลยังไม่ถูกต้อง แก้ช่องที่มีข้อความสีแดงแล้วลองใหม่');
      first.focus();
      return;
    }

    const session = currentSession();
    if (!session) {
      sessionEnded('เซสชันหมดอายุแล้ว กรุณาเข้าสู่ระบบใหม่ก่อนอัปโหลด');
      return;
    }

    const body = new FormData();
    for (const [name, value] of Object.entries(uploadFields(fields))) body.append(name, value);
    body.append('file', file, file.name);

    submitButton.disabled = true;
    submitButton.textContent = 'กำลังอัปโหลด…';
    // No Content-Type header: the browser sets multipart/form-data with its boundary.
    const result = await fetchJson('/notes', { method: 'POST', headers: authHeaders(session), body });
    submitButton.disabled = false;
    submitButton.textContent = 'อัปโหลด';

    if (!result.ok || !result.body) {
      if (result.status === 401) {
        sessionEnded(uploadErrorMessage(401, { error: 'unauthorized' }));
        return;
      }
      const serverFirst = showFieldErrors(form, fieldErrors(result.body));
      showError(uploadErrorMessage(result.status, result.body));
      if (serverFirst) serverFirst.focus();
      return;
    }

    showDone(result.body);
  });

  function showDone(note) {
    form.hidden = true;
    uploaderLine.hidden = true;
    doneNoteTitle.textContent = note.title;
    doneUploader.textContent = note.uploader_name;
    doneSearchLink.href = searchUrlFor(note);
    tokenInput.value = note.edit_token || '';
    copyStatus.textContent = '';
    done.hidden = false;
    doneTitle.focus();
  }

  copyButton.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(tokenInput.value);
      copyStatus.textContent = 'คัดลอกแล้ว';
    } catch {
      // Clipboard API needs a secure context (https or localhost). Select it for Ctrl+C instead.
      tokenInput.select();
      copyStatus.textContent = 'คัดลอกอัตโนมัติไม่ได้ เลือกข้อความไว้ให้แล้ว กด Ctrl+C';
    }
  });

  document.getElementById('uploadAnother').addEventListener('click', () => {
    // The token is only on screen while this box is open
    tokenInput.value = '';
    done.hidden = true;
    form.reset();
    showFieldErrors(form, {});
    uploaderLine.hidden = false;
    form.hidden = false;
    form.elements.title.focus();
  });

  start();
})();
