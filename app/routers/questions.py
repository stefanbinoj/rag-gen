from fastapi import APIRouter, Depends
from app.schemas.questions import GenerateRequest, QuestionOut
from app.services.questions import generate_questions
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post(
    "/generate-questions",
    response_model=list[QuestionOut],
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Questions generated successfully"},
        400: {"description": "Invalid input"},
        502: {"description": "LLM provider error", "content": {"application/json": {"example": {"detail": "provider timeout"}}}}
    },
    tags=["questions"],
)
async def generate_questions_endpoint(req: GenerateReq):
    """
    Generate questions using an LLM.

    This endpoint accepts a `prompt` and returns an array of generated
    question objects. Each item contains `id` and `question` fields.

    - **prompt**: the natural-language prompt for the LLM
    - **count**: the number of questions to generate (default 1)
    """
    try:
        # call LLM...
        pass
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SomeLLMProviderError:
        # return a 502 with custom JSON
        return JSONResponse({"detail": "LLM provider failed"}, status_code=502)

