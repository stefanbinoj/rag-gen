
from app.schemas.models import Model



async def get_model_name(type: str):
    models = await Model.find_one()

    if not models:
        raise ValueError("No model configuration found in the database.")

    if type == "generation":
        return models.generation_model
    else:
        return models.validation_model
