# 0002 Use PostgreSQL

## Context

The application needs reliable relational modelling for users, words, definitions, tags, reviews, and review attempts.

## Decision

Use PostgreSQL as the primary database.

## Consequences

PostgreSQL supports relational integrity, indexes, transactions, and production-grade deployment options. Local development will require database setup, and schema changes should be managed through Alembic migrations.
