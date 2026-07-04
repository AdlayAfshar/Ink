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
|----------|---------|-------------|
| `APP_NAME` | `Personal Glossary API` | The application name. |
| `ENVIRONMENT` | `local` | The application environment (for example: `local`, `development`, `test`, or `production`). |

Example:

```env
APP_NAME=Personal Glossary API
ENVIRONMENT=local
```