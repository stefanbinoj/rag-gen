from fastapi import APIRouter, HTTPException
from app.schemas.res import BaseResponse, ComprehensionResponse
from app.schemas.req import QuestionReqPara, ComprehensionReqPara

from app.services.generation_node import generate_questions
from app.services.validation_node import validate_questions
from app.services.chroma_node import search_similar_questions

router = APIRouter()


@router.post(
    "/generate-questions",
    response_model=list[ComprehensionResponse],
    responses={
        201: {"description": "Questions generated successfully"},
        422: {"description": "Invalid input"},
    },
)
async def generate_questions_endpoint(req: QuestionReqPara):
    generated_questions = await generate_questions(req)
    print(f"\nGenerated {len(generated_questions)} questions")

    validated_results = []
    for idx, question in enumerate(generated_questions):
        print(f"Validating question {idx + 1}")

        similar_questions = await search_similar_questions(
            question=question, subject=req.subject, topic=req.topic, top_k=3
        )
        print(f"  Found {len(similar_questions)} similar questions in database")
        print("  Similar Questions:", similar_questions)

        validation_result = await validate_questions(req, question, similar_questions)
        validated_results.append(
            {"req": req, "question": question, "validation": validation_result}
        )

    print(f"Validation completed for all {len(validated_results)} questions")

    for idx, result in enumerate(validated_results):
        print(f"\nQuestion {idx + 1} validation score: {result['validation'].score}/10")

    return []  # Placeholder return


@router.post("/passive_paragraph", response_model=BaseResponse)
async def passive(req: ComprehensionReqPara):
    print("Received request:", req)
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
