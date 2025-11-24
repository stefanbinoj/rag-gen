from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, model_validator
from datetime import datetime


class QuestionType(str, Enum):
    mcq = "mcq"
    fill_in_the_blank = "fill_in_the_blank"
    short_answer = "short_answer"
    long_form = "long_form"
    comprehension_based = "comprehension_based"


class Difficulty(str, Enum):
    easy = "easy"
    med = "med"
    hard = "hard"


class Stream(str, Enum):
    _11Plus = "11Plus"
    GCSE = "GCSE"
    CBSE = "CBSE"
    ICSE = "ICSE"


class Country(str, Enum):
    UK = "UK"
    INDIA = "INDIA"
    US = "US"


class Language(str, Enum):
    eng = "eng"


class ComprehensionBasedType(str, Enum):
    direct_retrieval = "direct_retrieval"
    inference_questions = "inference_questions"
    vocabulary_meaning = "vocabulary_meaning"
    summary = "summary"
    author_intent = "author_intent"
    character_analysis = "character_analysis"
    evidence_based_reasoning = "evidence_based_reasoning"


class OptionLabel(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class GenerateRequest(BaseModel):
    type: QuestionType
    subject: str
    topic: str
    difficulty: Difficulty
    stream: Stream
    country: Country
    age: str = Field(..., description='e.g. "10-11" or "14-16"')
    no_of_questions: int = Field(..., gt=0)
    sub_topic: str | None = None
    language: Language = Language.eng

    # comprehension-specific fields (optional unless type == comprehension_based)
    more_information: str | None = None
    distribution: bool | None = False
    require_vocabulary_question: bool | None = False

    @model_validator(mode="after")
    def validate_comprehension(self) -> "GenerateRequest":
        if self.type == QuestionType.comprehension_based and not self.more_information:
            raise ValueError(
                "more_information is required when type == 'comprehension_based'"
            )
        return self


class Metadata(BaseModel):
    _id: str = Field(..., alias="_id", description="MongoDB ObjectId as string")
    created_at: datetime
    question_score: int = Field(..., description="Equals number of questions generated")
    generation_attempts: int
    generation_time: float = Field(..., description="Seconds taken to generate")
    tokens_used: int
    cost: float


class QuestionItem(BaseModel):
    question: str
    options: dict[OptionLabel , str]
    correct_option: OptionLabel
    explanation: str | None = None


class BaseResponse(BaseModel):
    no_of_questions: int
    questions: list[QuestionItem]
    metadata: Metadata


class ComprehensionResponse(BaseResponse):
    passage_title: str
    passage_text: str
    question_type: ComprehensionBasedType

    # (BaseResponse model_validator still applies)


# Example usage note:
# if req.type == QuestionType.comprehension_based:
#     resp = ComprehensionResponse(...)
# else:
#     resp = BaseResponse(...)
