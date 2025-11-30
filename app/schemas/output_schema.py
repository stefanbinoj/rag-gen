from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional


class OptionLabel(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class ComprehensionType(str, Enum):
    direct_retrieval = "direct_retrieval"
    inference_questions = "inference_questions"
    vocabulary_meaning = "vocabulary_meaning"
    summary = "summary"
    author_intent = "author_intent"
    character_analysis = "character_analysis"
    evidence_based_reasoning = "evidence_based_reasoning"


class Options(BaseModel):
    A: str
    B: str
    C: str
    D: str


class QuestionItem(BaseModel):
    """Contains information about a single question item."""

    question: str = Field(..., description="The question text")
    options: Options = Field(..., description="The options for the question")
    correct_option: OptionLabel = Field(
        ..., description="The label of the correct option"
    )
    explanation: str = Field(..., description="Explanation for the correct answer")


class ComprehensionQuestionItem(QuestionItem):
    """Extends QuestionItem to include comprehension type."""

    comprehension_type: ComprehensionType = Field(
        ..., description="The type of comprehension question"
    )


class ValidationResult(BaseModel):
    """Contains validation results for a single question."""

    score: float = Field(..., ge=0, le=1, description="Validation score from 0 to 1")
    duplication_chance: float = Field(
        ..., ge=0, le=1, description="Chance of duplication from 0 to 1"
    )
    issues: list[str] = Field(
        default_factory=list, description="List of identified issues"
    )


class ValidationNodeReturn(BaseModel):
    validation_result: ValidationResult = Field(
        ..., description="Results from the validation process"
    )
    added_to_vectordb: bool = Field(
        ..., description="Indicates if the question was added to the vector database"
    )
    similar_section: str = Field(
        ..., description="Details about similar questions found during validation"
    )
    uuid: Optional[str] = Field(
        default=None, description="The UUID of the question if added to DB"
    )
