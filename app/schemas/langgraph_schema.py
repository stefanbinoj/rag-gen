from typing import TypedDict, List
from app.schemas.input_schema import QuestionReqPara
from app.schemas.output_schema import QuestionItem, ValidationNodeReturn
from app.schemas.mongo_models import QuestionLog

class GeneratedQuestionsStats(QuestionItem):
    total_time: float
    retries: int

class QuestionState(TypedDict):
    start_time: float
    request: QuestionReqPara

    # Generation Phase
    question_state: List[GeneratedQuestionsStats]

    # Validation Phase
    validation_state: List[ValidationNodeReturn]  # Validation results for each question

    current_retry: int

    total_regeneration_attempts: int

