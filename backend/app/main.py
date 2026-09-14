from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.modules.auth.router import router as auth_router
from backend.app.modules.dictionary.router import router as dictionary_router

app = FastAPI(
    title=settings.app_name,
    description="Backend API for a personal glossary and vocabulary learning platform.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(dictionary_router)

@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "name": "Personal Glossary API",
        "status": "foundation phase",
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
