# ADR-008: Let the Logged-In Uploader Edit and Delete Their Notes, Alongside the Edit Token

🌐 **English** · [ภาษาไทย](./0008-owner-login-for-note-changes.th.md)

**Status:** Accepted · amends [ADR-004](./0004-per-note-edit-token.md)

**Context:**
[ADR-004](./0004-per-note-edit-token.md) made a per-note edit token the only way to edit or delete a note, as a stand-in until the team had accounts. Accounts now exist: [ADR-005](./0005-auth-jwt-with-server-side-sessions.md) added `auth-service`, and since US-31 (#31) every upload requires login and stores the uploader's account id in `notes.uploader_id` (a `NOT NULL` column).

The web design for the profile page (Issue #82, wireframe screen 1e) shows "My uploads" with edit and delete on every row. With ADR-004 alone, that page cannot work: the token is returned once at upload time, the server only keeps its hash, and a user who did not save it can never change the note again. Asking users to paste a token before every edit is the burden ADR-004 itself expected the real auth flow to remove.

ADR-004 planned to delete the token entirely once accounts landed. Doing that now would break clients that already rely on `X-Note-Token` (the CI smoke test DK-03 to DK-06 and any saved tokens), so this ADR adds the account path instead of replacing the token path.

**Decision:**
`PATCH /notes/<id>` and `DELETE /notes/<id>` accept **either** proof of ownership:

1.  A valid `X-Note-Token` for that note (ADR-004, unchanged).
2.  An `Authorization: Bearer <access_token>` whose account id equals `notes.uploader_id`.

The check order and responses:

*   The edit token is checked first. If it matches, the request passes without calling `auth-service`, so token holders can still edit while `auth-service` is down.
*   With no valid token and no `Authorization` header, the answer is `403 forbidden`, exactly as before.
*   With a Bearer token that `auth-service` rejects, the answer is `401 unauthorized` with `WWW-Authenticate: Bearer`, so the web app knows to send the user back to login. If `auth-service` is unreachable, `503 auth_unavailable`.
*   A valid login that is not the uploader gets `403 forbidden`.
*   A missing note is still `404` before any ownership check.

The same `uploader_id` also backs a new read endpoint, `GET /notes/mine` (login required), which lists the caller's notes with a summary for the profile page. `uploader_id` itself is still not exposed in any response.

**Consequences:**
*   **Positive:**
    *   The profile page can offer edit and delete without the user keeping a token.
    *   A lost token is no longer fatal for notes uploaded with an account, which is every note since US-31.
    *   Existing token clients and tests keep working; only one old test, which asserted that login alone was not enough, had to change.
*   **Negative:**
    *   There are now two ways in. A leaked edit token still grants edit/delete on its note even if the account owner changes their password. Token revocation is still out of scope.
    *   Ownership by login inherits the limits of ADR-005: no email verification yet, and `notes-service` trusts `auth-service`'s answer to `GET /auth/me`.
    *   Removing the token later (the original ADR-004 plan) is still a separate decision, and would need the web app and the smoke tests to stop sending `X-Note-Token` first.
