# Personal Glossary / Vocabulary Learning Platform

## Overview

Personal Glossary is a backend-first vocabulary learning platform. It helps users search for words, save vocabulary to a personal glossary, add notes and tags, track learning status, and eventually review words with spaced repetition.

This is not intended to be a simple dictionary clone. The project is designed as a long-term backend engineering portfolio project that demonstrates thoughtful API design, data modelling, authentication, external API integration, caching, testing, documentation, and production readiness.

## Why This Project Exists

The goal is to build a real product while practicing the engineering skills expected from an industry-ready backend/software engineer. Each milestone should introduce a concrete engineering problem: modelling shared versus user-owned data, designing clean boundaries, integrating with external services, adding reliable tests, and preparing the system for deployment.

## Portfolio Goals

This repository should eventually show:

- Clean backend architecture using FastAPI
- REST API design with clear resource boundaries
- PostgreSQL schema design and migrations
- Authentication and authorization
- External dictionary provider integration behind an abstraction
- Caching of shared dictionary data
- Automated testing with pytest
- Clear technical documentation and architecture decisions
- Incremental delivery through GitHub Issues and pull requests

## Planned Architecture

The first implementation will be a modular monolith. The backend is organized around modules such as `auth`, `dictionary`, `glossary`, `reviews`, and `tags`. Shared dictionary data, such as words and definitions, is separate from user-specific data, such as saved words, notes, tags, and review history.

The system uses a FastAPI backend and PostgreSQL database. Dictionary lookups are handled through a provider abstraction, with Free Dictionary as the primary provider and Merriam-Webster as a fallback provider.

## Learning Outcomes

The project is intended to build practical experience with:

- FastAPI application structure
- RESTful API design
- PostgreSQL data modelling
- SQLAlchemy ORM patterns
- Alembic migrations
- JWT authentication
- External API integration
- Caching strategies
- Unit and integration testing
- Docker-based local development
- CI/CD, deployment, and observability

## Local Backend Setup

Requirements:

- Python 3.11+. Python 3.11.x is recommended for local development via `.python-version`; Docker and CI should use Python 3.11.x for consistency.
- `pip`

This project uses `pyproject.toml` with standard `pip` editable installs. Poetry is not part of the supported workflow.

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install runtime and development dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run the API:

```bash
python -m uvicorn backend.app.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Run tests:

```bash
python -m pytest
```

Verify form parsing support for the login route:

```bash
python -c "import multipart; print('python-multipart installed')"
```

## Local Frontend Setup

Requirements:

- Node.js
- npm

Install frontend dependencies:

```bash
cd frontend
npm install
```

Create a `frontend/.env` file with the backend API URL:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Run the frontend:

```bash
npm run dev
```

The frontend is available at:

```text
http://localhost:5173
```

Build the frontend:

```bash
npm run build
```

Run the frontend linter:

```bash
npm run lint
```

## Run Frontend and Backend Together

Start the backend from the repository root:

```bash
python -m uvicorn backend.app.main:app --reload
```

In a separate terminal, start the frontend:

```bash
cd frontend
npm run dev
```

The local services are available at:

```text
Frontend: http://localhost:5173
Backend:  http://localhost:8000
```

The frontend sends dictionary lookup requests to the backend using the API URL configured by `VITE_API_BASE_URL`.

## Deployment

The application is deployed on Google Cloud Platform, with both the frontend and backend running on Google Cloud Run.

### Frontend

The public React/Vite frontend is available at:

```text
https://ink-frontend-850771094851.europe-west2.run.app
```

The frontend is built as a production Docker image using a multi-stage build.

The first stage uses Node.js to install dependencies and create the Vite production build. The resulting static files are then copied into an Nginx image, which serves the application on port `8080` for Cloud Run.

The production backend URL is supplied through `VITE_API_BASE_URL` when the frontend image is built.

The frontend container image is stored in Google Artifact Registry and deployed to the `ink-frontend` Cloud Run service.

### Backend

The production FastAPI backend is available at:

```text
https://ink-api-850771094851.europe-west2.run.app
```

The backend runs as the `ink-api` Google Cloud Run service.

Production PostgreSQL is hosted on Google Cloud SQL.

Sensitive production configuration, including the database URL, JWT secret, and Merriam-Webster API key, is stored in Google Cloud Secret Manager and exposed to the backend Cloud Run service as environment variables.

### CORS

The production backend allows browser requests from the deployed frontend origin:

```text
https://ink-frontend-850771094851.europe-west2.run.app
```

This allows the frontend Cloud Run service to make browser-based requests to the backend Cloud Run service.

### Production Architecture

```text
Browser
   |
   v
Cloud Run
ink-frontend
   |
   v
Cloud Run
ink-api
   |
   v
Cloud SQL
PostgreSQL
```

Production secrets used by the backend are managed through Google Cloud Secret Manager.

### Deployment Verification

The production integration has been manually verified by:

- Opening the public Cloud Run frontend
- Searching for a dictionary word
- Sending the lookup request to the production Cloud Run API
- Receiving a successful API response
- Confirming the backend CORS configuration allows the production frontend origin
- Confirming the dictionary result is rendered correctly in the frontend

## Current Status

The project includes a deployed FastAPI backend, managed PostgreSQL database, public React/Vite frontend, dictionary provider fallback, production CORS configuration, automated tests, continuous backend deployment, and production logging.

## Run Backend with Docker

Build the backend Docker image:

```bash
docker build -t ink-api .
```

## Run Frontend with Docker

Build the frontend image with the backend API URL:

```bash
docker build \
  --platform linux/amd64 \
  --build-arg VITE_API_BASE_URL=http://localhost:8000 \
  -t ink-frontend \
  ./frontend
```

Run the frontend container:

```bash
docker run --rm \
  -p 8080:8080 \
  ink-frontend
```

The containerized frontend is then available at:

```text
http://localhost:8080
```