from fastapi import APIRouter, HTTPException
from app.schemas.res import BaseResponse, ComprehensionResponse
from app.schemas.req import QuestionReqPara, ComprehensionReqPara
from app.services.generation_node import generate_questions
from app.deps import get_llm_client
from app.prompts.generation_prompt import system_prompt

router = APIRouter()


@router.post(
    "/generate-questions",
    response_model=list[ComprehensionResponse],
    responses={
        201: {"description": "Questions generated successfully"},
        400: {"description": "Invalid input"},
        502: {
            "description": "LLM provider error",
            "content": {
                "application/json": {"example": {"detail": "provider timeout"}}
            },
        },
    },
)
async def generate_questions_endpoint(req: QuestionReqPara):
    """
    Generate questions using an LLM.

    This endpoint accepts a `prompt` and returns an array of generated
    question objects. Each item contains `id` and `question` fields.

    - **prompt**: the natural-language prompt for the LLM
    - **count**: the number of questions to generate (default 1)
    """
    print("Received request:", req)

    llm_chain = LLMChain(prompt=system_prompt, llm=get_llm_client("gpt-4"))
    question = "What NFL team won the Super Bowl in the year Justin Beiber was born?"
    print(llm_chain.run(question))


@router.post("/passive_paragraph", response_model=BaseResponse)
async def passive(req: ComprehensionReqPara):
    print("Received request:", req)
    await generate_questions()
    return {"success": True}


@router.get("/questions/{id}")
async def read_question(id: int):
    print("Fetching question with ID:", id)
    q = {}  # fetch from DB or cache
    if not q:
        raise HTTPException(status_code=404, detail="not found")


@router.get("/prompt-config")
async def get_prompt_config():
    return {"model": "gpt-4", "temperature": 0.2}


@router.post("/prompt-config")
async def set_prompt_config(cfg):
    # persist config
    return cfg
