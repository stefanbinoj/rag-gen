from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from app.schemas.questions import GenerateRequest, QuestionOut, PromptConfigIn, PromptConfigOut
from app.services.questions import generate_questions
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
async def generate_questions_endpoint(req: GenerateRequest):
    """
    Generate questions using an LLM.

    This endpoint accepts a `prompt` and returns an array of generated
    question objects. Each item contains `id` and `question` fields.

    - **prompt**: the natural-language prompt for the LLM
    - **count**: the number of questions to generate (default 1)
    """
    print("Received request:", req)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=[
        {"id": 1, "question": "What is the capital of France?"},
        {"id": 2, "question": "Who wrote 'To Kill a Mockingbird'?"}
    ])


@router.post("/passive_paragraph", response_model=QuestionOut)
async def passive(req: GenerateRequest):
    print("Received request:", req)
    await generate_questions()
    return { "success" : True }

@router.get("/questions/{id}", response_model=QuestionOut)
async def read_question(id: int):
    print("Fetching question with ID:", id)
    q = {}  # fetch from DB or cache
    if not q:
        raise HTTPException(status_code=404, detail="not found")

@router.get("/prompt-config", response_model=PromptConfigOut)
async def get_prompt_config():
    return {"model": "gpt-4", "temperature": 0.2}

@router.post("/prompt-config", response_model=PromptConfigOut)
async def set_prompt_config(cfg: PromptConfigIn):
    # persist config
    return cfg
