from fastapi import FastAPI

app = FastAPI(
    title="Personal Glossary API",
    description="Backend API for a personal glossary and vocabulary learning platform.",
    version="0.1.0",
)


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "name": "Personal Glossary API",
        "status": "foundation phase",
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
