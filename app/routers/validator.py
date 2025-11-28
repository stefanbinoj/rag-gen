from fastapi import APIRouter
# from app.schemas.validator import ValidateQuestionRequest, ValidatePassageRequest

router = APIRouter()

@router.post("/validate-question")
async def validate_question(req):
    print("Received request:", req)
    return {"valid": True}

@router.post("/validate-passage")
async def validate_passage(req):
    print("Received request:", req)
    return {"valid": True}


