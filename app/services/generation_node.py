import time
from typing import List
from pydantic import BaseModel
from app.deps import get_llm_client
from app.schemas.req import QuestionReqPara
from app.schemas.res import QuestionItem
from app.services.helper import get_model_name, get_prompt


class QuestionsList(BaseModel):
    questions: List[QuestionItem]


async def generate_questions(state: QuestionReqPara) -> tuple[List[QuestionItem], float]:
    start_time = time.time()
    model_name = await get_model_name("generation")
    llm = get_llm_client(model_name)
    system_prompt = await get_prompt("generation")

    model_with_structure = llm.with_structured_output(QuestionsList)

    user_message = f"""Generate {state.no_of_questions} MCQs.

{f"Age: {state.age} | " if state.age else ""}Subject: {state.subject} | Topic: {state.topic}
Stream: {state.stream.value} | Country: {state.country.value} | Difficulty: {state.difficulty.value}
{f"Sub-topic: {state.sub_topic}" if state.sub_topic else ""}"""

    result = model_with_structure.invoke(
        [
            ("system", system_prompt),
            ("user", user_message),
        ]
    )

    generation_time = time.time() - start_time

    print(f"Generation time: {generation_time:.2f} seconds")

    # Extract questions from the result
    if isinstance(result, QuestionsList):
        questions = result.questions
    else:
        # Fallback for unexpected formats
        print(f"Unexpected result type: {type(result)}")
        raise ValueError("Failed to parse generated questions.")

    return questions , generation_time
