# DatApp Backend

The backend is a FastAPI application with typed configuration, async SQLAlchemy
database access, Alembic migrations, and PostgreSQL-backed integration tests.

## Application boundaries

- `app/models`: persistence entities and relationships
- `app/repositories`: workspace-scoped database queries
- `app/services`: transaction-aware ownership and role rules
- `app/auth`: provider-neutral OIDC token verification and identity data
- `app/api`: HTTP transport and reusable authentication dependencies; currently
  public health endpoints and the protected current-user endpoint

Workspace creation also creates its owner membership in the same request
transaction. Project reads are always scoped through workspace membership.
Owner, admin, and editor roles may create projects; viewers are read-only.

## Authentication boundary

Protected routes will depend on `get_current_user`. The dependency validates a
managed-provider access token with an explicit algorithm, issuer, audience,
required claims, and a cached JWKS signing key. A valid first login creates the
local user; an email already linked to another provider subject is rejected.

Set `AUTH_ISSUER`, `AUTH_AUDIENCE`, `AUTH_JWKS_URL`, and `AUTH_ALGORITHM` in the
repository-root `.env` file after selecting an identity provider. Until then,
health endpoints remain available and any protected dependency returns a safe
`503` response. Real provider credentials and tokens must never be committed.

`GET /api/v1/auth/me` is the first protected endpoint. It returns the current
local user's safe public profile and deliberately excludes the provider subject.

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
