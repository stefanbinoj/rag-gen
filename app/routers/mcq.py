from fastapi import APIRouter

router = APIRouter()

@router.post("/generate-distractors")
async def generate_distractors():
    return {"distractors": ["A","B","C"]}

@router.post("/validate-options")
async def validate_options(question_id: str):
    return {"valid": True}
