# ADR-001: Selection of Core Technology Stack

🌐 **English** · [ภาษาไทย](./0001-tech-stack-selection.th.md)

**Status:** Accepted

**Context:**
NoteShare is a web application that lets university students upload, search, and share lecture notes. We are a team of three students ("The Builders") with existing experience in Python, basic HTML/CSS/JavaScript, Git, and Docker. Our main constraints are the one-semester timeline and the need for rapid prototyping and iteration. We have already decided to build the system as a small set of microservices (see the container diagram in [../README.md](../README.md)), so the stack must support several independently deployable services that communicate over the network and a separate store for uploaded files.

**Decision:**
We have decided to adopt the following core technology stack:

- **Frontend:** React (single-page application) with Vite.
- **Backend:** Python with Flask, organized as a small set of microservices (API Gateway, User & Auth, Notes, Stats).
- **Database:** PostgreSQL as the primary relational store, plus S3-compatible object storage for uploaded note files.
- **Packaging & Deployment:** Docker and Docker Compose for local development; backend services run as containers on a cloud host (e.g., Render/Railway) and the frontend is deployed to Vercel.

**Consequences:**

*   **Positive:**
    - Python/Flask matches the whole team's existing skills and the course material, keeping the learning curve low.
    - React's component model fits NoteShare's interactive, mobile-first UI (search, filter, preview, upload) and is a widely used, employable skill.
    - PostgreSQL's relational model maps cleanly onto the well-defined relationships between users, notes, courses, and credit records.
    - Keeping large files in object storage instead of the database keeps the database small and downloads fast and cheap.
    - Docker gives every member an identical environment and lets each service be built and deployed on its own.
*   **Negative:**
    - A microservices layout adds operational overhead (several services, inter-service calls, more moving parts) that is heavy for a three-person, one-semester project. We accept this to practice service decomposition and keep the number of services small to limit the cost.
    - Splitting the frontend (Vercel) and backend (container host) means two deployment targets, and we must configure CORS and environment variables carefully.
    - Free tiers on hosts such as Render and Vercel can introduce cold starts and resource limits that we need to plan around for demos.
    - We start with a single shared PostgreSQL instance (one schema per service) rather than a full database-per-service, trading strict isolation for simplicity; we can split the databases later if a service needs it.

**Alternatives:**

*   **Monolith vs. microservices:**
    - We considered building NoteShare as a single monolithic Flask application, which would have been simpler for a three-person team to develop, test, and deploy as one deployable unit.
    - We chose to decompose into microservices anyway, to practice service decomposition as a learning goal, accepting the operational overhead already noted above under Negative consequences (more services, inter-service calls, and moving parts for a three-person team).

**Related decisions:**

- [ADR-002: Use RESTful APIs for Internal Service Communication](./0002-use-restful-api-internal-communication.md)
