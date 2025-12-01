from pydantic import BaseModel
from app.deps import get_llm_client
from app.prompts.comprehensive_generation_prompt import comprehensive_generation_system_prompt
from app.schemas.input_schema import ComprehensionReqPara
import asyncio

from config import load_environment_variables

class ComprehensionResult(BaseModel):
    paragraph: str

async def generate_comprehension(
    state: ComprehensionReqPara,
) :
    load_environment_variables()
    model_name = "openai/gpt-5.1-chat"
    llm = get_llm_client(model_name)
    system_prompt = comprehensive_generation_system_prompt()

    model_with_structure = llm.with_structured_output(ComprehensionResult, include_raw=True)

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
Word count:  for demo purpose keept it one line

Instructionsny emojis and always ensure passage is in {state.country} respective context.
"""


    result = model_with_structure.invoke(
        [
            ("system", system_prompt),
            ("user", user_message_comprehensive),
        ]
    )

    print(result)
    total = result["raw"].response_metadata["token_usage"]["total_tokens"]
    parsed = result["parsed"]
    print("="*20)
    print(total)
    print("="*20)
    print(parsed)
    print("="*20)

    # Extract questions from the result
    if isinstance(parsed, ComprehensionResult):
        paragraph = parsed.paragraph
    else:
        # Fallback for unexpected formats
        print(f"Unexpected result type: {type(result)}")
        raise ValueError("Failed to parse generated questions.")



state_dict = {
  "type": "mcq",
  "subject": "english",
  "topic": "coastal animals",

  "difficulty": "easy",
  "stream": "11Plus",
  "country": "India",

  "no_of_questions": 3,
  "language": "English",
  "generate_comprehension": True,
  "more_information": "expalin about how disaster affect them early and is underlooked"
}

state = ComprehensionReqPara(**state_dict)

async def main():
    await generate_comprehension(state)

asyncio.run(main())
