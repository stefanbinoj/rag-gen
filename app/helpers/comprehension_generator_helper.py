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

    stream_value = state.stream.value
    if stream_value == "11Plus":
        wc_min, wc_max = 300, 450
    elif stream_value in ("GCSE", "CBSE", "ICSE"):
        wc_min, wc_max = 500, 800
    else:
        wc_min, wc_max = 450, 700



    user_message_comprehensive = f"""
Params: subject={state.subject} | topic={state.topic} | sub_topic={state.sub_topic or ''} | stream={stream_value} | difficulty={state.difficulty.value} | age={state.age or ''} | country={state.country}
More info: {state.more_information or ''}
Word count: {wc_min}-{wc_max}

Instructions:
- Produce a well-structured, exam-style comprehension passage with a clear introduction, development of ideas, illustrative example(s), and a concise conclusion.
- Make sure the passage contains specific, testable facts and details that can be used to form reliable MCQs.
- Match vocabulary and sentence complexity to the difficulty level and stream.
- Don't use any emojis and always ensure passage is in {state.country} respective context.
"""


    result = model_with_structure.invoke(
        [
            ("system", system_prompt),
            ("user", user_message_comprehensive),
        ]
    )

    print("----Comprehension generated is:\n", result)

    # Extract questions from the result
    if isinstance(result, ComprehensionResult):
        paragraph = result.paragraph
    else:
        # Fallback for unexpected formats
        print(f"Unexpected result type: {type(result)}")
        raise ValueError("Failed to parse generated questions.")

    generation_time = time.time() - start_time
    return paragraph, generation_time

