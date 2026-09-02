# ADR-003: Narrow the First Running Slice to One Service and Local File Storage

🌐 **English** · [ภาษาไทย](./0003-tracer-bullet-scope.th.md)

**Status:** Accepted

**Context:**
[ADR-001](./0001-tech-stack-selection.md) commits NoteShare to a microservices architecture — API Gateway, User & Auth Service, Notes Service, Stats Service — backed by PostgreSQL and S3-compatible object storage. Until now the repository has contained no running application: Sprint 1 "Must" stories were closed against front-end prototypes whose data is hardcoded, as `prototypes/sprint1/README.md` states plainly. The team's own Definition of Done requires a sprint to be demonstrable end-to-end, which the project cannot currently satisfy.

We need a first slice that actually runs through every layer (a tracer bullet). Building the full target architecture before anything runs would mean a three-person team spending its remaining time on infrastructure rather than on the user stories the course grades.

**Decision:**
For the first running slice (US-08, issue #8) we will deliberately build **less** than the target architecture:

*   **One backend service, not four.** `notes-service` owns note metadata and files. The API Gateway and User & Auth Service are not built yet; `notes-service` is exposed directly and every endpoint is unauthenticated.
*   **Local file storage behind an interface, not object storage.** Files are written to a directory mounted as a Docker volume. All access goes through the `save`/`open`/`delete` interface in `storage.py`, so swapping in MinIO or S3 touches one file.
*   **PostgreSQL from the start.** This is the one target-architecture choice we do *not* defer, because a database swap late in the project is far more disruptive than a storage swap, and `docker compose` makes it cheap now.
*   **No schema migration tool yet.** `SQLAlchemy.create_all()` builds the schema. Alembic comes in when the schema stabilises and there is data worth preserving.

ADR-001 and ADR-002 remain the target; this ADR records the order we approach it in, not a change of destination.

**Consequences:**
*   **Positive:**
    *   The project gets a demonstrable end-to-end path — upload with metadata, filter, download — satisfying the Sprint Definition of Done for the first time.
    *   CI now exercises real application code end-to-end (`docker compose up` plus an upload → filter → download round trip) rather than only prototypes.
    *   The storage interface and the container split keep the migration path to ADR-001 open without rewriting business logic.
*   **Negative:**
    *   The running system does not match the C4 Container diagram yet. `docs/architecture/c4-container.md` describes the target, not what `docker compose up` starts — a reader can be misled if they do not read this ADR.
    *   Local file storage is not durable across a redeploy on a real host and does not scale beyond one instance. It is acceptable only because nothing is deployed to production yet.
    *   Every endpoint is open. `notes-service` must not be exposed publicly before #5/#6 (auth) land — the uploader's name is currently taken from the form and is trivially spoofable.
    *   Without migrations, any schema change during this phase requires dropping the volume (`docker compose down -v`).
