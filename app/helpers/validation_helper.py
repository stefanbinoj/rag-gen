import time
from typing import cast, Optional, List
from app.deps import get_llm_client
from app.schemas.input_schema import ComprehensionReqPara, QuestionReqPara
from app.schemas.output_schema import (
    ComprehensionQuestionItem,
    ComprehensionType,
    FillInTheBlankQuestionItem,
    QuestionItem,
    SubjectiveQuestionItem,
    ValidationResult,
    ValidationNodeReturn,
)
from app.helpers.db_helper import get_model_name, get_prompt
from app.helpers.chroma_helper import add_question_to_chroma


async def validate_questions(
    state: QuestionReqPara | ComprehensionReqPara,
    question: QuestionItem | ComprehensionQuestionItem | FillInTheBlankQuestionItem | SubjectiveQuestionItem,
    similar_questions: Optional[List[dict]] = None,
    add_to_db: bool = True,
    is_comprehension: bool = False,
    comprehension_passage: str | None = None,
    is_fill_blank: bool = False,
    is_subjective: bool = False,
) -> tuple[ValidationNodeReturn, float, int]:
    start_time = time.time()
    comprehension_type: Optional[ComprehensionType] = None

    if is_comprehension:
        question = cast(ComprehensionQuestionItem, question)
        comprehension_type = question.comprehension_type

    model_name = await get_model_name("validation")
    llm = get_llm_client(model_name)

    # Determine system prompt based on question type
    if is_subjective:
        system_prompt_name = "subjective_validation"
    elif is_fill_blank:
        system_prompt_name = "fill_blank_validation"
    elif is_comprehension:
        system_prompt_name = "comprehensive_question_validation"
    else:
        system_prompt_name = "validation"
    
    system_prompt = await get_prompt(system_prompt_name)

    model_with_structure = llm.with_structured_output(ValidationResult, include_raw=True)

    # Build similar section first
    similar_section = ""
    if similar_questions:
        similar_section = "\n\nSimilar questions found in database:"
        for i, sim_q in enumerate(similar_questions[:3], 1):
            similarity = sim_q.get("distance", "N/A")
            similar_section += f"\n{i}. {sim_q['question']}\n   (Similarity: {similarity}) (Metadata: {sim_q.get('metadata')})"
        similar_section += "\n\nCompare the provided question with these similar ones. Are they essentially the same? Would they have the same answer?"

    # Build validation message based on question type
    if is_subjective:
        subjective_q = cast(SubjectiveQuestionItem, question)
        user_message = f"""
Validate this subjective question:

{f"Age: {state.age} | " if state.age else ""}Subject: {state.subject} | Topic: {state.topic}
Stream: {state.stream.value} | Country: {state.country} | Difficulty: {state.difficulty.value}
{f"Sub-topic: {state.sub_topic}" if state.sub_topic else ""}

Question: {subjective_q.question}
Expected Answer: {subjective_q.expected_answer}
Marking Scheme: {subjective_q.marking_scheme.model_dump()}

Also consider the following similar questions from the database to avoid duplicates:
{similar_section}

Instructions:
- Assess correctness, clarity, relevance to topic, and any factual errors.
- Verify the expected answer is comprehensive and correct.
- Check that the marking scheme is detailed, specific, and marks add up correctly.
- Provide a score (0.0-1.0), duplication_chance (0.0-1.0), and a list of issues if any.
"""
    elif is_fill_blank:
        fill_question = cast(FillInTheBlankQuestionItem, question)
        user_message = f"""
Validate this fill-in-the-blank question:

{f"Age: {state.age} | " if state.age else ""}Subject: {state.subject} | Topic: {state.topic}
Stream: {state.stream.value} | Country: {state.country} | Difficulty: {state.difficulty.value}
{f"Sub-topic: {state.sub_topic}" if state.sub_topic else ""}

Question: {fill_question.question}
Answer: {fill_question.answer}
Acceptable Answers: {fill_question.acceptable_answers}
Explanation: {fill_question.explanation}

Also consider the following similar questions from the database to avoid duplicates:
{similar_section}

Instructions:
- Assess correctness, clarity, relevance to topic, and any factual errors.
- Verify the answer correctly fills the blank.
- Check that acceptable_answers are truly valid alternatives.
- Provide a score (0.0-1.0), duplication_chance (0.0-1.0), and a list of issues if any.
"""
    else:
        # Cast to QuestionItem for MCQ/comprehension types
        mcq_question = cast(QuestionItem | ComprehensionQuestionItem, question)
        option_a = mcq_question.options.A
        option_b = mcq_question.options.B
        option_c = mcq_question.options.C
        option_d = mcq_question.options.D

        user_message_normal = f"""
Validate this MCQ:

{f"Age: {state.age} | " if state.age else ""}Subject: {state.subject} | Topic: {state.topic}
Stream: {state.stream.value} | Country: {state.country} | Difficulty: {state.difficulty.value}
{f"Sub-topic: {state.sub_topic}" if state.sub_topic else ""}

Question: {mcq_question.question}
Options: A) {option_a} | B) {option_b} | C) {option_c} | D) {option_d}
Correct: {mcq_question.correct_option.value}
Explanation: {mcq_question.explanation}

Also consider the following similar questions from the database to avoid duplicates:
{similar_section}

Instructions:
- Assess correctness, clarity, relevance to topic, and any factual errors.
- Provide a score (0.0-1.0), duplication_chance (0.0-1.0), and a list of issues if any.
"""

        user_message_comprehensive = f"""
Validate this comprehension-based MCQ (answers must be supported by the passage):

{f"Age: {state.age} | " if state.age else ""}Subject: {state.subject} | Topic: {state.topic}
Stream: {state.stream.value} | Country: {state.country} | Difficulty: {state.difficulty.value}
{f"Sub-topic: {state.sub_topic}" if state.sub_topic else ""}

{f"Comprehension Passage: {comprehension_passage}" if is_comprehension else "N/A"}

Question: {mcq_question.question}
Options: A) {option_a} | B) {option_b} | C) {option_c} | D) {option_d}
Correct: {mcq_question.correct_option.value}
Explanation: {mcq_question.explanation}
question_type: {comprehension_type}

Also consider the following similar questions from the database to avoid duplicates:
{similar_section}

Instructions:
- Verify the correct option is directly supported by the passage.
- Flag any options that could be justified by the passage (ambiguity), factual errors, or misinterpretation.
- Provide a score (0.0-1.0), duplication_chance (0.0-1.0), and list of issues with short remediation suggestions.
"""

        user_message = (
            user_message_comprehensive if is_comprehension else user_message_normal
        )

    result = model_with_structure.invoke(
        [
            ("system", system_prompt),
            ("user", user_message),
        ]
    )

    validation_time = time.time() - start_time

    total_token = result["raw"].response_metadata["token_usage"]["total_tokens"]
    parsed = result["parsed"]

    # Cast result to ValidationResult object
    validation_result: ValidationResult = cast(ValidationResult, parsed)

    return_value = ValidationNodeReturn(
        validation_result=validation_result,
        added_to_vectordb=False,
        similar_section=similar_section,
        uuid=None,
    )
    if not add_to_db:
        return return_value, validation_time, total_token

    chroma_res, question_id = await add_question_to_chroma(
        question=question.question,
        subject=state.subject,
        topic=state.topic,
        score=validation_result.score,
        duplication_chance=validation_result.duplication_chance,
    )

    return_value.added_to_vectordb = chroma_res
    return_value.uuid = question_id
    return return_value, validation_time, total_token
