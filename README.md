# DatApp

DatApp is a web application for uploading tabular datasets, assessing data
quality, calculating statistics, creating visualizations, and exporting analysis
results. Development is intentionally incremental so that each architectural and
engineering decision remains understandable.

The project begins as a modular monolith: the frontend and backend are separate
applications in one repository, with one backend deployment and one PostgreSQL
database. This keeps the system straightforward while leaving clear module
boundaries for future growth.

## Initial technology stack

- Frontend: React, TypeScript, Vite, and Tailwind CSS
- Backend: Python, FastAPI, Pydantic, SQLAlchemy 2, and Alembic
- Database: PostgreSQL, run locally with Docker Compose
- Data processing (later phase): Polars, DuckDB, and OpenPyXL
- Quality tools: Ruff, Pytest, and ESLint

No frontend or backend application has been scaffolded yet. The current step
only establishes the repository foundation.

## Repository structure

```text
DatApp/
|-- frontend/          # React application boundary
|-- backend/           # FastAPI application boundary
|-- .env.example       # Documented, non-secret configuration template
|-- .gitignore         # Files that must remain outside version control
`-- README.md          # Project overview and development roadmap
```

The `frontend` and `backend` directories contain short boundary notes for now.
Each application will receive its own source layout, dependency configuration,
tests, and documentation when it is scaffolded in a later step.

## Local development prerequisites

Install the following software before application setup:

- Git
- Node.js (current LTS) and npm
- Python 3.12 or another version selected during backend setup
- Docker Desktop with Docker Compose
- A code editor such as Visual Studio Code

PostgreSQL does not need a separate host installation because it will run in
Docker. Exact supported versions and setup commands will be pinned when the
frontend and backend are scaffolded.

## Planned development phases

1. Repository foundation and architecture documentation
2. Backend scaffold, configuration, health endpoint, and tests
3. Frontend scaffold, shared layout, and backend connectivity check
4. PostgreSQL and Docker Compose development environment
5. User authentication and authorization boundaries
6. Analysis projects and ownership-aware database models
7. Secure CSV/XLSX upload and storage workflow
8. Dataset validation, preview, and column detection
9. Data-quality profiling and basic statistics
10. Visualization recommendations and result export
11. AI-assisted insights and usage limits, only after the core product is stable

Each phase will be split into small, testable steps. Billing, subscriptions,
machine learning, and advanced AI features are outside the initial scope.

## Configuration

Copy `.env.example` to `.env` when local services are introduced, then replace
the development-only example values as needed. Never commit `.env` or real
credentials.

