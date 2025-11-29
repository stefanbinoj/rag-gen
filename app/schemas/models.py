from beanie import Document
from datetime import datetime
from pydantic import Field
from app.prompts.generation_prompt import generation_system_prompt
from app.prompts.validation_prompt import validation_system_prompt
from app.prompts.regeneration_prompt import regeneration_system_prompt
from typing import List, Optional
from app.schemas.req import QuestionReqPara
from app.schemas.res import Options
from pydantic import BaseModel


class Model(Document):
    generation_model: str = "openai/gpt-5.1-chat"
    validation_model: str = "openai/gpt-oss-120b"
    regeneration_model: str = "openai/gpt-5.1-chat"
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


class QuestionLog(BaseModel):
    _id: Optional[str] = None
    question: str
    options: Options
    correct_option: str
    explanation: str
    validation_score: float
    duplication_chance: float
    issues: List[str]
    retries: int
    chroma_id: Optional[str] = None
    total_time: Optional[float] = None
    similar_questions: Optional[str] = None




class GenerationLog(Document):
    request: QuestionReqPara
    questions: List[QuestionLog]
    created_at: datetime = Field(default_factory=datetime.now)
    total_questions: int

    class Settings:
        name = "generation_logs"
