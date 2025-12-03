from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator 


class QuestionType(str, Enum):
    mcq = "mcq"
    fill_in_the_blank = "fill_in_the_blank"
    subjective = "subjective"

class Difficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"

class Stream(str, Enum):
    _11Plus = "11Plus"
    GCSE = "GCSE"
    CBSE = "CBSE"
    ICSE = "ICSE"

class QuestionReqPara(BaseModel):
    type: QuestionType
    subject: str
    topic: str
    sub_topic: Optional[str] = None
    difficulty: Difficulty
    stream: Stream
    country: str = "UK"
    age: Optional[str] = None
    no_of_questions: int = Field(..., gt=0, le=25)
    language: str = "English"

    @field_validator("subject", "topic", "sub_topic", mode="before")
    @classmethod
    def sanitize_strings(cls, v):
        if isinstance(v, str):
            return v.strip().lower().rstrip(".").replace(" ", "_")
        return v


class ComprehensionReqPara(QuestionReqPara):
    generate_comprehension: bool
    more_information: Optional[str] = None
    comprehensive_paragraph: Optional[str] = None
    type: Optional[QuestionType] = Field(default=None, exclude=True)

    @model_validator(mode="after")
    def check_comprehension_requirements(self):
        if self.generate_comprehension is False and not self.comprehensive_paragraph:
            raise ValueError(
                "comprehensive_paragraph is required when generate_comprehension is False"
            )
        return self


class ModelReqPara(BaseModel):
    generation_model: Optional[str] = None
    validation_model: Optional[str] = None


class PromptReqPara(BaseModel):
    generation_prompt: Optional[str] = None
    regeneration_prompt: Optional[str] = None
    validation_prompt: Optional[str] = None
    comprehensive_generation_prompt: Optional[str] = None
    comprehensive_question_generation_prompt: Optional[str] = None
    comprehensive_question_validation_prompt: Optional[str] = None
    comprehensive_question_regeneration_prompt: Optional[str] = None


class GraphType(str, Enum):
    mcq = "mcq"
    fill_in_the_blank = "fill_in_the_blank"
    comprehension = "comprehension"
