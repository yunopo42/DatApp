# DatApp Development Tracker

This file is the source of truth for DatApp implementation progress. Update it
in the same commit that completes a tracked task. Do not place credentials,
personal data, access tokens, or environment-specific secrets in this file.

## Status legend

- `[x]` Completed and verified
- `[ ]` Not started or still in progress
- **Current** The smallest milestone the project is actively implementing
- **Deferred** Intentionally excluded until its planned phase

## Verified baseline

Last verified: 2026-07-20

- Frontend lint passes with ESLint.
- Frontend TypeScript and Vite production build pass.
- Backend Ruff lint and formatting checks pass.
- Backend test suite passes: 26 tests.
- Alembic reports no pending model migration operations.
- Python dependency check reports no broken requirements.
- PostgreSQL runs in Docker and reports healthy.
- Supabase session, ES256 JWT verification, FastAPI profile provisioning, and
  the local PostgreSQL user record have been verified end to end.
- The browser dashboard reports frontend online, backend online, and database
  healthy without console errors.
- Workspace creation, refresh, sign-out, and sign-in persistence have been
  verified in the browser against live PostgreSQL data.
- Workspace membership roles now drive project creation permissions in the
  live frontend while the backend remains authoritative.

## Completed milestones

### M0 — Repository and local development foundation

- [x] Create the Git repository and public GitHub repository.
- [x] Establish the `frontend/` and `backend/` application boundaries.
- [x] Add root environment examples and ignore real `.env` values.
- [x] Verify Git, Python, Node.js, npm, Docker, and Docker Compose.
- [x] Run PostgreSQL locally through Docker Compose.

### M1 — Frontend application foundation

- [x] Create the React 19, TypeScript, and Vite application.
- [x] Configure Tailwind CSS and ESLint.
- [x] Build the responsive DatApp dashboard shell.
- [x] Add the animated dark-violet to light-violet visual theme.
- [x] Display live FastAPI and PostgreSQL readiness state.
- [x] Load shared root environment variables safely through Vite.

### M2 — Backend and database foundation

- [x] Create the FastAPI application and typed Pydantic settings.
- [x] Add liveness and database readiness endpoints.
- [x] Configure async SQLAlchemy 2 sessions.
- [x] Configure Alembic migrations.
- [x] Add safe CORS configuration for the local frontend.
- [x] Add useful readiness and authentication diagnostics without logging
  secrets.
- [x] Add a Windows-compatible `python -m app` launcher using an asyncio event
  loop supported by async Psycopg.

### M3 — Identity, workspace, and project domain foundation

- [x] Create user, workspace, workspace-member, and project models.
- [x] Create the initial database migration.
- [x] Add repository and service boundaries.
- [x] Enforce workspace membership and project role rules.
- [x] Create authenticated workspace list/create API endpoints.
- [x] Create authenticated project list/create API endpoints.
- [x] Test ownership, membership, role, validation, conflict, and isolation
  behavior.

### M4 — Supabase authentication integration

- [x] Configure Supabase with a frontend publishable key only.
- [x] Keep service-role and secret keys out of the frontend and repository.
- [x] Implement email/password account creation, sign-in, and sign-out.
- [x] Make account creation and form focus accessible from the dashboard.
- [x] Verify Supabase ES256 tokens with the public JWKS endpoint.
- [x] Protect the current-user, workspace, and project API endpoints.
- [x] Provision the authenticated Supabase user in local PostgreSQL.
- [x] Synchronize the frontend session with `GET /api/v1/auth/me`.
- [x] Display a safe backend profile verification state in onboarding.

## Completed milestone history

### M5 — Authenticated workspace experience

Goal: allow a signed-in user to create, list, and select a real workspace from
the dashboard. No mock workspace data should remain when this milestone is
complete.

- [x] **W-01:** Add a typed frontend API client for workspace list and create
  requests using the current Supabase access token.
- [x] **W-02:** Load the signed-in user's workspaces and represent loading,
  empty, error, and ready states.
- [x] **W-03:** Add a focused create-workspace form with name and URL-safe slug
  fields.
- [x] **W-04:** Display safe backend validation and slug-conflict errors.
- [x] **W-05:** Show created workspaces in the dashboard and allow one to be
  selected.
- [x] **W-06:** Replace the placeholder workspace onboarding step with live
  completion state.
- [x] **W-07:** Verify create, refresh, sign-out, and sign-in persistence in the
  browser.

Acceptance criteria:

- A signed-in user can create a workspace without manually calling the API.
- Only the authenticated user's memberships are listed.
- Duplicate or invalid slugs produce a clear, safe message.
- Refreshing the page preserves the workspace through PostgreSQL persistence.
- Frontend lint/build and all backend checks still pass.

## Recently completed milestone

### M6 — Project experience

- [x] Add a typed frontend project API client.
- [x] List projects for the selected workspace.
- [x] Add a create-project form with name and optional description.
- [x] Respect owner, admin, editor, and viewer permissions in the UI.
- [x] Replace dashboard project placeholders with live data.

Acceptance criteria:

- Projects are always loaded from the active workspace's protected API.
- Owner, admin, and editor roles can create projects; viewer cannot.
- A created project persists in PostgreSQL and updates the live dashboard.
- Frontend lint/build and all backend checks pass without browser console
  errors.

## Current milestone

### M7 — Secure dataset upload and storage

- [x] Define dataset and stored-file database models.
- [x] Create and verify the required Alembic migration.
- [ ] Define file-size, extension, MIME, and filename policies.
- [ ] Implement workspace/project-scoped CSV and XLSX upload.
- [ ] Store files outside the public web root with generated identifiers.
- [ ] Reject unsafe, unsupported, oversized, or malformed uploads.
- [ ] Add cleanup behavior for failed database or storage operations.

## Planned milestones

### M8 — Workspace collaboration and resource lifecycle

- [ ] Define and document the complete owner, admin, editor, and viewer
  permission matrix for workspaces, projects, datasets, and memberships.
- [ ] Add workspace edit operations with safe name and slug-change rules.
- [ ] Add project edit, archive, restore, and delete operations.
- [ ] Add dataset rename, download, replace, and delete operations with atomic
  database and stored-file cleanup.
- [ ] Add role-aware overflow menus to workspace, project, and dataset cards.
- [ ] Allow owner and admin roles to manage members; prevent editor and viewer
  roles from changing membership or destructive workspace settings.
- [ ] Allow non-owner members to leave a workspace and require the owner to
  transfer ownership before leaving.
- [ ] Define project-level membership or explicit access overrides so a user
  can leave one project without leaving the entire workspace.
- [ ] Create cryptographically random, human-readable workspace invitation
  codes with hashed storage, expiry, usage limits, and revocation.
- [ ] Allow owner and admin roles to issue invitation codes for viewer or editor
  access only; never grant owner or admin through a redeemable code.
- [ ] Add authenticated, rate-limited invitation redemption with duplicate
  membership protection and safe error messages.
- [ ] Add member listing, role changes, removal, invite management, and join/
  leave history to the workspace UI.
- [ ] Require an impact preview and typed workspace-name confirmation before an
  owner or admin can delete a workspace.
- [ ] Implement recoverable workspace deletion with retention, cleanup, and
  protection against orphaned database records or stored files.
- [ ] Record auditable events for invitations, joins, leaves, role changes,
  edits, archives, restores, and destructive operations.
- [ ] Test permission boundaries, last-owner protection, expired/revoked/
  exhausted codes, rate limits, concurrent redemption, and cleanup failures.

Acceptance criteria:

- Every card action is derived from the authenticated user's effective role.
- Members can leave the correct scope without gaining or retaining unintended
  access.
- Invitation codes cannot be guessed, reused beyond policy, elevated to admin,
  or recovered from the database.
- Destructive operations clearly show their impact and cannot leave orphaned
  data or files.

### M9 — Dataset validation and preview

- [ ] Detect CSV encoding and delimiter safely.
- [ ] Read CSV data with Polars.
- [ ] Read XLSX metadata and sheets with OpenPyXL.
- [ ] Detect column names and initial data types.
- [ ] Produce a bounded preview without loading an entire large file into the
  browser.
- [ ] Report row-level and column-level validation problems.

### M10 — Deterministic analysis and data quality

- [ ] Calculate missing-value, uniqueness, duplicate, and type-quality metrics.
- [ ] Produce descriptive statistics for supported column types.
- [ ] Use DuckDB where SQL-style local analysis is appropriate.
- [ ] Persist analysis runs and deterministic results.
- [ ] Display progress, success, and failure states.

### M11 — Visualization and export

- [ ] Recommend chart types from deterministic column metadata.
- [ ] Build interactive charts from verified analysis results.
- [ ] Export selected results to CSV and XLSX.
- [ ] Add report-ready summaries and safe download endpoints.

### M12 — Predictive modeling foundation

Design reference: [Predictive Modeling Design](docs/PREDICTIVE_MODELING.md)

- [ ] Define experiment, training-run, model-artifact, and prediction-run
  records scoped through workspace, project, and dataset ownership.
- [ ] Add regression and classification problem definitions with explicit
  target, feature, metric, and split configuration.
- [ ] Validate minimum row counts, target suitability, class balance, missing
  values, and unsupported feature types before training.
- [ ] Build leak-resistant scikit-learn preprocessing and baseline pipelines.
- [ ] Support reproducible train/test splits and cross-validation with stored
  random seeds, package versions, parameters, and dataset identity.
- [ ] Calculate problem-appropriate metrics and compare every trained model
  with a simple baseline.
- [ ] Run training outside request handlers with queued, running, succeeded,
  failed, and cancelled states.
- [ ] Present model comparison, limitations, feature importance, and safe error
  messages in the UI.
- [ ] Store only server-generated model artifacts and generate batch
  predictions for compatible datasets.
- [ ] Test workspace isolation, role permissions, leakage prevention,
  reproducibility, failure cleanup, and artifact access.

### M13 — Advanced modeling and model lifecycle

- [ ] Add time-aware validation and forecasting for suitable ordered datasets.
- [ ] Add clustering and anomaly-detection workflows with suitable evaluation
  summaries.
- [ ] Add controlled hyperparameter search with resource and time limits.
- [ ] Track model versions, promotion, archival, and prediction lineage.
- [ ] Detect input-schema drift and report model performance when labels become
  available.
- [ ] Add scheduled batch prediction and retraining policies with explicit user
  control.

### M14 — Stabilization and deployment readiness

- [ ] Add frontend component and API integration tests.
- [ ] Expand backend tests for upload and analysis failure paths.
- [ ] Add production environment validation and startup checks.
- [ ] Re-enable Supabase email confirmation before production.
- [ ] Define backup, retention, deletion, and observability policies.
- [ ] Complete accessibility, responsive-layout, and performance reviews.
- [ ] Document deployment and rollback procedures.

## Deferred scope

Do not start these items until their milestone is explicitly activated:

- User profile and account settings UI
- Turkish and other multilingual interfaces
- Authentication providers beyond the planned email/password flow
- AI-assisted insights
- Subscription plans, billing, and payment integration
- Deep learning, custom user-supplied training code, and unrestricted AutoML

## Local development note

The normal backend port remains `8000`. During the 2026-07-20 Windows session,
an old Uvicorn reload process retained port 8000, so the active ignored `.env`
temporarily points the frontend to port `8001`.

Current temporary commands:

```powershell
# Repository root
docker compose up -d database

# backend/
python -m app --port 8001

# frontend/
npm run dev
```

After the stale Windows process is removed or the computer is restarted, set
`VITE_API_BASE_URL=http://localhost:8000` in the ignored `.env` file and use
`python -m app` from `backend/`.

## Verification commands

Run these before marking a milestone complete.

```powershell
# Repository root
docker compose ps

# backend/
python -m ruff check .
python -m ruff format --check .
python -m pytest
python -m alembic check
python -m pip check

# frontend/
npm run lint
npm run build
```

Also verify the affected user flow in the browser and check that the console
contains no new errors.

## Maintenance rule

When development continues:

1. Read this file before choosing the next task.
2. Work on the first incomplete task in the current milestone unless a new
   requirement explicitly changes the priority.
3. Update checkboxes and the verified baseline in the same commit as the code.
4. Move the **Current** milestone label only after all acceptance criteria pass.
5. Record new deferred ideas without implementing them early.
