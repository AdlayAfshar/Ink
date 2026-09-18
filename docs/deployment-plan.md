# Deployment Plan

## Stage 1: Local Development

Run the FastAPI app locally with a local PostgreSQL database. Keep configuration environment-based.

## Stage 2: Docker Compose

Add Docker and Docker Compose for repeatable local startup of the API and PostgreSQL.

## Stage 3: Managed PostgreSQL

Use Google Cloud SQL for the deployed PostgreSQL database.

The Cloud SQL instance is:

```text
ink-postgres
```

The instance runs PostgreSQL 16 in the same region as the Cloud Run service:

```text
europe-west2
```

The application database is:

```text
ink
```

A dedicated database user named `ink_app` is used by the deployed backend instead of the PostgreSQL administrator account.

Database credentials are not stored in the repository or directly in the Cloud Run configuration. The production database URL is stored in Google Secret Manager as:

```text
ink-database-url
```

Cloud Run exposes this secret to the application as:

```text
DATABASE_URL
```

The Cloud Run service is configured with the Cloud SQL connection:

```text
ink-backend-adlay:europe-west2:ink-postgres
```

The Cloud Run service account has the `Cloud SQL Client` role for database connectivity and the `Secret Manager Secret Accessor` role for reading runtime secrets.

### Production Database Migrations

Production migrations are run as a one-off Cloud Run Job rather than automatically when the API container starts.

The migration job is:

```text
ink-db-migrate
```

It uses the same backend container image, `DATABASE_URL` secret, Cloud SQL connection, and service account as the deployed API.

The job runs:

```bash
alembic upgrade head
```

Running migrations separately avoids having multiple Cloud Run API instances attempt to apply the same migration during application startup.

Alembic escapes percent signs when copying `DATABASE_URL` into its configuration because URL-encoded database passwords may contain percent-encoded characters.

### Credential Rotation

Database credentials should be rotated without committing credentials to the repository.

To rotate the application database credentials:

1. Change the password for the `ink_app` Cloud SQL user.
2. Build a new `DATABASE_URL` using the new password.
3. Add the updated value as a new version of the `ink-database-url` Secret Manager secret.
4. Redeploy the Cloud Run service so new instances use the updated secret.
5. Verify database connectivity and the deployed authentication flow.
6. Disable obsolete secret versions after the new credentials have been verified.

The PostgreSQL administrator account is reserved for database administration and is not used by the application.

## Stage 4: Cloud Deployment

Use GCP as the first production deployment platform.

Deploy the FastAPI container to Cloud Run and use Cloud SQL for managed PostgreSQL. Use Artifact Registry for container images, Secret Manager for secrets, Cloud Logging for logs and monitoring, and IAM service accounts for permissions.

AWS ECS Express Mode with RDS PostgreSQL has been evaluated as an alternative deployment path and is reserved for a future learning exercise.

Render and Fly.io were also evaluated as simpler deployment alternatives, but GCP was selected because it provides a better balance between infrastructure learning and deployment complexity for Ink.

See `architecture-decisions/0005-choose-deployment-platform.md` for the full platform comparison and decision.

### Manual Cloud Run Deployment

The backend was manually deployed to Google Cloud Run before introducing automated deployment.

Google Cloud project:

```text
ink-backend-adlay
```

Region:

```text
europe-west2
```

Required Google Cloud APIs:

```text
Cloud Run
Artifact Registry
Cloud Build
Secret Manager
```

A Docker repository named `ink` was created in Artifact Registry.

The backend image was built for `linux/amd64` and pushed to:

```text
europe-west2-docker.pkg.dev/ink-backend-adlay/ink/ink-api:latest
```

"Because the Cloud Run service is configured for x86_64 architecture, the image must explicitly target linux/amd64 when built from an Apple Silicon development machine to prevent a runtime deployment crash."

```bash
docker buildx build \
  --platform linux/amd64 \
  -t europe-west2-docker.pkg.dev/ink-backend-adlay/ink/ink-api:latest \
  --push \
  .
```

The production JWT secret is stored in Secret Manager as:

```text
ink-jwt-secret
```

The Cloud Run service account was granted the `Secret Manager Secret Accessor` role so the service can read the secret at runtime.

The backend was deployed with:

```bash
gcloud run deploy ink-api \
  --image=europe-west2-docker.pkg.dev/ink-backend-adlay/ink/ink-api:latest \
  --region=europe-west2 \
  --allow-unauthenticated \
  --set-env-vars=ENVIRONMENT=production,DEBUG=false,DATABASE_URL=postgresql+psycopg://placeholder:placeholder@placeholder/ink,CORS_ALLOWED_ORIGINS=https://example.com \
  --set-secrets=JWT_SECRET_KEY=ink-jwt-secret:latest
```

`CORS_ALLOWED_ORIGINS` remains a temporary placeholder until the frontend is deployed. The deployed backend now receives `DATABASE_URL` from the `ink-database-url` Secret Manager secret.

The deployed service is available at:

```text
https://ink-api-850771094851.europe-west2.run.app
```

The public health endpoint was verified with:

```bash
curl https://ink-api-850771094851.europe-west2.run.app/health
```

Response:

```json
{"status":"ok"}
```

Cloud Run logs were checked with:

```bash
gcloud run services logs read ink-api \
  --region=europe-west2 \
  --limit=30
```

The logs confirmed successful application startup, Uvicorn listening on port `8080`, and a `200 OK` response from `/health`.

## Stage 5: CI/CD

Add automated tests, migration checks, and deployment workflows through GitHub Actions.

## Stage 6: Monitoring and Logging

Add structured logging, error tracking, request metrics, and database monitoring before treating the service as production-ready.