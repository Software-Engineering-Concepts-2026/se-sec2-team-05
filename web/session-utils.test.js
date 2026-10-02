const test = require('node:test');
const assert = require('node:assert/strict');
const {
  SESSION_KEY,
  sessionFromLogin,
  saveSession,
  loadSession,
  clearSession,
  authHeaders,
  safeNextPath,
  loginUrl,
  fieldErrors,
  authErrorMessage,
} = require('./session-utils.js');

// A stand-in for window.sessionStorage
function memoryStorage(initial = {}) {
  const data = { ...initial };
  return {
    data,
    getItem: (key) => (key in data ? data[key] : null),
    setItem: (key, value) => {
      data[key] = String(value);
    },
    removeItem: (key) => {
      delete data[key];
    },
  };
}

// Storage that refuses everything, like a browser with site data blocked
const blockedStorage = {
  getItem() {
    throw new Error('SecurityError');
  },
  setItem() {
    throw new Error('QuotaExceededError');
  },
  removeItem() {
    throw new Error('SecurityError');
  },
};

const NOW = Date.parse('2026-10-02T10:00:00+00:00');

const loginBody = {
  access_token: 'header.payload.signature',
  token_type: 'Bearer',
  expires_at: '2026-10-02T18:00:00+00:00',
  user: { id: 4, email: 'somchai@up.ac.th', display_name: 'Somchai', created_at: '2026-10-01T00:00:00+00:00' },
};

test('sessionFromLogin keeps the token, expiry and the user name from POST /auth/login', () => {
  assert.deepEqual(sessionFromLogin(loginBody), {
    token: 'header.payload.signature',
    expiresAt: '2026-10-02T18:00:00+00:00',
    user: { id: 4, email: 'somchai@up.ac.th', display_name: 'Somchai' },
  });
});

test('sessionFromLogin rejects a body with a missing token, expiry or user', () => {
  assert.equal(sessionFromLogin(null), null);
  assert.equal(sessionFromLogin({ ...loginBody, access_token: '' }), null);
  assert.equal(sessionFromLogin({ ...loginBody, expires_at: 'soon' }), null);
  assert.equal(sessionFromLogin({ ...loginBody, user: null }), null);
});

test('saveSession then loadSession gives the same session back before it expires', () => {
  const storage = memoryStorage();
  const session = sessionFromLogin(loginBody);
  assert.equal(saveSession(storage, session), true);
  assert.deepEqual(loadSession(storage, NOW), session);
});

test('loadSession removes an expired session, so every page sees the user as logged out', () => {
  const storage = memoryStorage();
  saveSession(storage, sessionFromLogin(loginBody));
  assert.equal(loadSession(storage, Date.parse('2026-10-02T18:00:00+00:00')), null);
  assert.equal(storage.getItem(SESSION_KEY), null);
});

test('loadSession removes a session it cannot read', () => {
  for (const raw of ['not json', '{}', JSON.stringify({ token: 'x', expiresAt: 'later', user: { display_name: 'A' } })]) {
    const storage = memoryStorage({ [SESSION_KEY]: raw });
    assert.equal(loadSession(storage, NOW), null, raw);
    assert.equal(storage.getItem(SESSION_KEY), null, raw);
  }
});

test('blocked or missing storage means not logged in, and saving reports failure', () => {
  assert.equal(loadSession(blockedStorage, NOW), null);
  assert.equal(loadSession(null, NOW), null);
  assert.equal(saveSession(blockedStorage, sessionFromLogin(loginBody)), false);
  assert.doesNotThrow(() => clearSession(blockedStorage));
});

test('clearSession forgets the session (logout)', () => {
  const storage = memoryStorage();
  saveSession(storage, sessionFromLogin(loginBody));
  clearSession(storage);
  assert.equal(loadSession(storage, NOW), null);
});

test('authHeaders sends the token as a Bearer header, and nothing when logged out', () => {
  assert.deepEqual(authHeaders(sessionFromLogin(loginBody)), {
    Authorization: 'Bearer header.payload.signature',
  });
  assert.deepEqual(authHeaders(null), {});
});

test('safeNextPath allows only this site\'s own pages and keeps their query string', () => {
  assert.equal(safeNextPath('/upload.html'), '/upload.html');
  assert.equal(safeNextPath('/?q=CS201&year_level=2'), '/?q=CS201&year_level=2');
  assert.equal(safeNextPath('/index.html'), '/index.html');
});

test('safeNextPath sends anything else to the search page (no open redirect)', () => {
  for (const raw of [
    null,
    '',
    'upload.html',
    'https://evil.example/',
    '//evil.example/upload.html',
    '/\\evil.example',
    'javascript:alert(1)',
    '/login.html',
    '/notes/1/download',
  ]) {
    assert.equal(safeNextPath(raw), '/', String(raw));
  }
});

test('loginUrl carries the page to come back to', () => {
  assert.equal(loginUrl('/upload.html'), '/login.html?next=%2Fupload.html');
  assert.equal(loginUrl('https://evil.example/'), '/login.html?next=%2F');
});

test('fieldErrors reads the per-field reasons of a validation_failed body', () => {
  assert.deepEqual(
    fieldErrors({ error: 'validation_failed', fields: { email: 'รูปแบบอีเมลไม่ถูกต้อง', password: 'จำเป็นต้องกรอก' } }),
    { email: 'รูปแบบอีเมลไม่ถูกต้อง', password: 'จำเป็นต้องกรอก' },
  );
  assert.deepEqual(fieldErrors({ error: 'invalid_credentials' }), {});
  assert.deepEqual(fieldErrors(null), {});
  assert.deepEqual(fieldErrors({ fields: ['email'] }), {});
});

test('authErrorMessage covers each auth-service error', () => {
  assert.equal(
    authErrorMessage(401, { error: 'invalid_credentials', message: 'อีเมลหรือรหัสผ่านไม่ถูกต้อง' }),
    'อีเมลหรือรหัสผ่านไม่ถูกต้อง',
  );
  assert.match(authErrorMessage(409, { error: 'email_taken' }), /สมัครสมาชิกไว้แล้ว/);
  assert.match(authErrorMessage(400, { error: 'validation_failed', fields: {} }), /ช่องที่มีข้อความสีแดง/);
  assert.match(authErrorMessage(401, { error: 'unauthorized' }), /เข้าสู่ระบบใหม่/);
  assert.match(authErrorMessage(503, { error: 'auth_unavailable' }), /ไม่พร้อมใช้งาน/);
  assert.match(authErrorMessage(0, null), /เชื่อมต่อเซิร์ฟเวอร์ไม่ได้/);
  assert.match(authErrorMessage(502, null), /HTTP 502/);
});
