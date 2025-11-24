from fastapi import APIRouter
# from app.schemas.mcq import DistractorRequest, ValidateOptionsRequest

router = APIRouter()

@router.post("/generate-distractors")
async def generate_distractors(req):
    print("Received request:", req)
    return {"distractors": ["A","B","C"]}

@router.post("/validate-options")
async def validate_options(req):
    print("Received request:", req)
    # validation logic
    return {"valid": True}
