from fastapi import APIRouter
# from app.schemas.mcq import DistractorRequest, ValidateOptionsRequest

router = APIRouter()

@router.post("/generate-distractors")
async def generate_distractors():
    return {"distractors": ["A","B","C"]}

@router.post("/validate-options")
async def validate_options():
    return {"valid": True}
