import json
from app.deps import get_llm_client
from app.prompts.generation_prompt import generation_system_prompt
from app.schemas.req import QuestionReqPara
from app.schemas.res import QuestionItem
from app.services.helper import get_model_name


async def generate_questions(state: QuestionReqPara):
    model_name = await get_model_name("generation")
    llm = get_llm_client(model_name)
    system_prompt = generation_system_prompt(state)

    model_with_structure = llm.with_structured_output(list[QuestionItem])
    result = model_with_structure.invoke(
        [
            ("system", system_prompt),
        ]
    )

    print("LLM result:", json.dumps(result, indent=2))
