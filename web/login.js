// Login and register page wiring (US-05 #5, US-06 #6). Talks to POST /auth/login and
// POST /auth/register through the gateway, keeps the session in sessionStorage, then goes
// back to the page in ?next=.
(function () {
  const { sessionFromLogin, saveSession, safeNextPath, fieldErrors, authErrorMessage } =
    window.SessionUtils;
  const { storage, currentSession, fetchJson, showFieldErrors } = window.Site;

  const next = safeNextPath(new URLSearchParams(window.location.search).get('next'));

  // Already logged in in this tab: nothing to do here.
  if (currentSession()) {
    window.location.replace(next);
    return;
  }

  const tabs = {
    login: { tab: document.getElementById('loginTab'), form: document.getElementById('loginForm') },
    register: { tab: document.getElementById('registerTab'), form: document.getElementById('registerForm') },
  };
  const loginError = document.getElementById('loginError');
  const registerError = document.getElementById('registerError');
  const notice = document.getElementById('authNotice');

  function showTab(name, { focus = true } = {}) {
    for (const [key, { tab, form }] of Object.entries(tabs)) {
      const selected = key === name;
      tab.setAttribute('aria-selected', String(selected));
      tab.tabIndex = selected ? 0 : -1;
      form.hidden = !selected;
    }
    if (focus) tabs[name].form.querySelector('input').focus();
  }

  for (const [name, { tab }] of Object.entries(tabs)) {
    tab.addEventListener('click', () => {
      notice.hidden = true;
      showTab(name);
    });
  }

  // Left/right arrows move between the two tabs, as in the WAI-ARIA tabs pattern.
  document.querySelector('[role="tablist"]').addEventListener('keydown', (event) => {
    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
    const other = tabs.login.tab.getAttribute('aria-selected') === 'true' ? 'register' : 'login';
    showTab(other, { focus: false });
    tabs[other].tab.focus();
  });

  function setError(box, message) {
    box.textContent = message || '';
    box.hidden = !message;
  }

  function setBusy(form, busy, label) {
    const button = form.querySelector('button[type="submit"]');
    if (!button.dataset.label) button.dataset.label = button.textContent;
    button.disabled = busy;
    button.textContent = busy ? label : button.dataset.label;
  }

  // Returns null on success (the browser is already leaving the page), or the failed result.
  async function logIn(email, password) {
    const result = await fetchJson('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!result.ok) return result;

    const session = sessionFromLogin(result.body);
    if (!session) return { ok: false, status: result.status, body: null };
    if (!saveSession(storage(), session)) {
      return { ok: false, status: result.status, body: { error: 'storage_unavailable' } };
    }
    window.location.assign(next);
    return null;
  }

  function storageMessage(result) {
    return result.body && result.body.error === 'storage_unavailable'
      ? 'browser นี้ไม่ยอมให้เก็บการเข้าสู่ระบบไว้ (อาจปิด storage ไว้) ลองเปิดหน้าต่างปกติแทน'
      : null;
  }

  tabs.login.form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const form = tabs.login.form;
    const data = new FormData(form);
    setError(loginError, '');
    showFieldErrors(form, {});
    setBusy(form, true, 'กำลังเข้าสู่ระบบ…');

    const failed = await logIn(String(data.get('email') || ''), String(data.get('password') || ''));
    if (!failed) return;
    setBusy(form, false);
    const first = showFieldErrors(form, fieldErrors(failed.body));
    setError(loginError, storageMessage(failed) || authErrorMessage(failed.status, failed.body));
    // Wrong email or password: clear the password and start typing it again
    if (failed.body && failed.body.error === 'invalid_credentials') {
      form.elements.password.value = '';
      form.elements.password.focus();
    } else if (first) {
      first.focus();
    }
  });

  tabs.register.form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const form = tabs.register.form;
    const data = new FormData(form);
    const email = String(data.get('email') || '');
    const password = String(data.get('password') || '');
    setError(registerError, '');
    showFieldErrors(form, {});
    setBusy(form, true, 'กำลังสมัครสมาชิก…');

    const result = await fetchJson('/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ display_name: String(data.get('display_name') || ''), email, password }),
    });
    if (!result.ok) {
      setBusy(form, false);
      const first = showFieldErrors(form, fieldErrors(result.body));
      setError(registerError, authErrorMessage(result.status, result.body));
      if (first) first.focus();
      return;
    }

    // Registered: log straight in with the same details, so the user is not asked twice.
    const failed = await logIn(email, password);
    if (!failed) return;
    setBusy(form, false);
    form.reset();
    tabs.login.form.elements.email.value = email;
    showTab('login');
    notice.textContent = 'สมัครสมาชิกสำเร็จแล้ว กรุณาเข้าสู่ระบบ';
    notice.hidden = false;
    setError(loginError, storageMessage(failed));
    tabs.login.form.elements.password.focus();
  });

  showTab(window.location.hash === '#register' ? 'register' : 'login', { focus: false });
})();
