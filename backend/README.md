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
