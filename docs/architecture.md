# Architecture

## Approach

The initial architecture is a modular monolith. The application is deployed as one backend service while the codebase is organized into domain modules with clear responsibilities.

## Modules

- `auth`: user registration, login, password hashing, JWT creation, and authenticated user access.
- `dictionary`: external dictionary provider integration, shared word data, definitions, examples, synonyms, antonyms, and phonetics.
- `glossary`: saved user words and learning status.
- `reviews`: spaced repetition scheduling and review attempts.
- `tags`: user-defined tags and word-tag relationships.

## Why Not Microservices Initially

Microservices would add deployment, observability, networking, and data consistency complexity before the product needs it. A modular monolith allows the project to demonstrate clean boundaries while keeping development and testing efficient.

## Evolution Path

If the product grows, modules can become clearer service candidates. For example, dictionary provider integration or background review scheduling could later move into separate workers or services. That decision should be driven by operational need, not premature architecture.
