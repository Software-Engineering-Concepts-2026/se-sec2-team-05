// Pure helpers for login state in the NoteShare web app (login.html, upload.html, nav.js).
// Storage is passed in rather than read from window, so session-utils.test.js can run them
// under `node --test` with a plain object standing in for sessionStorage.
// Same loading pattern as search-utils.js: window.SessionUtils in the browser, module.exports
// under Node.
(function (exportTo) {
  // The token lives in sessionStorage (one tab, gone when the tab closes), not localStorage.
  // Reasons are in web/README.md, "เก็บ token ไว้ที่ไหน".
  const SESSION_KEY = 'noteshare.session';

  // Pages a login may send the user back to. Anything else falls back to the search page,
  // so ?next= can never point the browser at another site.
  const NEXT_PAGES = ['/', '/index.html', '/upload.html', '/note.html', '/profile.html', '/admin.html'];
  const DEFAULT_NEXT = '/';

  // POST /auth/login body -> the session the pages keep. Returns null for a body that is
  // missing a field, so a broken response never ends up half-saved.
  function sessionFromLogin(body) {
    if (!body || typeof body.access_token !== 'string' || !body.access_token) return null;
    if (Number.isNaN(Date.parse(body.expires_at))) return null;
    const user = body.user;
    if (!user || typeof user.display_name !== 'string') return null;
    return {
      token: body.access_token,
      expiresAt: body.expires_at,
      user: { id: user.id, email: user.email, display_name: user.display_name },
    };
  }

  function saveSession(storage, session) {
    try {
      storage.setItem(SESSION_KEY, JSON.stringify(session));
      return true;
    } catch {
      // Storage can be off or full (private mode). The caller tells the user login did not stick.
      return false;
    }
  }

  function clearSession(storage) {
    try {
      storage.removeItem(SESSION_KEY);
    } catch {
      // nothing saved, nothing to clear
    }
  }

  // The saved session, or null when there is none, it is unreadable, or it has expired.
  // An expired or unreadable one is removed, so every page agrees the user is logged out.
  function loadSession(storage, now = Date.now()) {
    let raw;
    try {
      raw = storage.getItem(SESSION_KEY);
    } catch {
      return null;
    }
    if (!raw) return null;

    let session;
    try {
      session = JSON.parse(raw);
    } catch {
      session = null;
    }
    const expires = session ? Date.parse(session.expiresAt) : NaN;
    const valid =
      session &&
      typeof session.token === 'string' &&
      session.token &&
      session.user &&
      typeof session.user.display_name === 'string' &&
      !Number.isNaN(expires);
    if (!valid || expires <= now) {
      clearSession(storage);
      return null;
    }
    return session;
  }

  function authHeaders(session) {
    return session ? { Authorization: `Bearer ${session.token}` } : {};
  }

  // ?next= value -> a same-site page to open after login. Only the pages in NEXT_PAGES are
  // allowed. Their query string is kept, so a search survives the round trip.
  function safeNextPath(raw) {
    if (typeof raw !== 'string' || !raw.startsWith('/') || raw.startsWith('//') || raw.includes('\\')) {
      return DEFAULT_NEXT;
    }
    let url;
    try {
      url = new URL(raw, 'http://noteshare.invalid');
    } catch {
      return DEFAULT_NEXT;
    }
    if (url.origin !== 'http://noteshare.invalid' || !NEXT_PAGES.includes(url.pathname)) {
      return DEFAULT_NEXT;
    }
    return url.pathname + url.search;
  }

  function loginUrl(next) {
    return `/login.html?next=${encodeURIComponent(safeNextPath(next))}`;
  }

  // validation_failed bodies carry {fields: {name: reason}}. Anything else -> no field errors.
  function fieldErrors(body) {
    const fields = body && body.fields;
    if (!fields || typeof fields !== 'object' || Array.isArray(fields)) return {};
    const errors = {};
    for (const [name, reason] of Object.entries(fields)) errors[name] = String(reason);
    return errors;
  }

  // API error -> one line for the top of the form. Field-level reasons come from fieldErrors.
  function authErrorMessage(status, body) {
    const code = body && body.error;
    if (code === 'invalid_credentials') return (body && body.message) || 'อีเมลหรือรหัสผ่านไม่ถูกต้อง';
    if (code === 'email_taken') return 'อีเมลนี้สมัครสมาชิกไว้แล้ว ลองเข้าสู่ระบบแทน';
    if (code === 'validation_failed') return 'ข้อมูลยังไม่ถูกต้อง แก้ช่องที่มีข้อความสีแดงแล้วลองใหม่';
    if (code === 'unauthorized') return 'เซสชันหมดอายุหรือออกจากระบบไปแล้ว กรุณาเข้าสู่ระบบใหม่';
    if (code === 'auth_unavailable') return 'ระบบยืนยันตัวตนไม่พร้อมใช้งานตอนนี้ ลองใหม่อีกสักครู่';
    if (status === 0) return 'เชื่อมต่อเซิร์ฟเวอร์ไม่ได้ ตรวจการเชื่อมต่อแล้วลองใหม่';
    return `เกิดข้อผิดพลาดจากเซิร์ฟเวอร์ (HTTP ${status}) ลองใหม่อีกครั้ง`;
  }

  const SessionUtils = {
    SESSION_KEY,
    NEXT_PAGES,
    sessionFromLogin,
    saveSession,
    loadSession,
    clearSession,
    authHeaders,
    safeNextPath,
    loginUrl,
    fieldErrors,
    authErrorMessage,
  };

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = SessionUtils;
  } else {
    exportTo.SessionUtils = SessionUtils;
  }
})(typeof window !== 'undefined' ? window : globalThis);
