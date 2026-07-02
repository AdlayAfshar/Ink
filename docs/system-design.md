# System Design

## High-Level Components

The system begins as a FastAPI backend backed by PostgreSQL. The backend exposes REST endpoints for authentication, dictionary lookup, personal glossary management, tagging, and reviews.

## Backend API

The API owns request validation, authentication, business workflows, and persistence coordination. It is organized by domain modules to keep boundaries clear as the project grows.

## Database

PostgreSQL stores both shared dictionary data and user-specific learning data. These concerns are intentionally separated so dictionary definitions can be cached once while each user maintains their own notes, tags, saved words, and review progress.

## External Dictionary Provider

The first provider will be Free Dictionary API. Access should be wrapped behind a provider interface so the application is not tightly coupled to one external API shape.

## Future Frontend

A frontend can later consume the REST API for search, glossary management, reviews, and analytics. The backend should remain useful and testable without a frontend.

## Future Background Workers

Background workers may later handle scheduled review preparation, provider refreshes, email notifications, or analytics aggregation.

## Future Cache

Redis or another cache may be introduced to reduce repeated external dictionary lookups and improve response times for frequently searched words.

## Future AI Layer

AI-assisted explanations and example generation may be added later. This should be isolated behind service boundaries and must not replace the core dictionary and learning data model.
