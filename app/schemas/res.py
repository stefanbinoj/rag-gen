from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class OptionLabel(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"

class ComprehensionBasedType(str, Enum):
    direct_retrieval = "direct_retrieval"
    inference_questions = "inference_questions"
    vocabulary_meaning = "vocabulary_meaning"
    summary = "summary"
    author_intent = "author_intent"
    character_analysis = "character_analysis"
    evidence_based_reasoning = "evidence_based_reasoning"


class Metadata(BaseModel):
    id: str = Field(..., alias="_id", description="MongoDB ObjectId as string")
    created_at: datetime
    question_score: int = Field(..., description="Equals number of questions generated")
    generation_attempts: int
    generation_time: float = Field(..., description="Seconds taken to generate")
    tokens_used: int
    cost: float


class QuestionItem(BaseModel):
    """ Contains information about a single question item. """
    question: str = Field(..., description="The question text")
    options: dict[OptionLabel , str] = Field(..., description="Mapping of option labels to option text")
    correct_option: OptionLabel = Field(..., description="The label of the correct option")
    explanation: str = Field(..., description="Explanation for the correct answer")


class BaseResponse(BaseModel):
    no_of_questions: int
    questions: list[QuestionItem]
    metadata: Metadata


class ComprehensionResponse(BaseResponse):
    """ Response model for comprehension-based questions. """
    passage_title: str = Field(..., description="Title of the passage")
    passage_text: str = Field(..., description="Text of the passage")
    question_type: ComprehensionBasedType

    # (BaseResponse model_validator still applies)


# Example usage note:
# if req.type == QuestionType.comprehension_based:
#     resp = ComprehensionResponse(...)
# else:
#     resp = BaseResponse(...)
