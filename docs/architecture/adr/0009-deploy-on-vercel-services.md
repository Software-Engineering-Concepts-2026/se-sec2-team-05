# ADR-009: Deploy on Vercel with Services, Neon Postgres and Private Vercel Blob

🌐 **English** · [ภาษาไทย](./0009-deploy-on-vercel-services.th.md)

**Status:** Accepted · the 4 MB upload limit is replaced by ADR-012 (direct upload to Blob, 10 MB)

**Context:**
The team wants a public URL for NoteShare and chose Vercel. ADR-001 planned containers on Render/Railway for the backend plus Vercel for the frontend, but what we actually built is one `docker compose` stack: three Flask services, PostgreSQL, files on a disk volume (ADR-003) and an nginx gateway (ADR-006). Vercel runs each backend as a Vercel Function: instances are stateless and scale to zero, so anything written to their disk is lost, and a request or response body is capped at 4.5 MB.

**Decision:**
*   Deploy all four parts as **Vercel Services** in one project (`vercel.json` at the repo root): `web` (the static files of `web/`), `notes`, `auth` and `stats` (Flask). Top-level rewrites replace the nginx routes one for one, and `notes`/`stats` reach `auth` through a private **service binding** that fills `AUTH_SERVICE_URL`.
*   Use **Neon Postgres** from the Vercel Marketplace for `DATABASE_URL`. The services turn a `postgres://`/`postgresql://` URL into `postgresql+psycopg://` because only psycopg 3 is installed, and use `pool_pre_ping` because Neon closes idle connections.
*   Store note files and previews in a **private Vercel Blob** store through a new `BlobFileStorage` (`NOTES_STORAGE_BACKEND=blob` + `BLOB_READ_WRITE_TOKEN`). Downloads still go through notes-service, so its checks and counters keep working.
*   Lower the upload limit from 20 MB to **4 MB** everywhere (service, web form, nginx) so a full upload request stays under 4.5 MB. Direct browser-to-Blob uploads were rejected for now: they would need a token endpoint and changes to both the upload page and the API.
*   Keep `docker compose` as the local and CI path; it still uses local disk storage and nginx.

**Consequences:**
*   Secrets (`AUTH_JWT_SECRET`, database password, Blob token) live in Vercel environment variables instead of the committed compose file, and the site gets HTTPS.
*   Notes larger than 4 MB can no longer be uploaded, on Vercel or locally.
*   notes-service now depends on the `vercel` Python SDK, which also lands in its Docker image even though compose does not use Blob.
*   Schema changes still have no migration tool: on Neon a new column means creating it by hand or resetting the database.
*   Cold starts after idle periods make the first request slower, and the free Hobby plan's limits apply.
