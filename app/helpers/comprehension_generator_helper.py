import time

from pydantic import BaseModel
from app.deps import get_llm_client
from app.schemas.input_schema import ComprehensionReqPara
from app.helpers.db_helper import get_model_name, get_prompt

class ComprehensionResult(BaseModel):
    paragraph: str

async def generate_comprehension(
    state: ComprehensionReqPara,
) -> tuple[str, float]:
    start_time = time.time()
    model_name = await get_model_name("generation")
    llm = get_llm_client(model_name)
    system_prompt = await get_prompt("comprehension")

    model_with_structure = llm.with_structured_output(ComprehensionResult)

    user_message = f"""{f"Age: {state.age} | " if state.age else ""}Subject: {state.subject} | Topic: {state.topic}
Stream: {state.stream.value} | Country: {state.country} | Difficulty: {state.difficulty.value}
{f"Sub-topic: {state.sub_topic}" if state.sub_topic else ""}
{f"Additional Information: {state.more_information}" if state.more_information else ""}"""

    result = model_with_structure.invoke(
        [
            ("system", system_prompt),
            ("user", user_message),
        ]
    )

    print("----Comprehension generation result:", result)

    # Extract questions from the result
    if isinstance(result, ComprehensionResult):
        paragraph = result.paragraph
    else:
        # Fallback for unexpected formats
        print(f"Unexpected result type: {type(result)}")
        raise ValueError("Failed to parse generated questions.")

    generation_time = time.time() - start_time
    return paragraph, generation_time

