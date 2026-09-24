# Backend

FastAPI backend for the Personal Glossary / Vocabulary Learning Platform.

## Dependency Workflow

Use Python 3.11+ (recommended: 3.11.x per `.python-version`) and install dependencies from the root `pyproject.toml` with `pip`.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

The project does not use Poetry. Runtime dependencies and the `dev` extra are declared in `pyproject.toml`.

## Run Locally

```bash
python -m uvicorn backend.app.main:app --reload
```

## Logging

The backend uses Python's standard `logging` module for application logs.

Logs are written to standard output so they are visible both during local development and in Cloud Run.

Application startup logs include the current environment:

```text
INFO backend.app.main Application starting environment=local
```

Dictionary provider failures are logged with useful diagnostic information such as the requested word, HTTP status code, exception type, and fallback provider usage.

Sensitive values such as passwords, JWT secrets, database credentials, API keys, authorization headers, and access tokens must never be written to logs.

### Local Logs

Run the application locally:

```bash
python -m uvicorn backend.app.main:app --reload
```

Application logs are written directly to the terminal.

### Cloud Run Logs

View recent logs for the deployed Cloud Run service with:

```bash
gcloud run services logs read ink-api \
  --region=europe-west2
```

To follow new logs as they are produced:

```bash
gcloud beta run services logs tail ink-api \
  --region=europe-west2
```

Logs can also be inspected in Google Cloud Console through Cloud Run or Logs Explorer.

## Docker Compose

Docker Compose can run the FastAPI application and PostgreSQL together for local development.

From the repository root, create the Compose environment file:

```bash
cp .env.example .env
```

Start the API and PostgreSQL services:

```bash
docker compose up --build
```

Start the services in the background:

```bash
docker compose up -d
```

Apply database migrations inside the API container:

```bash
docker compose run --rm api alembic upgrade head
```

Check the current migration revision:

```bash
docker compose run --rm api alembic current
```

Verify the API health endpoint:

```bash
curl http://localhost:8000/health
```

Stop the services:

```bash
docker compose down
```

The API connects to PostgreSQL through the Compose service hostname `postgres` instead of `localhost`.

The Compose database connection is:

```text
postgresql+psycopg://postgres:postgres@postgres:5432/ink
```

PostgreSQL data is stored in the named `postgres_data` volume, so database data persists when containers are stopped and recreated.

To remove the containers and delete the PostgreSQL volume:

```bash
docker compose down -v
```

## Current Endpoints

- `GET /`: service metadata.
- `GET /health`: health check.

## Structure

- `app/main.py`: FastAPI application entry point.
- `app/core`: shared configuration and infrastructure code.
- `app/modules/auth`: authentication module.
- `app/modules/dictionary`: dictionary lookup and shared word data.
- `app/modules/glossary`: user saved words.
- `app/modules/reviews`: spaced repetition and review history.
- `app/modules/tags`: user tags.

## Environment Variables

The application configuration is managed through environment variables. If a variable is not provided, the default value defined in `app/core/config.py` will be used.

Create a `.env` file in the `backend` directory to override the defaults.

| Variable | Default | Description |
| --- | --- | --- |
| `APP_NAME` | `Personal Glossary API` | The application name. |
| `ENVIRONMENT` | `local` | The application environment. |
| `DATABASE_URL` | `postgresql+psycopg:///ink` | PostgreSQL connection URL used by the application. |
| `TEST_DATABASE_URL` | `postgresql+psycopg:///ink_test` | Dedicated PostgreSQL database used by tests. |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000,http://localhost:5173` | Comma-separated list of frontend origins allowed to call the API. |
| `MERRIAM_WEBSTER_API_BASE_URL` | `https://www.dictionaryapi.com/api/v3/references/learners/json` | Base URL for the Merriam-Webster Learner's Dictionary API used as the fallback dictionary provider. |
| `MERRIAM_WEBSTER_API_KEY` | None | API key used to authenticate requests to the Merriam-Webster fallback provider. |
| `MERRIAM_WEBSTER_API_TIMEOUT` | `5.0` | Timeout in seconds for requests to the Merriam-Webster fallback provider. |

Example:

```env
APP_NAME=Personal Glossary API
ENVIRONMENT=local
DATABASE_URL=postgresql+psycopg:///ink
TEST_DATABASE_URL=postgresql+psycopg:///ink_test
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
MERRIAM_WEBSTER_API_KEY=
```

The Free Dictionary API is the primary external dictionary provider.

Merriam-Webster Learner's Dictionary is the fallback provider. It is used when the primary provider fails because of an upstream service error, timeout, or connection failure.

A successful response from the primary provider does not trigger the fallback provider. A word-not-found response from the primary provider also does not trigger fallback and continues to produce the normal `404` response.

Dictionary lookups remain database-first. If a word is already stored locally, the stored entry is returned without calling either external provider. Successful results from either the primary or fallback provider are persisted for future lookups.

The fallback provider is optional. If `MERRIAM_WEBSTER_API_KEY` is not configured, dictionary lookups continue to use only the primary Free Dictionary provider.

Never commit a real Merriam-Webster API key to the repository. Store the key in local environment configuration for development and use a secret manager for deployed environments.

## Test Database

Persistence-related tests use a dedicated local PostgreSQL database named `ink_test`.

Tests must not write to the normal development database.

Create the test database once before running the test suite:

```bash
createdb ink_test
```

Alternatively, create it through PostgreSQL:

```bash
psql -U postgres
```

Then run:

```sql
CREATE DATABASE ink_test;
```

The default test database connection is:

```text
postgresql+psycopg:///ink_test
```

The pytest database fixture creates all SQLAlchemy tables before each test and drops them after each test. This keeps persistence tests isolated and prevents state from leaking between tests.

FastAPI's normal `get_db` dependency is overridden during tests so API requests use the test database session instead of the development database.

Persistence tests require a local PostgreSQL server and an existing `ink_test` database.

## Running Tests

Run the full test suite from the project root:

```bash
python -m pytest
```

Run only database isolation tests:

```bash
python -m pytest -k database_isolation -v
```

A successful isolation test confirms that the same unique-constrained value can be created in separate tests without conflicts because each test starts with clean database tables.

## Database Migrations

This project uses Alembic to manage database schema changes.

Create a new migration:

```bash
alembic revision -m "create users table"
```

Apply the latest migrations:

```bash
alembic upgrade head
```

Revert the most recent migration:

```bash
alembic downgrade -1
```

## Production Database

The deployed backend uses Google Cloud SQL for PostgreSQL.

The production database runs on the `ink-postgres` Cloud SQL instance in `europe-west2`. The application connects to the `ink` database using the dedicated `ink_app` database user.

Production database credentials are not stored in the repository. The complete production `DATABASE_URL` is stored in Google Secret Manager as `ink-database-url` and exposed to the Cloud Run service as the `DATABASE_URL` environment variable.

The Cloud Run service connects to Cloud SQL using:

```text
ink-backend-adlay:europe-west2:ink-postgres
```

### Production Migrations

Production migrations are executed separately from the API service using the `ink-db-migrate` Cloud Run Job.

The job runs:

```bash
alembic upgrade head
```

The migration job uses the same container image, Cloud SQL connection, and `DATABASE_URL` secret as the deployed backend.

Do not automatically run migrations when the API container starts. Keeping migrations separate prevents multiple Cloud Run instances from attempting to modify the database schema at the same time.

### Verifying Database Connectivity

After deploying the API and applying migrations, verify the deployed authentication flow:

1. Register a test user with `POST /auth/register`.
2. Log in with `POST /auth/login`.
3. Use the returned bearer token with `GET /auth/me`.

A successful register, login, and authenticated read confirms that the deployed backend can write to and read from the managed PostgreSQL database.

### Rotating Database Credentials

To rotate production database credentials:

1. Change the password for the `ink_app` Cloud SQL user.
2. Build a new `DATABASE_URL` with the new password.
3. Add it as a new version of the `ink-database-url` Secret Manager secret.
4. Redeploy the Cloud Run service.
5. Verify database connectivity and the authentication flow.
6. Disable obsolete secret versions after the new credentials have been verified.

Never commit production database credentials or the production `DATABASE_URL` to the repository.

## CORS Configuration

CORS allowed origins are configured through the `CORS_ALLOWED_ORIGINS` environment variable.

For local development:

```env
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

For production, set this variable to the deployed frontend origin:

```env
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.example.com
```

Multiple origins can be provided as a comma-separated list.

Production configuration must use explicit origins and must not use `*` when credentials are enabled.