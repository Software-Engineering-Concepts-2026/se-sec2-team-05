# ADR-004: Per-Note Edit Tokens as a Temporary Stand-In for Ownership Checks

🌐 **English** · [ภาษาไทย](./0004-per-note-edit-token.th.md)

**Status:** Accepted (temporary — to be superseded when #5/#6 land) · amended by [ADR-008](./0008-owner-login-for-note-changes.md): the logged-in uploader can now edit/delete without the token, and the token still works

**Context:**
US-19 (#19) and US-20 (#20) both carry the acceptance criterion "only the owner" may edit or delete a note. The system has no trustworthy notion of identity yet: [ADR-003](./0003-tracer-bullet-scope.md) deliberately deferred the User & Auth Service (#5, #6), and `uploader_name` is submitted through the upload form and displayed on every note. Checking a request's `uploader_name` against the stored one would therefore check nothing at all — the value is public and anyone can retype it.

That leaves three options: ship the stories with an ownership check that does not hold, block both stories until authentication exists, or find an interim mechanism that actually enforces the criterion. The first repeats the mistake ADR-003 criticises — closing stories against work that does not satisfy their acceptance criteria. The second stalls two Sprint 1 "Must" stories behind a service the team has not started.

**Decision:**
`notes-service` issues a **per-note edit token**:

*   `POST /notes` generates 256 bits of randomness (`secrets.token_urlsafe(32)`) and returns it **once**, in the creation response only.
*   Only the SHA-256 hash of the token is stored, in `notes.edit_token_hash`. The token itself is never written to the database, logged, or returned by any other endpoint.
*   `PATCH /notes/<id>` and `DELETE /notes/<id>` require the token in an `X-Note-Token` header and compare it with `secrets.compare_digest`. A missing or wrong token is `403`.
*   SHA-256 without key stretching is sufficient here: the token is machine-generated high-entropy randomness, not a human-chosen password, so there is nothing for a brute-force or rainbow-table attack to exploit.
*   Read endpoints stay open, exactly as ADR-003 left them.

The mechanism lives in one file, `services/notes-service/tokens.py`, so that removing it later is a contained change.

**This is not authentication.** There is no identity, no session, no login, no token revocation, and no way for a user who loses a token to recover it. It is a capability check on a single note and nothing more.

**Consequences:**
*   **Positive:**
    *   The "only the owner" criterion of #19 and #20 is enforced in a way that can be tested, rather than asserted. Cross-note tests confirm one note's token cannot touch another.
    *   Both stories can ship without waiting for the User & Auth Service.
    *   The migration path is small: when #5/#6 land, delete `tokens.py` and the `edit_token_hash` column, and check `note.owner_id == current_user.id` instead.
*   **Negative:**
    *   A lost token means the note can no longer be edited or deleted by its uploader; an admin path does not exist yet. Acceptable only because nothing is deployed and no real data exists.
    *   The token is transported as a plain header, so it is only as safe as the transport. `notes-service` must stay off the public internet until #5/#6, which ADR-003 already requires.
    *   Any client that wants to offer editing has to store the token itself, which is a burden the real auth flow will remove.
    *   Adding `edit_token_hash` and `updated_at` changes the schema, and there is still no migration tool (ADR-003), so dev environments need `docker compose down -v`.
