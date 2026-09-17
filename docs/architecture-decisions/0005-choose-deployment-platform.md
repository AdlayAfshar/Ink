# 0005 Choose Deployment Platform

## Context

Ink needs a production deployment platform for its FastAPI container and
PostgreSQL database.

The project is also intended to practise realistic backend and cloud
engineering concepts, including:

- container deployment
- managed PostgreSQL
- secrets management
- identity and access management
- logging and observability
- CI/CD
- deployment rollback
- cost awareness

The goal is therefore not simply to choose the easiest platform. The chosen
platform should provide useful cloud engineering experience without adding
unnecessary infrastructure complexity to the first production deployment.

Four deployment options were considered:

- Google Cloud Run + Cloud SQL
- AWS ECS Express Mode + RDS PostgreSQL
- Render Web Service + Render Postgres
- Fly.io Machines + Managed Postgres

## Options Considered

### Google Cloud Run + Cloud SQL

The GCP deployment would use:

- Cloud Run to run the FastAPI container
- Cloud SQL for PostgreSQL
- Artifact Registry for container images
- Secret Manager for secrets
- Cloud Logging for logs and monitoring
- IAM and service accounts for permissions

Cloud Run provides a managed container runtime with automatic scaling and
relatively little infrastructure to configure directly.

This option still exposes important cloud concepts such as container
registries, managed databases, IAM, secrets, logging, revisions, and
deployment automation.

It therefore provides a useful balance between learning value and operational
complexity.

### AWS ECS Express Mode + RDS PostgreSQL

The AWS deployment would use:

- ECS Express Mode to manage the container service
- Fargate to run containers
- ECR for container images
- RDS PostgreSQL for the database
- Secrets Manager or SSM Parameter Store for secrets
- CloudWatch for logs and monitoring
- IAM roles for service permissions

ECS Express Mode reduces the amount of ECS configuration required and
automatically configures supporting infrastructure.

However, the AWS path still exposes more infrastructure concepts and AWS
services, including Fargate, IAM roles, networking, load balancing, RDS,
CloudWatch, and deployment configuration.

This provides strong learning value but introduces more moving parts for the
first production deployment.

### Render Web Service + Render Postgres

The Render deployment would use:

- Render Web Service to run the FastAPI application
- Render Postgres for PostgreSQL
- environment variables and secrets managed through Render
- integrated logs and deployment history
- Git-based automatic deployments

Render provides the simplest deployment path of the options considered.

It reduces the amount of infrastructure that must be configured directly and
makes it possible to deploy a FastAPI application and PostgreSQL database
quickly.

This is useful for learning application deployment, but it exposes fewer
general cloud infrastructure concepts than GCP or AWS.

### Fly.io Machines + Managed Postgres

The Fly.io deployment would use:

- Fly Machines to run the application container
- Fly.io Managed Postgres or an external PostgreSQL provider
- Fly secrets for application secrets
- Fly networking and deployment tooling
- Fly logs and monitoring

Fly.io provides more infrastructure visibility than a traditional PaaS while
remaining simpler than configuring a larger cloud provider.

It provides useful experience with Docker images, Machines, networking,
regions, scaling, and deployment configuration.

However, its concepts and tooling are more platform-specific and provide less
direct experience with the cloud services commonly encountered in GCP or AWS
environments.

## Comparison

| Area | GCP | AWS | Render | Fly.io |
| --- | --- | --- | --- | --- |
| Container runtime | Cloud Run | ECS Express Mode + Fargate | Web Service | Machines |
| PostgreSQL | Cloud SQL | RDS PostgreSQL | Render Postgres | Managed or external Postgres |
| Container registry | Artifact Registry | ECR | Platform-managed | Fly registry |
| Secrets | Secret Manager | Secrets Manager / SSM | Render secrets | Fly secrets |
| Logging | Cloud Logging | CloudWatch | Integrated logs | Fly logs |
| Permissions | IAM / Service Accounts | IAM Roles | Platform permissions | Platform permissions |
| CI/CD integration | Strong | Strong | Simple Git integration | CLI / CI integration |
| Infrastructure complexity | Medium | High | Low | Medium |
| Cost risk | Medium | Higher | Lower | Medium |
| Learning value | High | Very high | Moderate | Moderate to high |
| Portfolio signal | Strong cloud experience | Strong cloud experience | Application deployment | Container deployment |
| Rollback story | Cloud Run revisions | ECS deployments | Previous deploys | Machine releases/deployments |

## Cost and Complexity

All four platforms introduce some ongoing cost once production resources are
running, especially PostgreSQL.

AWS can involve several separately billed resources such as Fargate, RDS,
load balancing, CloudWatch, networking, and data transfer. This creates more
resources to understand and monitor.

GCP also separates compute, database, registry, logging, and networking costs,
but Cloud Run keeps the application runtime relatively small and can scale
down when it is not receiving traffic.

Render reduces infrastructure configuration and makes costs easier to reason
about, but this simplicity also removes some of the infrastructure learning
that the project is intended to provide.

Fly.io provides relatively direct control over Machines and application
resources, but requires understanding Fly-specific deployment, networking,
and scaling concepts.

Exact prices can change and should be checked before production resources are
created.

## Decision

Use Google Cloud Run and Cloud SQL for the first production deployment of Ink.

GCP provides the best balance for the current stage of the project. It exposes
real cloud concepts such as container registries, managed PostgreSQL, IAM,
secrets, logging, revisions, and CI/CD while keeping the first deployment
smaller than the equivalent AWS architecture.

AWS ECS Express Mode and RDS PostgreSQL will remain a future deployment
exercise. After the GCP deployment is working, the same application can be
deployed to AWS to compare the two architectures directly.

Render and Fly.io will not be used for the first deployment. Both are viable
deployment platforms, but they provide less direct value for the project's
current goal of learning major cloud-provider infrastructure.

## Consequences

Ink will maintain one production deployment path initially rather than
multiple cloud environments.

The first deployment will provide practical experience with:

- building and publishing container images
- deploying containers to Cloud Run
- connecting Cloud Run to Cloud SQL
- managing production secrets
- configuring IAM and service accounts
- inspecting application logs
- building a CI/CD deployment workflow
- deploying new revisions
- rolling back a failed deployment
- monitoring cloud resource costs

The project accepts some additional complexity compared with using Render in
exchange for greater exposure to cloud infrastructure concepts.

AWS remains intentionally deferred rather than rejected. A future AWS
deployment can be used to practise ECS, Fargate, ECR, RDS, IAM, networking,
load balancing, CloudWatch, and AWS deployment workflows.

This decision should be revisited if Ink develops requirements that Cloud Run
does not handle well, if AWS-specific experience becomes a project priority,
or if production cost and operational requirements change significantly.