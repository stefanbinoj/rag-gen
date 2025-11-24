from pydantic import BaseModel

class GenerateRequest(BaseModel):
    prompt: str
    count: int = 1
    difficulty: str | None = None


class QuestionOut(BaseModel):
    id: int
    question: str
    options: list[str] | None = None


class PromptConfigIn(BaseModel):
    model: str
    temperature: float


class PromptConfigOut(PromptConfigIn):
    updated_at: str

