# ADR-007: Configure Notes Service Admins with User IDs

[🌐 English] · [ภาษาไทย](./0007-notes-service-admin-user-ids.th.md)

**Status:** Accepted

**Context:**
Issue #17 requires admin capability to review and remove inappropriate-content reports. The current scope should not expand into changing the authentication and authorization model owned by `auth-service`.

**Decision:**
Configure Notes Service admins through the comma-separated `ADMIN_USER_IDS` environment variable. Do not add an admin or role field to `auth-service`.

**Consequences:**
*   Notes Service can authorize report-management endpoints without changing `auth-service`.
*   This service-local allowlist is a limited solution; authorization can move to a role-based model in the future, especially as Issue #18 is extended.
