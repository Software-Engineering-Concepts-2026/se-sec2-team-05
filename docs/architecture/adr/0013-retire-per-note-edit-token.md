# ADR-013: Retire the Per-Note Edit Token

🌐 **English** · [ภาษาไทย](./0013-retire-per-note-edit-token.th.md)

**Status:** Accepted · supersedes ADR-004, narrows ADR-008

**Context:**
ADR-004 gave every note a random edit token as a stand-in for ownership while the system had no login, and said it should go once the User & Auth Service existed. ADR-005 added that service, US-31 made the uploader come from the logged-in account (`uploader_id`), and ADR-008 let the logged-in uploader edit and delete their notes while keeping the token as a second way in. Since then the token has only had costs: one more secret for users to keep, a separate edit page that skips login, a second code path in every permission check, and a header the gateway has to treat as an exception.

**Decision:**
*   Editing (`PATCH /notes/<id>`) and deleting (`DELETE /notes/<id>`) a note **require logging in as the account that uploaded it**. No login gives `401`, another account gives `403`, as in ADR-008.
*   `POST /notes` no longer returns `edit_token`. The `X-Note-Token` header is ignored.
*   The `notes.edit_token_hash` column is dropped by Alembic revision `0002` (ADR-010). `tokens.py` is removed.
*   The web app drops `edit.html` and the token box after upload. Owners edit and delete from the profile page (ADR-008), and the note and upload pages point there.
*   Admin moderation stays as it is: admins remove reported notes through `/reports/<id>/note` (ADR-007).

**Consequences:**
*   One way to prove ownership, checked by auth-service, which can revoke it (logout). The gateway has no token exception to keep.
*   Tokens already handed out stop working. Uploaders of existing notes can still edit and delete them by logging in, because every note already has `uploader_id` (US-31).
*   Editing now needs auth-service to be up; while it is down, edits and deletes get `503`, as reads that need login already do.
*   The migration cannot restore the hashes on downgrade; it adds the column back empty.
