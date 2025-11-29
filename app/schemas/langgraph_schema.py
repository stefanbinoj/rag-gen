from typing import TypedDict, List
from app.schemas.input_schema import  ComprehensionReqPara, GraphType, QuestionReqPara
from app.schemas.output_schema import QuestionItem, ValidationNodeReturn

class GeneratedQuestionsStats(QuestionItem):
    total_time: float
    retries: int

class QuestionState(TypedDict):
    type: GraphType

    start_time: float
    request: QuestionReqPara | ComprehensionReqPara

    # Comprehensive
    comprehensive_paragraph: str | None

    # Generation Phase
    question_state: List[GeneratedQuestionsStats]
    validation_state: List[ValidationNodeReturn]  # Validation results for each question

    current_retry: int
    total_regeneration_attempts: int

