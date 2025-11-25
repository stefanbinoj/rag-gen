from beanie import Document
from datetime import datetime
from pydantic import Field

class Model(Document):
    generation_model: str = "openai/gpt-5-mini"
    validation_model: str = "google/gemini-2.5-flash"
    updated_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "models"     # collection name

