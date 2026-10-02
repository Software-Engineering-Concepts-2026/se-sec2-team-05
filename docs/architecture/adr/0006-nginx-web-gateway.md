# ADR-006: Serve the Web App and Proxy the APIs Through One nginx Gateway

🌐 **English** · [ภาษาไทย](./0006-nginx-web-gateway.th.md)

**Status:** Accepted

**Context:**
Every backend story so far shipped as an API only. The pages in `prototypes/sprint1/` are static mockups with hardcoded data, so two stories still have one acceptance criterion open that only a real page can satisfy: US-11 (#11) "close the preview and return to the search results without losing your place", and US-31 (#31) "show the owner's name every time the note is displayed".

A browser page can only call the APIs if they are on the same origin, or if the services answer with CORS headers. Today `notes-service` (`:5001`) and `auth-service` (`:5002`) are separate origins and send no CORS headers. A page opened from disk (`file://`) or from any third port is therefore blocked before a request reaches either service.

The [C4 Container diagram](../c4-container.md) puts an API Gateway in front of the services for exactly this kind of job, but [ADR-003](./0003-tracer-bullet-scope.md) deferred it and [ADR-005](./0005-auth-jwt-with-server-side-sessions.md) made `notes-service` verify tokens through `GET /auth/me` in the meantime. Two open PRs (#68, #69) also conflict with `main` in `services/notes-service/app.py`, so any change that has to touch that file makes those merges harder.

**Decision:**
Add a `web` container built from `web/Dockerfile`: nginx (`nginxinc/nginx-unprivileged`, non-root, port 8080) that

*   serves the static files of the web app (`web/index.html`, `app.js`, `search-utils.js`, `style.css`) at `/`,
*   proxies `/notes` and `/notes/…` to `notes-service:5001`, and `/auth/…` to `auth-service:5002`, passing the original path, query string and `Authorization` header through unchanged,
*   allows request bodies up to 22 MB, a little above `notes-service`'s own 21 MB limit, so an oversized upload is still rejected by `notes-service` with its JSON `413` instead of an nginx HTML error page.

The page then calls relative URLs (`/notes?…`, `/notes/7/preview`) on its own origin, and no service needs CORS. Ports 5001 and 5002 stay published, so existing `curl` checks and CI smoke tests keep working.

**This is not the API Gateway from the C4 diagram yet.** It does not verify JWTs, rate-limit, or aggregate responses. Each service still enforces its own rules, and `notes-service` still asks `auth-service` about every token (ADR-005). The routes live in one file, `web/nginx.conf`, so token checks can be added there later, or the file can be replaced by a real gateway, without changing the page.

**Alternatives considered:**
*   **CORS headers in each Flask service:** this keeps the page anywhere, but it edits `app.py` in both services, including the `notes-service` file that #68 and #69 already conflict on. Every service also has to keep its own list of allowed origins in step with the others. Rejected for now.
*   **Serve the page from `notes-service`:** this needs the fewest moving parts, but the frontend becomes part of one backend service, `/auth` is still a different origin, and it touches `notes-service/app.py` as well. Rejected.
*   **Write the full API Gateway in Flask now, as the C4 diagram says:** this is the target design, but it is far more work than this slice needs, and it would repeat ADR-003's mistake of building layers before a thin end-to-end path exists. Deferred, and this gateway is the place it would go.

**Consequences:**
*   **Positive:**
    *   A browser can run the search → preview flow end to end on the real stack at `http://localhost:8080`, which closes the last acceptance criterion of #11 and #31.
    *   No service code changes, so the open PRs #68/#69 are not affected.
    *   The system now has one public entry point, which is where gateway concerns (JWT checks, rate limits) can be added later.
    *   The CI smoke test covers the gateway: static files, query strings, the `Authorization` header and a multipart upload all pass through nginx (DK-08).
*   **Negative:**
    *   One more container in `docker compose up`, and one more config file that can drift from the services' routes. A new top-level path such as `/stats` needs a new `location` block in `web/nginx.conf`.
    *   Services are still reachable directly on 5001/5002, so the gateway is not a security boundary. Until it checks tokens itself, every service must keep enforcing auth on its own.
    *   nginx resolves `notes-service` and `auth-service` when it starts. If either container does not exist, `web` fails to start instead of returning `502`.
