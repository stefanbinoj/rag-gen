from beanie import Document
from datetime import datetime
from pydantic import Field
from app.prompts.generation_prompt import generation_system_prompt
from app.prompts.validation_prompt import validation_system_prompt
from app.prompts.regeneration_prompt import regeneration_system_prompt


class Model(Document):
    generation_model: str = "openai/gpt-5-mini"
    validation_model: str = "google/gemini-2.5-flash"
    regeneration_model: str = "openai/gpt-5-mini"
    updated_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "models"  # collection name


class Prompt(Document):
    generation_prompt: str = generation_system_prompt()
    validation_prompt: str = validation_system_prompt()
    regeneration_prompt: str = regeneration_system_prompt()
    updated_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "prompts"
