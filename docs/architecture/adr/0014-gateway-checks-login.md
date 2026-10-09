# ADR-014: The Gateway Checks the Login Before Forwarding

🌐 **English** · [ภาษาไทย](./0014-gateway-checks-login.th.md)

**Status:** Accepted

**Context:**
The C4 Container diagram puts an API Gateway in front of the services, and ADR-006 left a note that the nginx gateway "does not verify JWTs yet". Since then the system grew to about thirty routes in three services, and each service checks the login on its own: notes-service and stats-service ask auth-service `GET /auth/me` (ADR-005), and the open routes (search, note page, preview, download, comments list, stats overview) answer anyone. On Vercel (ADR-009) the top-level rewrites in `vercel.json` replace nginx and forward everything as well. A request without a valid token for a login-only route therefore travels all the way into a Flask function before it is refused.

On Vercel, Routing Middleware is the only code that runs before the rewrites. Two things had to be tested on a real preview deployment, because the docs do not cover them for projects that use `services`:
*   A `middleware.ts` file at the repository root is **ignored** in services mode (the build only lists the three Flask functions). Declaring it with `"proxy": { "entrypoint": … }` in `vercel.json` works.
*   The middleware is built as CommonJS, so it cannot import an `.mjs` module (`ERR_REQUIRE_ESM` at runtime).

Service bindings are not available in Routing Middleware, so the middleware cannot reach auth-service privately.

**Decision:**
*   One rule table says which method + path needs a login, which is open, and the special case for editing a note. Login-only: upload, favorites list and toggle, my notes, thanks, rating, report, write/delete a comment, per-note stats, and the admin report routes. `PATCH`/`DELETE /notes/<id>` needs a login **unless the request carries `X-Note-Token`**, so editing with the edit token (ADR-004) still works without an account. That exception is temporary and is marked in both config files. Everything else, including `/auth/*` and `GET /stats`, is open.
*   **docker compose:** `web/nginx.conf` holds the table as two `map` blocks and runs `auth_request` to `auth-service /auth/me` on every API location. A `set` in each location computes the rule in the main request, because inside the auth subrequest `$uri` is the subrequest's own path. Open routes answer the subrequest with `204` without calling auth-service.
*   **Vercel:** `gateway/proxy.ts` is Routing Middleware, declared under `"proxy"` in `vercel.json` with a matcher for `/notes` and `/reports` only. The logic lives in `gateway/rules.js` (CommonJS), which calls `/auth/me` on the deployment's own public URL and forwards `Authorization`, plus the cookie and `x-vercel-protection-bypass` so the call also passes Deployment Protection on previews.
*   Both gateways answer like the services do: `401 {"error": "unauthorized"}` with `WWW-Authenticate: Bearer`, and `503 {"error": "auth_unavailable"}` when auth-service is down or gives anything other than 2xx or 401. The web pages therefore show the same messages as before.
*   The gateway checks only that the login is valid. Admin role, note ownership, the edit token itself and "can rate only after opening" stay in the services, which keep all their checks (defence in depth).
*   `gateway/cases.json` lists every public route with the expected result. `node --test` checks `rules.js` against it, and `src/tests/test_gateway_rules.py` checks the nginx maps, the `vercel.json` matcher, and that every Flask route of the three services appears in the cases.

**Alternatives considered:**
*   **Verify the JWT signature in the gateway with `AUTH_JWT_SECRET`:** this needs no network call, but it cannot see a session revoked by logout (ADR-005), so a logged-out token would pass the gateway and the gateway would contradict auth-service. It would also put the signing secret into one more component. Rejected.
*   **A separate gateway service in Flask:** this would be the C4 box literally, but it adds a fourth function and one more hop to every request on Vercel, and it duplicates what nginx and Routing Middleware already do. Rejected.
*   **Check every request, open ones included:** this would turn an expired token on the search page into an error, while the services deliberately treat it as "not logged in". Rejected.

**Consequences:**
*   Requests without a valid login for login-only routes stop at the gateway, and both gateways give the same answer. The CI smoke test checks this on the compose stack, including the `503` when auth-service is stopped.
*   Login-only routes cost one more call to auth-service (nginx subrequest, or one more request through Vercel's public routing). Open routes are unchanged, and on Vercel static pages do not run the middleware at all.
*   A new route has to be added in three places: `gateway/cases.json`, `gateway/rules.js` and the map in `web/nginx.conf`. The tests fail if any of them is missing it.
*   Services are still reachable directly on 5000–5002 in compose, so the services must keep their own checks. On Vercel the services are reachable only through the rewrites, which run after the middleware.
*   Uploads still pass through the middleware: a 4 MB file (the notes-service limit) was accepted through both gateways in testing.
*   When the edit token is removed, delete the `X-Note-Token` exception in `gateway/rules.js` and the `"~^edit:."` line in `web/nginx.conf`, then update the cases.
