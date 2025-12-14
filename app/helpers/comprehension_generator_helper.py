import time

from pydantic import BaseModel
from app.deps import get_llm_client
from app.schemas.input_schema import ComprehensionReqPara
from app.helpers.db_helper import get_model_name, get_prompt

class ComprehensionResult(BaseModel):
    paragraph: str

async def generate_comprehension(
    state: ComprehensionReqPara,
) -> tuple[str, float, int,int]:
    start_time = time.time()
    model_name = await get_model_name("generation")
    llm = get_llm_client(model_name)
    system_prompt = await get_prompt("comprehension")
    
    # Enforce language in system prompt
    system_prompt += f"\n\n**LANGUAGE REQUIREMENT:** The comprehension passage MUST be generated in {state.language}. All content must strictly be in {state.language} language."
    
    # Add special_instructions to system prompt if present
    if state.special_instructions:
        system_prompt += f"\nIf custom word_counts are provided, ensure the passage adheres to them.\n\n**SPECIAL INSTRUCTIONS FROM USER (HIGHEST PRIORITY):**\n{state.special_instructions}"

    model_with_structure = llm.with_structured_output(ComprehensionResult, include_raw=True)

    wc_min, wc_max = state.min_word_count or 600, state.max_word_count or 800

    user_message_comprehensive = f"""
Params: subject={state.subject} | topic={state.topic} | sub_topic={state.sub_topic or ''} | stream={state.stream} | difficulty={state.difficulty.value} | age={state.age or ''} | country={state.country} | language={state.language}
More info: {state.more_information or ''}
Word count: {wc_min}-{wc_max}

Instructions:
- Produce a well-structured, exam-style comprehension passage with a clear introduction, development of ideas, illustrative example(s), and a concise conclusion.
- Make sure the passage contains specific, testable facts and details that can be used to form reliable MCQs.
- Match vocabulary and sentence complexity to the difficulty level and stream.
- Don't use any emojis and always ensure passage is in {state.country} respective context.
- CRITICAL: The entire passage MUST be in {state.language} language.
{f"\n\nSPECIAL INSTRUCTIONS (MUST FOLLOW): {state.special_instructions}" if state.special_instructions else ""}
"""


    result = model_with_structure.invoke(
        [
            ("system", system_prompt),
            ("user", user_message_comprehensive),
        ]
    )

    total_input = result["raw"].response_metadata["token_usage"]["prompt_tokens"]
    total_output = result["raw"].response_metadata["token_usage"]["completion_tokens"]
    parsed = result["parsed"]

    # Extract questions from the result
    if isinstance(parsed, ComprehensionResult):
        paragraph = parsed.paragraph
    else:
        # Fallback for unexpected formats
        print(f"Unexpected result type: {type(result)}")
        raise ValueError("Failed to parse generated questions.")

    generation_time = time.time() - start_time
    return paragraph, generation_time, total_input, total_output

