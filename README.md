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

The system will start with a FastAPI backend and PostgreSQL database. Dictionary lookups will initially use the Free Dictionary API through a provider abstraction so the source can be replaced or extended later.

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

- Python 3.11+
- `pip`

Install dependencies:

```bash
pip install -e ".[dev]"
```

Run the API:

```bash
uvicorn backend.app.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Run tests:

```bash
pytest
```

## Current Status

Foundation phase. The repository contains initial documentation, project structure, GitHub workflow templates, and a minimal FastAPI application with root and health endpoints.
