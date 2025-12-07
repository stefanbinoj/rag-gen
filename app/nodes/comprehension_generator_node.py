from typing import cast
from app.helpers.comprehension_generator_helper import generate_comprehension
from app.schemas.input_schema import ComprehensionReqPara
from app.schemas.langgraph_schema import QuestionState


async def comprehension_generator_node(state: QuestionState) -> QuestionState:
    print("\n0) Generating comprehension...")

    req = cast(ComprehensionReqPara, state["request"])

    generated_paragraph, generation_time, total_input, total_output = await generate_comprehension(
        req
    )

    print(f"Generated comprehension paragraph in {generation_time:.2f} seconds.")

    return {
        **state,
        "comprehensive_paragraph": generated_paragraph,
    }
