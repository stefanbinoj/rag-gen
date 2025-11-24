from fastapi import FastAPI
from app.routers.v1 import questions, mcq, validator, admin, health

def create_app():
    app = FastAPI(title="Question Generator")
    api_v1 = "/api/v1"
    app.include_router(questions.router, prefix=f"{api_v1}/questions", tags=["questions"])
    # include other routers...
    return app

app = create_app()

