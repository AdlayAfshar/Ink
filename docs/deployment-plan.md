# Deployment Plan

## Stage 1: Local Development

Run the FastAPI app locally with a local PostgreSQL database. Keep configuration environment-based.

## Stage 2: Docker Compose

Add Docker and Docker Compose for repeatable local startup of the API and PostgreSQL.

## Stage 3: Managed PostgreSQL

Move database hosting to a managed PostgreSQL provider for staging or production.

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

Because the development machine uses Apple Silicon, the image must explicitly target `linux/amd64` for Cloud Run:

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

`DATABASE_URL` and `CORS_ALLOWED_ORIGINS` are temporary placeholders until the managed PostgreSQL database and frontend are deployed.

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