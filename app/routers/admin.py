from fastapi import APIRouter
from starlette.responses import JSONResponse
from app.schemas.models import Model
from app.schemas.req import ModelReqPara

router = APIRouter()


@router.get("/metrics")
async def admin_metrics():
    return {"status": "to be implemented with langfuse"}


@router.get("/models")
async def list_models():
    models = await Model.find_one()
    return JSONResponse(
        content={
            "success": True,
            "models": models.model_dump(mode="json") if models else None,
        },
        status_code=200,
    )


@router.post("/models/switch")
async def switch_model(req: ModelReqPara):
    models = await Model.find_one()
    if not models:
        # Use exclude_none=True so that if fields are missing, the Model defaults are used
        new_model = Model(**req.model_dump(exclude_none=True))
        await new_model.insert()
        return JSONResponse(
            content={"success": True, "model": new_model.model_dump(mode="json")},
            status_code=201,
        )

    if req.generation_model:
        models.generation_model = req.generation_model
    if req.validation_model:
        models.validation_model = req.validation_model

    from datetime import datetime

    models.updated_at = datetime.now()

    await models.save()
    return JSONResponse(
        content={"success": True, "model": models.model_dump(mode="json")},
        status_code=200,
    )
