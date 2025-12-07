from typing import TypedDict, List
from app.schemas.input_schema import ComprehensionReqPara, GraphType, QuestionReqPara
from app.schemas.mongo_models import ComprehensionLog, GenerationLog, FillInTheBlankLog, SubjectiveLog
from app.schemas.output_schema import (
    ComprehensionQuestionItem,
    FillInTheBlankQuestionItem,
    QuestionItem,
    SubjectiveQuestionItem,
    ValidationNodeReturn,
)


class GeneratedQuestionsStats(QuestionItem):
    total_time: float
    retries: int
    total_input_tokens: int
    total_output_tokens: int


class GeneratedComprehensionQuestionsStats(ComprehensionQuestionItem):
    total_time: float
    retries: int
    total_input_tokens: int
    total_output_tokens: int


class GeneratedFillInTheBlankQuestionsStats(FillInTheBlankQuestionItem):
    total_time: float
    retries: int
    total_input_tokens: int
    total_output_tokens: int


class GeneratedSubjectiveQuestionsStats(SubjectiveQuestionItem):
    total_time: float
    retries: int
    total_input_tokens: int
    total_output_tokens: int


class QuestionState(TypedDict):
    type: GraphType

    start_time: float
    request: QuestionReqPara | ComprehensionReqPara

    # Comprehensive
    comprehensive_paragraph: str | None

    # Generation Phase
    question_state: (
        List[GeneratedQuestionsStats]
        | List[GeneratedComprehensionQuestionsStats]
        | List[GeneratedFillInTheBlankQuestionsStats]
        | List[GeneratedSubjectiveQuestionsStats]
    )

    validation_state: List[ValidationNodeReturn]  # Validation results for each question

    current_retry: int
    total_regeneration_attempts: int

    final_state: GenerationLog | ComprehensionLog | FillInTheBlankLog | SubjectiveLog | None

