# DatApp

DatApp is a modular-monolith web application for uploading tabular datasets,
assessing data quality, calculating statistics, creating visualizations, and
exporting reproducible analysis results.

Development is intentionally incremental. AI, billing, subscriptions, and
advanced analytics remain outside the current foundation.

## Technology stack

- Frontend: React 19, TypeScript, Vite, and ESLint
- Backend: Python 3.13, FastAPI, Pydantic, SQLAlchemy 2, and Alembic
- Database: PostgreSQL 18 through Docker Compose
- Quality: Ruff, Pytest, ESLint, TypeScript, and Vite production builds
- Planned data processing: Polars, DuckDB, and OpenPyXL
- Planned styling: Tailwind CSS

## Current foundation

- Typed environment configuration with secret masking
- FastAPI liveness and PostgreSQL readiness endpoints
- Async SQLAlchemy engine and session factory
- Alembic migration infrastructure
- User, workspace, membership, and project domain models
- React and TypeScript development environment
- Backend unit and PostgreSQL integration tests
- Dockerized local PostgreSQL with persistent storage

Authentication, project APIs, file upload, dataset analysis, and AI features are
not implemented yet.

## Repository structure

```text
DatApp/
|-- backend/
|   |-- app/             # FastAPI application and domain code
|   |-- migrations/      # Alembic migration environment and revisions
|   `-- tests/           # Unit and PostgreSQL integration tests
|-- frontend/            # React, TypeScript, and Vite application
|-- compose.yaml         # Local PostgreSQL service
|-- .env.example         # Non-secret configuration template
|-- .gitignore
`-- README.md
```

## Prerequisites

- Git
- Python 3.13
- Node.js 24 and npm
- Docker Desktop with Docker Compose

PostgreSQL does not need a separate Windows installation.

## Local development

Run commands from the repository root unless a step says otherwise.

Create the local configuration once, then replace its development-only password
without committing the file:

```powershell
Copy-Item .env.example .env
```

Start PostgreSQL:

```powershell
docker compose up -d database
```

Prepare and start the backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

In another PowerShell window, prepare and start the frontend:

```powershell
cd frontend
npm install
npm run dev
```

Local endpoints:

- Frontend: `http://127.0.0.1:5173`
- Backend API documentation: `http://127.0.0.1:8000/docs`
- Liveness: `http://127.0.0.1:8000/health/live`
- Readiness: `http://127.0.0.1:8000/health/ready`

## Quality checks

From `backend/`:

```powershell
python -m ruff check .
python -m ruff format --check .
python -m pytest
python -m alembic check
```

From `frontend/`:

```powershell
npm run lint
npm run build
```

## Development phases

1. Repository and local development foundation — completed
2. Typed backend configuration and health checks — completed
3. PostgreSQL, SQLAlchemy, and Alembic foundation — completed
4. Identity, workspace, and project data foundation — completed
5. Authentication and authorization boundaries
6. Project application services and API
7. Secure CSV/XLSX upload and storage
8. Dataset validation, preview, and column detection
9. Data-quality profiling and basic statistics
10. Visualization recommendations and result export
11. AI-assisted insights, only after deterministic analysis is stable

## Configuration safety

`.env.example` documents required variables and is committed. `.env` contains
local values and is ignored by Git. Never commit real credentials or expose the
database URL through API responses and logs.
