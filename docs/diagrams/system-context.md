# System Context

```mermaid
flowchart LR
    User[User] --> Frontend[Future Frontend]
    User --> API[FastAPI Backend]
    Frontend --> API
    API --> DB[(PostgreSQL)]
    API --> Provider[Dictionary Provider]
    API -. future .-> Cache[(Redis Cache)]
    API -. future .-> Worker[Background Worker]
    API -. future .-> AI[AI Assistance Layer]
```
