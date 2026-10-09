# ADR-010: Alembic Migrations Run at Service Startup

🌐 **English** · [ภาษาไทย](./0010-alembic-migrations-at-startup.th.md)

**Status:** Accepted

**Context:**
notes-service and auth-service built their tables with `Base.metadata.create_all` (ADR-003). `create_all` only creates missing tables; it cannot add a column to a table that already exists. Locally that meant `docker compose down -v` after every schema change, and ADR-009 left the same gap on Neon: a new column meant creating it by hand or resetting the production database. Vercel also gives us no step to run a command before a service starts, and several instances (gunicorn workers, concurrent cold starts) can start against the same database at once. Both services share one Postgres database.

**Decision:**
*   Use **Alembic** in notes-service and auth-service. Each service has its own `migrations/` folder and its own version table (`alembic_version_notes`, `alembic_version_auth`), so they can share one database without touching each other's history. `env.py` compares and creates only the tables in its own service's metadata.
*   **Migrate on startup**: `build_session_factory()` calls `upgrade_to_head()` (`migrate.py` in notes-service, `auth_migrate.py` in auth-service) instead of `create_all`. This works the same in compose, on Vercel and in the tests, with no separate deploy step.
*   On Postgres, hold a **transaction-level advisory lock** (`pg_advisory_xact_lock`, a different key per service) for the whole migration, so instances that start together wait in turn instead of racing on `CREATE TABLE`.
*   The first revision `0001` is a **baseline** of the schema as `create_all` built it. A database that already has the service's tables but no version table (old compose volumes, Neon) is **stamped** as `0001` and then upgraded, so its rows are kept.
*   New schema changes go in new revisions written with `alembic revision --autogenerate` from the service folder (`alembic.ini` there is only for the CLI). `0001` is never edited.

**Consequences:**
*   A new column reaches Neon on the next deploy without resetting the database.
*   Every start runs a version check in one transaction, which adds a little time to cold starts.
*   A pre-Alembic database whose schema does not match the baseline would be stamped anyway and then fail on a later revision; all existing databases were made from the same models, so this is not expected.
*   The tests build their tables through the same migrations, and MG-01 (`alembic check`) fails if someone changes the models without adding a revision. MG-06 (concurrent starts) runs only on Postgres.
*   Both Docker images now also copy the migration files, and both services depend on `alembic`.
