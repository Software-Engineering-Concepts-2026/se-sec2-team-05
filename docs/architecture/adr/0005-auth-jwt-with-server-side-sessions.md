# ADR-005: User & Auth Service with JWT Access Tokens Backed by Server-Side Sessions

🌐 **English** · [ภาษาไทย](./0005-auth-jwt-with-server-side-sessions.th.md)

**Status:** Accepted

**Context:**
[ADR-003](./0003-tracer-bullet-scope.md) deferred the User & Auth Service, which left every Notes Service endpoint unauthenticated and `uploader_name` trivially spoofable. US-05 (#5) and US-06 (#6) are Sprint 1 "Must" stories that close that gap:

*   #5 — only university-domain emails may register, duplicate emails are refused, passwords are hashed before storage, and errors are easy to understand.
*   #6 — log in with email + password, **logging out invalidates the session/token immediately**, a failed login does not say which field was wrong (no account enumeration), and the user stays logged in until they log out or the token expires.

The non-functional requirements add NFR-004 (passwords hashed "e.g. with bcrypt", never plaintext), NFR-005 (private requests carry an unexpired JWT; the API Gateway rejects missing/invalid tokens with 401), and NFR-013 (each microservice has its own Dockerfile). The [C4 Container diagram](../c4-container.md) gives the User & Auth Service "registration, login (hashed passwords), JWT issuance".

These pull in different directions. A plain JWT is self-contained and cannot be revoked before it expires, so on its own it cannot satisfy "logout invalidates immediately". And NFR-005 assumes an API Gateway that, per ADR-003, does not exist yet.

**Decision:**
Build a separate `auth-service` container (Flask + SQLAlchemy, port 5002, its own Dockerfile). It shares the existing PostgreSQL database but owns its own tables, `users` and `auth_sessions`.

*   **Registration** (`POST /auth/register`) — the email is trimmed and lower-cased, and its domain must **exactly** match one of `ALLOWED_EMAIL_DOMAINS` (comma-separated, default `up.ac.th`; subdomains do not count). Passwords are 8–128 characters and are not trimmed. `display_name` is chosen by the user, 1–120 characters. All invalid fields are reported at once (`400`); a duplicate email is `409`, including under a concurrent race via the unique constraint.
*   **Access token** (`POST /auth/login`) — an HS256 JWT valid for **8 hours**, with **no refresh token**. Claims: `sub` (user id), `jti`, `iat`, `exp`, `iss`. Every login writes one `auth_sessions` row keyed by the `jti`.
*   **Verification** — a token is accepted only if **both** checks pass: the JWT signature, `exp` and `iss` are valid (the algorithm is pinned to HS256, so `alg: none` and algorithm swaps are rejected), **and** its `auth_sessions` row exists, belongs to `sub`, and has not been revoked.
*   **Logout** (`POST /auth/logout`) sets `revoked_at` on that session. The second check above fails from that moment on, which is what makes revocation immediate. Other sessions of the same user are unaffected.
*   **No enumeration at login** — wrong password and unknown email return the same `401 invalid_credentials` body. An unknown email is still checked against a dummy hash of the same cost, so response time does not reveal whether an account exists either.
*   **Other services verify through `GET /auth/me`** over REST ([ADR-002](./0002-use-restful-api-internal-communication.md)) instead of each holding the signing secret. The secret stays in one service, and revocation is checked in the one place that knows about it. Until an API Gateway exists, this call is how NFR-005's "reject with 401" is enforced.
*   **Signing secret** — `AUTH_JWT_SECRET` is required and must be at least 32 bytes (the HS256 key-size floor in RFC 7518 §3.2). There is deliberately no default in code; the service refuses to start without it. `docker-compose.yml` carries a dev-only value.

**Password hashing — Werkzeug scrypt as the NFR-004 equivalent of bcrypt:**
NFR-004 names bcrypt as an example. The substance of the requirement is a slow, salted, password-specific hash instead of plaintext or a fast general-purpose hash. We use `werkzeug.security.generate_password_hash(password, method="scrypt:131072:8:1")`, which is equivalent to bcrypt on every property NFR-004 depends on, and stronger on some:

*   **Salted per password** — Werkzeug generates a random salt for every hash, so identical passwords produce different hashes and precomputed tables do not apply. A test asserts this.
*   **Adjustable work factor stored in the hash** — like bcrypt's `$2b$<cost>$`, the hash string records `scrypt:<N>:<r>:<p>`, so the cost can be raised later without invalidating existing hashes.
*   **Constant-time verification** — `check_password_hash` compares with `hmac.compare_digest`.
*   **Memory-hard** — at these parameters each hash needs about 128 MiB of memory (bcrypt uses about 4 KiB), which makes GPU/ASIC cracking far more expensive.
*   **Ranked above bcrypt by OWASP** — the [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html) orders the recommendations Argon2id → scrypt → bcrypt → PBKDF2. It gives the scrypt minimum as N=2^17, r=8, p=1 and treats bcrypt (work factor ≥ 10) as the choice for legacy systems.
*   **No 72-byte truncation** — bcrypt ignores everything after 72 bytes of input. Thai characters take 3 bytes each in UTF-8, so a Thai passphrase of about 25 characters or more would be silently truncated. scrypt has no such limit, and we cap passwords at 128 characters only to bound request size.
*   **No new dependency** — Werkzeug already ships with Flask and uses `hashlib.scrypt` from OpenSSL, so there is no extra C extension to build in the image.

Werkzeug's own default is N=2^15, which is **below** the OWASP minimum. The parameters are therefore set explicitly in `credentials.py`, and a test fails if they drift. The measured cost is about 0.4 s per hash on a development laptop (2026-09-25).

**Alternatives considered:**
*   **Stateless JWT only, with logout meaning "the client forgets the token"** — rejected. The token stays valid until `exp`, which fails #6's "invalidate immediately".
*   **Opaque random session token instead of a JWT** — simplest, and revocation works the same way. Rejected to stay with the JWT that the C4 diagram and NFR-005 specify, and so that a future gateway could at least reject forged or expired tokens locally before asking auth-service.
*   **Authentication inside `notes-service`** — fewer containers, but it contradicts ADR-001 and NFR-013 and ties identity to the notes schema.
*   **The `bcrypt` or `argon2-cffi` package** — both need an extra native dependency. Argon2id is OWASP's first choice; because each hash string records its method, moving to it later only means re-hashing on the next successful login.

**Consequences:**
*   **Positive:**
    *   Every acceptance criterion of #5 and #6 is covered by an automated test, including "logout invalidates immediately" and "the same response for a wrong password and an unknown email".
    *   There is now a trustworthy identity that the upload flow can use to attach the uploader's name (US-31) instead of reading it from the form.
    *   The signing secret lives in one service only, and each hash carries its own method and cost, so both can be rotated or upgraded later.
*   **Negative:**
    *   **No email verification.** The domain check only proves an address *looks* like a university email, not that the person registering owns it — anyone can register someone else's `@up.ac.th` address. The C4 diagram's Email Service is out of scope for #5's criteria, but it must land before any public deployment, especially because `display_name` (and therefore the credit shown on notes) is self-chosen.
    *   Registration reveals whether an email already has an account (`409`). #5 requires the duplicate check, so this cannot be avoided at sign-up; login still does not leak it.
    *   Logins are not rate-limited. Brute force is slowed only by the scrypt cost. This is a follow-up.
    *   Giving up statelessness costs one HTTP call to auth-service plus one database lookup for every authenticated request to another service.
    *   There is no password reset, no profile editing, and no clean-up of expired `auth_sessions` rows yet.
    *   Bearer tokens are only as safe as the transport, so HTTPS is required in any real deployment. Until then ADR-003's rule still stands: keep the services off the public internet.
*   **Scope of this change:** only `auth-service` is added. `notes-service` does not call it yet, so uploads still take `uploader_name` from the form. Requiring login on upload and deriving the uploader from the account is the next change (refs #31). [ADR-004](./0004-per-note-edit-token.md)'s edit tokens stay in place and are not superseded by this ADR. The new tables are additive, so this change alone does not require `docker compose down -v`.
