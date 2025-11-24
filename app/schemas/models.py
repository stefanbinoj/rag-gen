from beanie import Document
from datetime import datetime
from pydantic import Field

class Model(Document):
    generation_model: str = "gpt-3.5-turbo"
    validation_model: str = "gpt-4"
    updated_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "models"     # collection name

