# Deployment Plan

## Stage 1: Local Development

Run the FastAPI app locally with a local PostgreSQL database. Keep configuration environment-based.

## Stage 2: Docker Compose

Add Docker and Docker Compose for repeatable local startup of the API and PostgreSQL.

## Stage 3: Managed PostgreSQL

Move database hosting to a managed PostgreSQL provider for staging or production.

## Stage 4: Cloud Deployment

Use GCP as the first production deployment platform.

Deploy the FastAPI container to Cloud Run and use Cloud SQL for managed PostgreSQL. Use the appropriate GCP services for container images, secrets, logging, and runtime configuration.

AWS ECS Express Mode with RDS PostgreSQL has been evaluated as an alternative deployment path and is reserved for a future learning exercise.

See `architecture-decisions/0005-choose-deployment-platform.md` for the platform comparison and decision.

## Stage 5: CI/CD

Add automated tests, migration checks, and deployment workflows through GitHub Actions.

## Stage 6: Monitoring and Logging

Add structured logging, error tracking, request metrics, and database monitoring before treating the service as production-ready.
