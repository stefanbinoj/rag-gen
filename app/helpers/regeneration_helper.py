import time
from app.deps import get_llm_client
from app.schemas.input_schema import QuestionReqPara, ComprehensionReqPara
from app.schemas.output_schema import QuestionItem, ValidationNodeReturn
from app.helpers.db_helper import get_model_name, get_prompt


async def regenerate_question(
    req: QuestionReqPara | ComprehensionReqPara,
    question: QuestionItem,
    validation_result: ValidationNodeReturn,
    temperature: float = 0.3,
    is_comprehension: bool = False,
    comprehension_passage: str | None = None,
) -> tuple[QuestionItem, float]:
    start_time = time.time()
    model_name = await get_model_name("regeneration")
    llm = get_llm_client(model_name, temperatur=temperature)

    system_prompt_name = "comprehensive_question_regeneration" if is_comprehension else "regeneration"
    system_prompt = await get_prompt(system_prompt_name)

    model_with_structure = llm.with_structured_output(QuestionItem)
    # Create different user messages for normal vs comprehension regeneration
    user_message_normal = f"""
REGENERATION TASK - Normal MCQ
-----------------------------
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

Please regenerate a single clear, unambiguous MCQ that addresses the issues above. Keep format consistent with `QuestionItem` schema.
"""

    user_message_comprehensive = f"""
REGENERATION TASK - Comprehension-based MCQ
-------------------------------------------
ORIGINAL REQUIREMENTS:
Subject: {req.subject}
Topic: {req.topic}
Sub-topic: {req.sub_topic if req.sub_topic else "N/A"}
Difficulty: {req.difficulty.value}
Stream: {req.stream.value}
Country: {req.country}
Age Group: {req.age if req.age else "N/A"}

COMPREHENSION PASSAGE:
{comprehension_passage if is_comprehension else "N/A"}

FAULTY QUESTION:
Question: {question.question}
Options: {question.options}
Correct Option: {question.correct_option}
Explanation: {question.explanation}

VALIDATION FEEDBACK:
Score: {validation_result.validation_result.score}
Duplication Chance: {validation_result.validation_result.duplication_chance}
Issues: {", ".join(validation_result.validation_result.issues)}

Please regenerate the question so that the correct answer is directly supported by the passage. Avoid ambiguity and ensure distractors are plausible but clearly incorrect when compared with the passage.
"""

    user_message = user_message_comprehensive if is_comprehension else user_message_normal

    result = model_with_structure.invoke(
        [
            ("system", system_prompt),
            ("user", user_message),
        ]
    )

    generation_time = time.time() - start_time

    if isinstance(result, QuestionItem):
        questions = result
    else:
        print(f"Unexpected result type: {type(result)}")
        raise ValueError("Failed to parse generated questions.")

    return questions, generation_time

