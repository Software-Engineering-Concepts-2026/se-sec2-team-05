# ADR-011: Rate Limit Login and Registration with Counters in Postgres

🌐 **English** · [ภาษาไทย](./0011-rate-limit-login-and-register.th.md)

**Status:** Accepted

**Context:**
auth-service accepted any number of `POST /auth/login` and `POST /auth/register` requests. A script could guess passwords for one account without limit, try one common password across many accounts, or walk a list of emails through registration, where the `409 email_taken` answer tells which emails have an account (ADR-005 accepted that leak for the sake of US-05). On Vercel the service runs as several stateless instances that scale to zero (ADR-009), so a counter kept in process memory would be split between instances and reset on every cold start. Students on the university network can share one public IP.

**Decision:**
*   Count attempts in a new table **`auth_attempts`** (kind, key, created_at), created by Alembic revision `0002` of auth-service (ADR-010). Every instance reads the same rows in the shared Postgres (Neon), and the limit is a sliding window over those rows.
*   **Login:** count failed logins per submitted email and per client IP. The defaults are 5 per email and 30 per IP in 15 minutes. When either limit is reached the service answers **`429`** with `Retry-After` and a Thai message with the minutes to wait, **before** checking the password, so even the right password is refused for that time. An email without an account is counted and locked the same way, so the answer does not reveal which emails exist. A successful login clears that email's counter, but not the IP counter.
*   **Registration:** count every request that passes validation, per client IP: both `201` and `409`, because `409` is the answer that leaks accounts. The default is 20 per hour, enough for a whole class registering from the campus network at once. Requests that fail validation (`400`) are not counted.
*   The client IP is the **rightmost** `X-Forwarded-For` hop, the one added by the proxy in front of the service (nginx appends it, Vercel overwrites the header), not the leftmost value that a client can write itself.
*   Limits and windows come from environment variables (`AUTH_LOGIN_MAX_FAILS_PER_EMAIL`, `AUTH_LOGIN_MAX_FAILS_PER_IP`, `AUTH_LOGIN_WINDOW_MINUTES`, `AUTH_REGISTER_MAX_PER_IP`, `AUTH_REGISTER_WINDOW_MINUTES`) with the defaults above. A value that is not a positive integer stops the service from starting instead of silently turning the limit off. Rows older than the longest window are deleted whenever a new attempt is recorded.
*   In-memory counters and the Vercel Firewall were rejected: memory does not work across Vercel instances, and the firewall would not cover `docker compose` or the tests.

**Consequences:**
*   Password guessing is slowed to a handful of tries per account per 15 minutes, and registration can no longer be used to check thousands of emails.
*   Anyone who knows a student's email can lock that account's login for 15 minutes by failing 5 times. The short window keeps this to an annoyance; the limit has no permanent lockout.
*   Many students behind one campus IP share the IP limits. The IP limits are set much higher than the per-email limit for this reason and can be raised through the environment.
*   Each login and registration costs one or two extra small queries, and failed logins write rows to the database.
*   The web login and register forms show the service's message for `429` instead of a generic HTTP error.
