from app.deps import get_llm_client
from app.schemas.req import QuestionReqPara


def validate_questions(state: QuestionReqPara):
    llm = get_llm_client(state["model_name"])
    result = llm.invoke([
        ("system", state["system_prompt"]),
        ("user", state["user_prompt"])
    ])

    print("LLM result:", result)


