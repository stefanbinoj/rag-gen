import time
from typing import cast
from app.deps import get_llm_client
from app.prompts.validation_prompt import validation_system_prompt
from app.schemas.req import QuestionReqPara
from app.schemas.res import QuestionItem, OptionLabel, ValidationResult
from app.services.helper import get_model_name


async def validate_questions(
    state: QuestionReqPara, question: QuestionItem
) -> ValidationResult:
    """
    Validate a single MCQ question with comprehensive metadata extraction.

    Args:
        state: QuestionReqPara containing context about the question
        question: QuestionItem to validate

    Returns:
        ValidationResult containing validation score, recommendation, and metadata
    """
    start_time = time.time()
    model_name = await get_model_name("validation")
    llm = get_llm_client(model_name)

    system_prompt = validation_system_prompt()

    # Use structured output to parse JSON response into ValidationResult
    model_with_structure = llm.with_structured_output(ValidationResult)

    # Format options for display
    option_a = question.options.get(OptionLabel.A, "N/A")
    option_b = question.options.get(OptionLabel.B, "N/A")
    option_c = question.options.get(OptionLabel.C, "N/A")
    option_d = question.options.get(OptionLabel.D, "N/A")

    user_message = f"""Validate this MCQ:

Age: {state.age} | Subject: {state.subject} | Topic: {state.topic}
Stream: {state.stream.value} | Country: {state.country.value} | Difficulty: {state.difficulty.value}
{f"Sub-topic: {state.sub_topic}" if state.sub_topic else ""}

Question: {question.question}
Options: A) {option_a} | B) {option_b} | C) {option_c} | D) {option_d}
Correct: {question.correct_option.value}
Explanation: {question.explanation}"""

    result = model_with_structure.invoke(
        [
            ("system", system_prompt),
            ("user", user_message),
        ]
    )

    validation_time = time.time() - start_time

    # Cast result to ValidationResult object
    validation_result: ValidationResult = cast(ValidationResult, result)

    print("Validation completed")
    print(f"  - Score: {validation_result.score}/10")
    print(f"  - Validation time: {validation_time:.2f}s")

    return validation_result
