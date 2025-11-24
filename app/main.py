from fastapi import FastAPI
from app.routers import questions, validator, admin, health, mcq
from config import load_environment_variables

def create_app() -> FastAPI:
    app = FastAPI(title="Question Generator", version="1.0.0")
    load_environment_variables()

    app.include_router(questions.router, prefix="/api/v1/questions", tags=["questions"])
    app.include_router(mcq.router, prefix="/api/v1/mcq", tags=["mcq"])
    app.include_router(validator.router, prefix="/api/v1/validators", tags=["validators"])
    app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
    app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
    return app


app = create_app()
