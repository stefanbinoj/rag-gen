import time
from typing import cast
from app.deps import get_llm_client
from app.schemas.req import QuestionReqPara
from app.schemas.res import QuestionItem, ValidationNodeReturn
from app.services.helper import get_model_name, get_prompt


async def regenerate_question(
    req: QuestionReqPara,
    question: QuestionItem,
    validation_result: ValidationNodeReturn,
) -> QuestionItem:
    start_time = time.time()
    model_name = await get_model_name("regeneration")
    llm = get_llm_client(model_name, temperatur=0.3)
    system_prompt = await get_prompt("regeneration")

    model_with_structure = llm.with_structured_output(QuestionItem)

    user_message = f"""
REGENERATION TASK:
------------------
ORIGINAL REQUIREMENTS:
Subject: {req.subject}
Topic: {req.topic}
Sub-topic: {req.sub_topic if req.sub_topic else "N/A"}
Difficulty: {req.difficulty.value}
Stream: {req.stream.value}
Country: {req.country}
Age Group: {req.age if req.age else "N/A"}

FAULTY QUESTION:
Question: {question.question}
Options: {question.options}
Correct Option: {question.correct_option}
Explanation: {question.explanation}

VALIDATION FEEDBACK:
Score: {validation_result.validation_result.score}
Duplication Chance: {validation_result.validation_result.duplication_chance}
Issues: {", ".join(validation_result.validation_result.issues)}

Please regenerate this single question to address the issues above.
"""

    result = model_with_structure.invoke(
        [
            ("system", system_prompt),
            ("user", user_message),
        ]
    )

    generation_time = time.time() - start_time

    print(f"Regeneration time: {generation_time:.2f} seconds")

    # Extract questions from the result
    if isinstance(result, QuestionItem):
        questions = result
    else:
        # Fallback for unexpected formats
        print(f"Unexpected result type: {type(result)}")
        raise ValueError("Failed to parse generated questions.")

    return questions

