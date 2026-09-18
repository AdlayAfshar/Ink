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

Because the Cloud Run service is configured for x86_64 architecture, the image must explicitly target `linux/amd64` when built from an Apple Silicon development machine to prevent a runtime deployment crash.

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

Use GitHub Actions to automatically test and deploy backend changes.

### Continuous Integration

The existing test workflow runs the backend test suite on pull requests and pushes to `main`.

The test environment uses PostgreSQL 16 and a dedicated test database.

Pull requests must pass CI before they can be merged into `main`.

### Continuous Deployment

The backend deployment workflow runs when changes are pushed to `main`, including changes merged through pull requests.

The workflow:

1. Runs the backend test suite.
2. Authenticates to Google Cloud using Workload Identity Federation.
3. Configures Docker authentication for Artifact Registry.
4. Builds the backend Docker image for `linux/amd64`.
5. Tags the image with the Git commit SHA.
6. Pushes the image to Artifact Registry.
7. Deploys the image to the `ink-api` Cloud Run service.
8. Verifies the deployed service using the `/health` endpoint.

The deployment job depends on the test job. If the tests fail, deployment does not run.

GitHub Actions authenticates to Google Cloud using Workload Identity Federation instead of a long-lived service account key.

The deployment service account is:

```text
github-deployer@ink-backend-adlay.iam.gserviceaccount.com
```

The Workload Identity configuration restricts access to the `AdlayAfshar/Ink` GitHub repository.

Docker images are pushed to:

```text
europe-west2-docker.pkg.dev/ink-backend-adlay/ink
```

Each deployment uses the Git commit SHA as the image tag so that deployed images can be traced back to their source commits.

### Deployment Verification

After deployment, the workflow checks the public health endpoint.

The equivalent manual check is:

```bash
curl --fail --show-error \
  https://ink-api-850771094851.europe-west2.run.app/health
```

If the health check fails, the deployment workflow is marked as failed.

### Rollback

Cloud Run keeps previous revisions of the deployed service.

Available revisions can be listed with:

```bash
gcloud run revisions list \
  --service=ink-api \
  --region=europe-west2
```

If a new deployment is unhealthy, traffic can be routed back to a previous healthy revision:

```bash
gcloud run services update-traffic ink-api \
  --region=europe-west2 \
  --to-revisions=REVISION_NAME=100
```

Replace `REVISION_NAME` with the previous healthy Cloud Run revision.

After rollback, verify the service again:

```bash
curl --fail --show-error \
  https://ink-api-850771094851.europe-west2.run.app/health
```

## Stage 6: Monitoring and Logging

Add structured logging, error tracking, request metrics, and database monitoring before treating the service as production-ready.