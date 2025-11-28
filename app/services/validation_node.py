import time
from typing import cast, Optional, List
from app.deps import get_llm_client
from app.schemas.req import QuestionReqPara
from app.schemas.res import QuestionItem, ValidationResult, ValidationNodeReturn
from app.services.helper import get_model_name, get_prompt
from app.services.chroma_node import add_question_to_chroma


async def validate_questions(
    state: QuestionReqPara,
    question: QuestionItem,
    similar_questions: Optional[List[dict]] = None,
) -> ValidationNodeReturn:
    start_time = time.time()
    model_name = await get_model_name("validation")
    llm = get_llm_client(model_name)

    system_prompt = await get_prompt("validation")

    model_with_structure = llm.with_structured_output(ValidationResult)

    option_a = question.options.A
    option_b = question.options.B
    option_c = question.options.C
    option_d = question.options.D

    similar_section = ""
    if similar_questions:
        similar_section = "\n\nSimilar questions found in database:"
        for i, sim_q in enumerate(similar_questions[:3], 1):
            similarity = sim_q.get("distance", "N/A")
            similar_section += f"\n{i}. {sim_q['question']}\n   (Similarity: {similarity}) (Metadata: {sim_q.get('metadata')})"
        similar_section += "\n\nCompare the provided question with these similar ones. Are they essentially the same? Would they have the same answer?"

    user_message = f"""Validate this MCQ:

{f"Age: {state.age} | " if state.age else ""}Subject: {state.subject} | Topic: {state.topic}
Stream: {state.stream.value} | Country: {state.country.value} | Difficulty: {state.difficulty.value}
{f"Sub-topic: {state.sub_topic}" if state.sub_topic else ""}

Question: {question.question}
Options: A) {option_a} | B) {option_b} | C) {option_c} | D) {option_d}
Correct: {question.correct_option.value}
Explanation: {question.explanation}

Also consider the following similar questions from the database to avoid duplicates:
{similar_section}"""

    result = model_with_structure.invoke(
        [
            ("system", system_prompt),
            ("user", user_message),
        ]
    )

    validation_time = time.time() - start_time

    # Cast result to ValidationResult object
    validation_result: ValidationResult = cast(ValidationResult, result)

    print(
        f"validation issues : {validation_result.issues} took time {validation_time:.2f} seconds"
    )

    chroma_res, question_id = await add_question_to_chroma(
        question=question,
        subject=state.subject,
        topic=state.topic,
        score=validation_result.score,
        duplication_chance=validation_result.duplication_chance,
    )

    return ValidationNodeReturn(
        validation_result=validation_result,
        added_to_vectordb=chroma_res,
        validation_time=validation_time,
        similar_section=similar_section,
        uuid=question_id,
    )
