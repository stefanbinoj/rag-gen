from beanie import Document
from datetime import datetime
from pydantic import Field
from app.prompts.generation_prompt import generation_system_prompt
from app.prompts.validation_prompt import validation_system_prompt
from app.prompts.regeneration_prompt import regeneration_system_prompt
from typing import List, Optional
from app.schemas.input_schema import QuestionReqPara
from app.schemas.output_schema import Options
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
    chroma_id: str
    question: str
    options: Options
    correct_option: str
    explanation: str
    validation_score: float
    duplication_chance: float
    total_time: float
    total_attempts: int
    issues: List[str]
    similar_questions: Optional[str] = None




class GenerationLog(Document):
    request: QuestionReqPara
    questions: List[QuestionLog]
    total_questions: int
    total_questions_generated: int
    total_regeneration_attempts: int
    total_retries: int
    total_time: float
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "generation_logs"
