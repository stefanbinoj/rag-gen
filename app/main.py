from fastapi import FastAPI
from beanie import init_beanie
from app.routers import history, questions, validator, admin, health
from app.schemas.mongo_models import Model, Prompt, GenerationLog, ComprehensionLog, FillInTheBlankLog, SubjectiveLog
from config import load_environment_variables
from app.deps import get_mongo_db


def create_app() -> FastAPI:
    app = FastAPI(title="Question Generator", version="1.0.0")
    load_environment_variables()

    @app.on_event("startup")
    async def startup_event():
        db = get_mongo_db()
        await init_beanie(database=db, document_models=[Model, Prompt, GenerationLog, ComprehensionLog,FillInTheBlankLog , SubjectiveLog])  # pyright: ignore[reportArgumentType]

        # Initialize default models if none exist
        if not await Model.find_one():
            await Model().insert()
            print("Default models configuration initialized.")

        # Initialize default prompts
        if not await Prompt.find_one():
            await Prompt().insert()
            print("Default prompts initialized.")

    app.include_router(questions.router, prefix="/api/v1/questions", tags=["questions"])
    app.include_router(
        validator.router, prefix="/api/v1/validators", tags=["validators"]
    )
    app.include_router(history.router, prefix="/api/v1/history", tags=["history"])
    app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
    app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
    return app


app = create_app()
