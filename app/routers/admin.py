from fastapi import APIRouter

router = APIRouter()

@router.get("/metrics")
async def admin_metrics():
    return {"requests": 1234}

@router.get("/models")
async def list_models():
    return [{"name": "gpt-4", "active": True}]

@router.post("/models/switch")
async def switch_model(model_name: str):
    # switch logic
    return {"switched_to": model_name}

