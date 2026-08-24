# Backend

FastAPI backend for the Personal Glossary / Vocabulary Learning Platform.

## Run Locally

```bash
uvicorn backend.app.main:app --reload
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
| `DATABASE_URL` | `postgresql+psycopg://postgres:postgres@localhost:5432/ink` | PostgreSQL connection URL used by the application. |
| `TEST_DATABASE_URL` | `postgresql+psycopg://postgres:postgres@localhost:5432/ink_test` | Dedicated PostgreSQL database used by tests. |

Example:

```env
APP_NAME=Personal Glossary API
ENVIRONMENT=local
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/ink
TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/ink_test
```

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
postgresql+psycopg://postgres:postgres@localhost:5432/ink_test
```

The pytest database fixture creates all SQLAlchemy tables before each test and drops them after each test. This keeps persistence tests isolated and prevents state from leaking between tests.

FastAPI's normal `get_db` dependency is overridden during tests so API requests use the test database session instead of the development database.

Persistence tests require a local PostgreSQL server and an existing `ink_test` database.

## Running Tests

Run the full test suite from the project root:

```bash
pytest
```

Run only database isolation tests:

```bash
pytest -k database_isolation -v
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