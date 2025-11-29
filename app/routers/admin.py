from datetime import datetime
from fastapi import APIRouter
from starlette.responses import JSONResponse
from app.schemas.mongo_models import Model, Prompt
from app.schemas.input_schema import ModelReqPara, PromptReqPara

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

    models.updated_at = datetime.now()

    await models.save()
    return JSONResponse(
        content={"success": True, "model": models.model_dump(mode="json")},
        status_code=200,
    )


@router.get("/prompts")
async def list_prompts():
    prompts = await Prompt.find_one()
    return JSONResponse(
        content={
            "success": True,
            "prompts": prompts.model_dump(mode="json") if prompts else None,
        },
        status_code=200,
    )


@router.post("/prompts/update")
async def update_prompt(req: PromptReqPara):
    prompts = await Prompt.find_one()
    if not prompts:
        return JSONResponse(
            content={"success": False, "message": "NO Prompt with not found."},
            status_code=404,
        ) 

    if req.generation_prompt:
        prompts.generation_prompt = req.generation_prompt
    if req.regeneration_prompt:
        prompts.regeneration_prompt = req.regeneration_prompt
    if req.validation_prompt:
        prompts.validation_prompt = req.validation_prompt

    prompts.updated_at = datetime.now()
    await prompts.save()

    return JSONResponse(
        content={"success": True, "prompt": prompts.model_dump(mode="json")},
        status_code=200,
    )

