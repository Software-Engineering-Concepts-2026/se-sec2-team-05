// DOM code shared by every page: the top nav bar, sessionStorage access, fetchJson and
// field error display. The logic it relies on (what counts as logged in, where ?next= may
// point) lives in session-utils.js and is unit tested there.
(function () {
  const { loadSession, clearSession, authHeaders, loginUrl } = window.SessionUtils;

  // window.sessionStorage itself can throw (blocked storage, sandboxed frame). null is fine
  // to pass on: the SessionUtils functions treat a failing storage as "not logged in".
  function storage() {
    try {
      return window.sessionStorage;
    } catch {
      return null;
    }
  }

  function currentSession() {
    return loadSession(storage());
  }

  async function fetchJson(url, options = {}) {
    let response;
    try {
      response = await fetch(url, {
        ...options,
        headers: { Accept: 'application/json', ...(options.headers || {}) },
      });
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

  // Puts each reason under its field (<span data-error-for="name">) and marks the input
  // aria-invalid. Returns the first input with an error, so the page can focus it.
  function showFieldErrors(form, errors) {
    let first = null;
    for (const box of form.querySelectorAll('[data-error-for]')) {
      const name = box.dataset.errorFor;
      const reason = errors[name];
      box.textContent = reason || '';
      box.hidden = !reason;
      const input = form.elements[name];
      if (!input) continue;
      if (reason) {
        input.setAttribute('aria-invalid', 'true');
        if (!first) first = input;
      } else {
        input.removeAttribute('aria-invalid');
      }
    }
    return first;
  }

  // ---- Top nav bar ----

  const nav = document.getElementById('siteNav');

  function link(href, text) {
    const a = document.createElement('a');
    a.href = href;
    a.textContent = text;
    if (href === window.location.pathname || (href === '/' && window.location.pathname === '/index.html')) {
      a.setAttribute('aria-current', 'page');
    }
    return a;
  }

  async function logout(session) {
    // Revoke the session on the server too (ADR-005), so the token stops working right away.
    // The tab forgets it either way: a failed request must not leave the user logged in here.
    await fetchJson('/auth/logout', { method: 'POST', headers: authHeaders(session) });
    clearSession(storage());
    // pages that only work logged in go back to the search page
    if (['/upload.html', '/profile.html', '/admin.html'].includes(window.location.pathname)) {
      window.location.assign('/');
    } else {
      renderNav();
    }
  }

  // Built with textContent, not innerHTML, because display_name is typed in by the user.
  function renderNav() {
    if (!nav) return;
    const session = currentSession();
    const left = document.createElement('div');
    left.className = 'nav-links';
    const brand = link('/', 'NoteShare');
    brand.className = 'nav-brand';
    brand.removeAttribute('aria-current');
    left.append(brand, link('/', 'ค้นหาโน้ต'), link('/upload.html', 'อัปโหลดโน้ต'), link('/stats.html', 'สถิติ'));
    if (session) left.append(link('/profile.html', 'โปรไฟล์'));

    const right = document.createElement('div');
    right.className = 'nav-user';
    if (session) {
      const name = document.createElement('span');
      name.className = 'nav-name';
      name.textContent = session.user.display_name;
      const out = document.createElement('button');
      out.type = 'button';
      out.className = 'secondary-btn';
      out.textContent = 'ออกจากระบบ';
      out.addEventListener('click', () => {
        out.disabled = true;
        logout(session);
      });
      right.append(name, out);
    } else if (window.location.pathname !== '/login.html') {
      const login = link(loginUrl(window.location.pathname + window.location.search), 'เข้าสู่ระบบ');
      login.className = 'primary-btn';
      right.append(login);
    }
    nav.replaceChildren(left, right);
  }

  renderNav();

  window.Site = { storage, currentSession, fetchJson, showFieldErrors, renderNav };
})();
