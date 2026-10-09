// GW-01 to GW-06 (test plan 2.26): the Vercel side of the gateway login check (ADR-014).
// web/nginx.conf is checked against the same gateway/cases.json by src/tests/test_gateway_rules.py.
const test = require('node:test');
const assert = require('node:assert/strict');
const { cases } = require('./cases.json');
const { classify, needsLogin, checkRequest } = require('./rules.js');

const BASE = 'https://noteshare.example';

function caseHeaders(c) {
  return new Headers(c.note_token ? { 'X-Note-Token': 'some-token' } : {});
}

function request(method, path, headers = {}) {
  return new Request(BASE + path, { method, headers });
}

// Records each call and answers with `status` (or throws when status is 'down').
function fakeAuth(status) {
  const calls = [];
  const fetchImpl = async (url, init) => {
    calls.push({ url: String(url), headers: init.headers });
    if (status === 'down') throw new TypeError('fetch failed');
    return new Response(status === 200 ? '{"id": 1}' : '{"error": "unauthorized"}', { status });
  };
  return { calls, fetchImpl };
}

test('GW-01 every route in cases.json gets the expected rule and check', () => {
  for (const c of cases) {
    const where = `${c.method} ${c.path}${c.note_token ? ' + X-Note-Token' : ''}`;
    assert.equal(classify(c.method, c.path), c.rule, where);
    assert.equal(needsLogin(c.method, c.path, caseHeaders(c)), c.check === 'login', where);
  }
});

test('GW-01 the method is matched case-insensitively and plain header objects work', () => {
  assert.equal(classify('post', '/notes'), 'login');
  assert.equal(needsLogin('PATCH', '/notes/3', { 'x-note-token': 'abc' }), false);
  assert.equal(needsLogin('PATCH', '/notes/3', {}), true);
  // An empty X-Note-Token is not a token.
  assert.equal(needsLogin('DELETE', '/notes/3', new Headers({ 'X-Note-Token': '' })), true);
});

test('GW-02 open routes and edit-token calls never ask auth-service', async () => {
  const auth = fakeAuth(401);
  for (const c of cases.filter((x) => x.check === 'skip')) {
    const result = await checkRequest(request(c.method, c.path, Object.fromEntries(caseHeaders(c))), auth.fetchImpl);
    assert.equal(result, undefined, `${c.method} ${c.path}`);
  }
  assert.equal(auth.calls.length, 0);
});

test('GW-03 a protected route without Authorization gets 401 JSON without calling auth-service', async () => {
  const auth = fakeAuth(200);
  const result = await checkRequest(request('GET', '/notes/mine'), auth.fetchImpl);
  assert.equal(result.status, 401);
  assert.deepEqual(await result.json(), { error: 'unauthorized' });
  assert.equal(result.headers.get('www-authenticate'), 'Bearer');
  assert.equal(auth.calls.length, 0);
});

test('GW-04 a valid token passes; the call goes to this deployment\'s /auth/me with the right headers', async () => {
  const auth = fakeAuth(200);
  const result = await checkRequest(
    request('POST', '/notes/12/comments?x=1', {
      Authorization: 'Bearer good',
      Cookie: '_vercel_jwt=abc',
      'X-Vercel-Protection-Bypass': 'bypass',
      'X-Note-Token': 'not forwarded',
    }),
    auth.fetchImpl,
  );
  assert.equal(result, undefined);
  assert.equal(auth.calls.length, 1);
  assert.equal(auth.calls[0].url, `${BASE}/auth/me`);
  const sent = auth.calls[0].headers;
  assert.equal(sent.get('authorization'), 'Bearer good');
  assert.equal(sent.get('cookie'), '_vercel_jwt=abc');
  assert.equal(sent.get('x-vercel-protection-bypass'), 'bypass');
  assert.equal(sent.get('x-note-token'), null);
});

test('GW-05 a bad or revoked token gets 401 JSON', async () => {
  const result = await checkRequest(request('GET', '/reports', { Authorization: 'Bearer old' }), fakeAuth(401).fetchImpl);
  assert.equal(result.status, 401);
  assert.deepEqual(await result.json(), { error: 'unauthorized' });
});

test('GW-06 auth-service down or failing gets 503 auth_unavailable, never a pass', async () => {
  for (const status of ['down', 500, 502, 403]) {
    const result = await checkRequest(
      request('PUT', '/notes/12/rating', { Authorization: 'Bearer good' }),
      fakeAuth(status).fetchImpl,
    );
    assert.equal(result.status, 503, String(status));
    assert.deepEqual(await result.json(), { error: 'auth_unavailable' });
  }
});
