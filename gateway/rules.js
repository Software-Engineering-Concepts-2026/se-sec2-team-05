// Which API requests the gateway must log in before forwarding (ADR-014).
// gateway/proxy.ts (Vercel Routing Middleware) uses this file. web/nginx.conf has the same table
// as two `map` blocks for docker compose; src/tests/test_gateway_rules.py checks both against
// gateway/cases.json and checks that every route of notes/stats/auth-service is listed there.
// CommonJS like web/*.js: Vercel builds the middleware as CommonJS and `node --test` loads it as is.
//
// The gateway only answers "is there a valid login?". Everything else (admin role, owner of
// the note, edit token) is still decided by the service, so a route listed here is checked twice.

// Routes that need a valid login. Paths are matched on the decoded path without the query.
const LOGIN_RULES = [
  { methods: ['POST'], path: /^\/notes$/ },
  { methods: ['GET'], path: /^\/notes\/(favorites|mine)$/ },
  { methods: ['POST', 'DELETE'], path: /^\/notes\/\d+\/favorite$/ },
  { methods: ['POST'], path: /^\/notes\/\d+\/thanks$/ },
  { methods: ['PUT'], path: /^\/notes\/\d+\/rating$/ },
  { methods: ['POST'], path: /^\/notes\/\d+\/(reports|comments)$/ },
  { methods: ['DELETE'], path: /^\/notes\/\d+\/comments\/\d+$/ },
  { methods: ['GET'], path: /^\/notes\/\d+\/stats$/ },
  // Admin pages: the gateway checks the login only, notes-service checks ADMIN_USER_IDS.
  { methods: ['GET'], path: /^\/reports$/ },
  { methods: ['DELETE'], path: /^\/reports\/\d+(\/note)?$/ },
];

// Edit or delete a note: the logged-in owner (ADR-008) or anyone with the note's edit token (ADR-004).
const EDIT_RULE = { methods: ['PATCH', 'DELETE'], path: /^\/notes\/\d+$/ };

const NOTE_TOKEN_HEADER = 'x-note-token';

function matches(rule, method, path) {
  return rule.methods.includes(method) && rule.path.test(path);
}

// 'login' | 'edit' | 'open'
function classify(method, path) {
  const verb = String(method).toUpperCase();
  if (LOGIN_RULES.some((rule) => matches(rule, verb, path))) return 'login';
  if (matches(EDIT_RULE, verb, path)) return 'edit';
  return 'open';
}

// true = ask auth-service before forwarding. `headers` is a Headers object or a plain object.
function needsLogin(method, path, headers) {
  const rule = classify(method, path);
  if (rule === 'login') return true;
  if (rule !== 'edit') return false;
  const token = headers && typeof headers.get === 'function'
    ? headers.get(NOTE_TOKEN_HEADER)
    : headers && headers[NOTE_TOKEN_HEADER];
  // ยกเว้นชั่วคราว: แก้/ลบด้วยรหัสแก้ไข (X-Note-Token) ยังไม่ต้อง login ให้ notes-service ตรวจรหัสเอง
  // ลบข้อยกเว้นนี้ออกเมื่อเลิกใช้ edit token
  return !token;
}

// Same JSON bodies as the services, so the web pages show the same messages.
function unauthorizedResponse() {
  return new Response(JSON.stringify({ error: 'unauthorized' }), {
    status: 401,
    headers: { 'content-type': 'application/json', 'www-authenticate': 'Bearer' },
  });
}

function unavailableResponse() {
  return new Response(JSON.stringify({ error: 'auth_unavailable' }), {
    status: 503,
    headers: { 'content-type': 'application/json' },
  });
}

// Headers passed on to auth-service. The cookie and the bypass header let the call through
// Deployment Protection on preview URLs; production is public and ignores them.
const FORWARDED_HEADERS = ['authorization', 'cookie', 'x-vercel-protection-bypass'];
const AUTH_TIMEOUT_MS = 5000;

// The whole gateway decision for one request. Resolves to a Response that stops the request
// (401 or 503), or to undefined = let it through to the service.
// Service bindings are not available in Routing Middleware, so auth-service is asked through
// this deployment's own public /auth/me route; `fetchImpl` is replaced in the tests.
async function checkRequest(request, fetchImpl = fetch) {
  const url = new URL(request.url);
  if (!needsLogin(request.method, url.pathname, request.headers)) return undefined;
  if (!request.headers.get('authorization')) return unauthorizedResponse();

  const headers = new Headers();
  for (const name of FORWARDED_HEADERS) {
    const value = request.headers.get(name);
    if (value) headers.set(name, value);
  }
  let answer;
  try {
    answer = await fetchImpl(new URL('/auth/me', url.origin), {
      headers,
      signal: AbortSignal.timeout(AUTH_TIMEOUT_MS),
    });
  } catch {
    return unavailableResponse();
  }
  if (answer.ok) return undefined;
  if (answer.status === 401) return unauthorizedResponse();
  return unavailableResponse();
}

module.exports = {
  LOGIN_RULES,
  EDIT_RULE,
  NOTE_TOKEN_HEADER,
  classify,
  needsLogin,
  checkRequest,
  unauthorizedResponse,
  unavailableResponse,
};
