from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, model_validator


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


class OptionLabel(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class QuestionReqPara(BaseModel):
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


class ComprehensionReqPara(QuestionReqPara):
    more_information: str | None = None

    # @model_validator(mode="after")
    # def validate_comprehension(self) -> "ComprehensionReqPara":
    #     if self.type == QuestionType.comprehension_based and not self.more_information:
    #         raise ValueError(
    #             "more_information is required when type == 'comprehension_based'"
    #         )
    #     return self


class ModelReqPara(BaseModel):
    generation_model: str | None = None
    validation_model: str | None = None
