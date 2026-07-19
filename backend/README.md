# DatApp Backend

The backend is a FastAPI application with typed configuration, async SQLAlchemy
database access, Alembic migrations, and PostgreSQL-backed integration tests.

## Setup

Run from this `backend/` directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

The repository-root `.env` file is loaded automatically. PostgreSQL must be
running through `docker compose up -d database` from the repository root.

## Checks

```powershell
python -m ruff check .
python -m ruff format --check .
python -m pytest
python -m alembic check
```

Integration tests use the local PostgreSQL schema inside a transaction and roll
back after each test. If PostgreSQL is unavailable, database-dependent tests are
reported as skipped rather than corrupting local state.
