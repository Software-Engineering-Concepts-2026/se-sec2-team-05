# NoteShare — Architecture

🌐 **English** · [ภาษาไทย](./README.th.md)

The architectural blueprint for **NoteShare**, a web platform where university students upload, search, and share lecture notes. We describe the system with the [C4 model](https://c4model.com/) (Level 1 & 2) and record the reasoning behind key decisions as [ADRs](./adr/).

## C4 Level 1 — System Context

Who uses NoteShare and which external systems it depends on.

![C4 Level 1 – System Context diagram for NoteShare](diagrams/c4-level-1-context.png)

| Relationship | Description |
| --- | --- |
| James (Note Seeker) → NoteShare | Searches, previews & downloads notes; gives credit to authors |
| Pim (Note Contributor) → NoteShare | Uploads & organizes notes; views recognition/usage of her notes |
| NoteShare → Email Service | Sends account-verification and notification emails |

Diagram source: [`diagrams/c4-level-1-context.svg`](diagrams/c4-level-1-context.svg) · notes in [c4-context.md](./c4-context.md)

## C4 Level 2 — Containers

Zooming into NoteShare: the runnable/deployable units and how they talk to each other.

![C4 Level 2 – Container diagram for NoteShare](diagrams/c4-level-2-container.png)

| Container | Tech | Responsibility |
| --- | --- | --- |
| Single-Page App | React + Vite | All user-facing UI in the browser: search, filter, preview, upload, credit |
| API Gateway | Python + Flask | Single entry point; routes requests to services and verifies tokens (JWT) |
| User & Auth Service | Python + Flask | Registration, login (hashed passwords), JWT issuance, profiles |
| Notes Service | Python + Flask | Note metadata, search/filter, upload/download, credits |
| Stats Service | Python + Flask | Aggregates download and usage stats for contributor recognition |
| PostgreSQL Database | PostgreSQL | Users, note metadata, courses, and credit records |
| Object Storage | S3-compatible | Uploaded note files (PDF/images) |

All calls from the SPA through the API Gateway to the services are REST/JSON over HTTP (see [ADR-002](./adr/0002-use-restful-api-internal-communication.md)). Each service talks to PostgreSQL directly over SQL, and the Notes Service is the only container that touches Object Storage.

Diagram source: [`diagrams/c4-level-2-container.svg`](diagrams/c4-level-2-container.svg) · notes in [c4-container.md](./c4-container.md)

## Technology Stack

| Layer | Choice |
| --- | --- |
| Frontend | React (SPA) + Vite |
| Backend | Python + Flask (microservices) |
| Inter-service communication | REST / JSON over HTTP |
| Database | PostgreSQL |
| File storage | S3-compatible object storage |
| Packaging | Docker + Docker Compose |
| Deployment | Backend as containers on a cloud host; frontend on Vercel |

Per-layer rationale and the alternatives we weighed are in [tech_stack.md](./tech_stack.md). Full trade-offs are in [ADR-001: Core Technology Stack](./adr/0001-tech-stack-selection.md).

## Architecture Decision Records

- [ADR-001 — Selection of Core Technology Stack](./adr/0001-tech-stack-selection.md)
- [ADR-002 — Use RESTful APIs for Internal Service Communication](./adr/0002-use-restful-api-internal-communication.md)
- [ADR-003 — Narrow the First Running Slice to One Service and Local File Storage](./adr/0003-tracer-bullet-scope.md)

> ⚠️ The C4 Container diagram above describes the **target** architecture. What `docker compose up` actually starts today is narrower — one `notes-service` plus `stats-service`, no gateway and no auth. See ADR-003.

## Editing the diagrams

Each diagram is kept in two forms in `diagrams/`, both with an English and a Thai version:

- `*.mmd` — the Mermaid text source (`C4Context` for Level 1, `C4Container` for Level 2), reviewable as a diff in a PR. Both are also embedded in [c4-context.md](./c4-context.md) and [c4-container.md](./c4-container.md).
- `*.svg` — a hand-positioned drawing of the same content, and the `.png` next to it is the export shown in this README.

To change a diagram, update **both** forms so they keep saying the same thing, then export the `.png` at 1600px wide (open the SVG in a browser and export, or use any SVG-to-PNG tool). Keep the same basename. Both language versions share identical geometry, so a layout change made in one can be copied straight into the other.

The rendered images come from the SVG rather than from Mermaid because Mermaid's `C4Container` renderer overlaps the boundary label with the relationship labels and ignores the shapes-per-row setting, which makes Level 2 unreadable; Level 1 crowds its full-length relationship labels for the same reason. The Mermaid sources still parse cleanly (checked with `mermaid-cli`). See [c4-container.md](./c4-container.md) for the details.
