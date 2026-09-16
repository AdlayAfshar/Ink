# 0005 Choose Deployment Platform

## Context

Ink needs a production deployment platform for its FastAPI container and PostgreSQL database.

Two cloud deployment paths were evaluated:

- GCP: Cloud Run + Cloud SQL
- AWS: ECS Express Mode + RDS PostgreSQL

The goal is to choose a practical first production deployment while still understanding the AWS alternative.

Because one of the project's main goals is to learn backend engineering
end to end, including cloud infrastructure and managed services, the
project intentionally evaluates major cloud providers rather than a more
streamlined PaaS such as Heroku.

A simpler PaaS could reduce deployment complexity, but it would expose
fewer of the infrastructure concepts that this project is intended to
practise.

## GCP Option

The GCP deployment would use:

- Cloud Run to run the FastAPI container
- Cloud SQL for PostgreSQL
- Artifact Registry for container images
- Secret Manager for secrets
- Cloud Logging for logs and monitoring

This path provides a relatively simple managed container deployment with less infrastructure to configure directly.

## AWS Option

The AWS deployment would use:

- ECS Express Mode to manage the container service
- Fargate to run containers
- ECR for container images
- RDS PostgreSQL for the database
- Secrets Manager or SSM Parameter Store for secrets
- CloudWatch for logs and monitoring
- IAM roles for service permissions

ECS Express Mode simplifies ECS deployment, but the AWS path still exposes more infrastructure concepts such as IAM, networking, load balancing, and Fargate.

## Comparison

| Area | GCP | AWS |
| --- | --- | --- |
| Container runtime | Cloud Run | ECS Express Mode + Fargate |
| PostgreSQL | Cloud SQL | RDS PostgreSQL |
| Container registry | Artifact Registry | ECR |
| Secrets | Secret Manager | Secrets Manager / SSM |
| Logging | Cloud Logging | CloudWatch |
| Permissions | IAM / Service Accounts | IAM Roles |
| Infrastructure complexity | Lower | Higher |
| Learning value | Managed deployment concepts | Broader infrastructure concepts |

## Cost and Complexity

Both platforms charge for the resources used by the application and database.

The AWS path can involve additional resources such as Fargate tasks, load balancing, networking, RDS, and CloudWatch. This creates more infrastructure to understand, configure, monitor, and potentially pay for.

The GCP path keeps the first deployment smaller and reduces the amount of infrastructure that needs to be managed directly.

## Decision

Use GCP Cloud Run and Cloud SQL for the first production deployment of Ink.

Keep AWS ECS Express Mode and RDS PostgreSQL as a future deployment exercise rather than introducing a second production deployment path now.

## Consequences

Ink can continue toward its first production deployment without maintaining two cloud environments.

The project still documents the AWS alternative and its tradeoffs.

A future AWS deployment can be used to practise ECS, Fargate, RDS, IAM, networking, load balancing, CloudWatch, and AWS deployment workflows.