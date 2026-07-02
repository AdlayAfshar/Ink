# 0001 Use FastAPI

## Context

The project needs a Python backend framework that supports REST APIs, validation, dependency injection, documentation, and testing.

## Decision

Use FastAPI as the backend web framework.

## Consequences

FastAPI provides strong developer ergonomics, automatic OpenAPI documentation, and good support for typed request and response models. The project should still define clear module boundaries so framework convenience does not leak into every layer.
