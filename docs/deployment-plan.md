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

The instance runs PostgreSQL 16 in the same region as the Cloud Run services:

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

Cloud Run exposes this secret to the backend as:

```text
DATABASE_URL
```

The backend Cloud Run service is configured with the Cloud SQL connection:

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

Both the frontend and backend are deployed to Google Cloud Run. Cloud SQL provides managed PostgreSQL, Artifact Registry stores container images, Secret Manager stores backend secrets, Cloud Logging provides application logs, and IAM service accounts control access to Google Cloud resources.

AWS ECS Express Mode with RDS PostgreSQL has been evaluated as an alternative deployment path and is reserved for a future learning exercise.

Render and Fly.io were also evaluated as simpler deployment alternatives, but GCP was selected because it provides a better balance between infrastructure learning and deployment complexity for Ink.

See `architecture-decisions/0005-choose-deployment-platform.md` for the full platform comparison and decision.

### Google Cloud Environment

Google Cloud project:

```text
ink-backend-adlay
```

Region:

```text
europe-west2
```

Required Google Cloud APIs include:

```text
Cloud Run
Artifact Registry
Cloud Build
Secret Manager
Cloud SQL
```

A Docker repository named `ink` is used in Artifact Registry:

```text
europe-west2-docker.pkg.dev/ink-backend-adlay/ink
```

Because deployment images target `linux/amd64`, images built from an Apple Silicon development machine explicitly use that platform to avoid architecture incompatibilities.

### Backend Deployment

The FastAPI backend runs as the Cloud Run service:

```text
ink-api
```

The deployed backend is available at:

```text
https://ink-api-850771094851.europe-west2.run.app
```

Backend container images are stored at:

```text
europe-west2-docker.pkg.dev/ink-backend-adlay/ink/ink-api
```

The production JWT secret is stored in Secret Manager as:

```text
ink-jwt-secret
```

The production database URL is stored as:

```text
ink-database-url
```

The Merriam-Webster API key used by the fallback dictionary provider is stored as:

```text
ink-merriam-webster-api-key
```

These secrets are exposed to the backend service as:

```text
JWT_SECRET_KEY
DATABASE_URL
MERRIAM_WEBSTER_API_KEY
```

The backend Cloud Run service account has the required Secret Manager and Cloud SQL permissions.

The production backend is configured with:

```text
ENVIRONMENT=production
DEBUG=false
CORS_ALLOWED_ORIGINS=https://ink-frontend-850771094851.europe-west2.run.app
```

The public health endpoint can be verified with:

```bash
curl --fail --show-error \
  https://ink-api-850771094851.europe-west2.run.app/health
```

Expected response:

```json
{"status":"ok"}
```

Cloud Run logs can be checked with:

```bash
gcloud run services logs read ink-api \
  --region=europe-west2 \
  --limit=30
```

### Frontend Deployment

The React/Vite frontend runs as a separate Cloud Run service:

```text
ink-frontend
```

The public frontend is available at:

```text
https://ink-frontend-850771094851.europe-west2.run.app
```

The frontend uses a multi-stage Docker build.

The build stage uses Node.js to install dependencies and create the Vite production bundle. The runtime stage uses Nginx to serve the generated static files on port `8080`, which is compatible with Cloud Run.

The frontend image is built with the production backend URL:

```bash
docker build \
  --platform linux/amd64 \
  --build-arg VITE_API_BASE_URL=https://ink-api-850771094851.europe-west2.run.app \
  -t ink-frontend:test \
  ./frontend
```

`VITE_API_BASE_URL` is a build-time variable because Vite embeds exposed environment variables into the generated frontend bundle.

After local verification, the image can be tagged for Artifact Registry:

```bash
docker tag ink-frontend:test \
  europe-west2-docker.pkg.dev/ink-backend-adlay/ink/ink-frontend:latest
```

The image is pushed with:

```bash
docker push \
  europe-west2-docker.pkg.dev/ink-backend-adlay/ink/ink-frontend:latest
```

The frontend is deployed to Cloud Run with:

```bash
gcloud run deploy ink-frontend \
  --image=europe-west2-docker.pkg.dev/ink-backend-adlay/ink/ink-frontend:latest \
  --region=europe-west2 \
  --platform=managed \
  --allow-unauthenticated \
  --port=8080
```

The frontend does not contain backend credentials or other production secrets.

### Production CORS

The backend accepts browser requests from the production frontend origin:

```text
https://ink-frontend-850771094851.europe-west2.run.app
```

The production configuration is:

```text
CORS_ALLOWED_ORIGINS=https://ink-frontend-850771094851.europe-west2.run.app
```

Local frontend origins are not included in the production CORS configuration.

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

Backend secrets are provided through Google Secret Manager rather than stored in container images or committed configuration files.

### Deployment Verification

The production frontend and backend integration has been manually verified.

Verification includes:

1. Opening the public `ink-frontend` Cloud Run service.
2. Searching for a dictionary word.
3. Confirming the browser sends the request to the production `ink-api` service.
4. Receiving a successful response from the backend.
5. Confirming the backend allows the production frontend origin through CORS.
6. Confirming the dictionary result renders correctly in the frontend.

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

Each automated backend deployment uses the Git commit SHA as the image tag so deployed backend images can be traced back to their source commits.

Frontend deployment is currently manual.

### Deployment Verification

After backend deployment, the workflow checks the public health endpoint.

The equivalent manual check is:

```bash
curl --fail --show-error \
  https://ink-api-850771094851.europe-west2.run.app/health
```

If the health check fails, the deployment workflow is marked as failed.

### Rollback

Cloud Run keeps previous revisions of the deployed service.

Available backend revisions can be listed with:

```bash
gcloud run revisions list \
  --service=ink-api \
  --region=europe-west2
```

If a new backend deployment is unhealthy, traffic can be routed back to a previous healthy revision:

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

The backend currently has basic production logging integrated with Cloud Run logs.

Future production-readiness work can add structured logging, error tracking, request metrics, alerting, and database monitoring.