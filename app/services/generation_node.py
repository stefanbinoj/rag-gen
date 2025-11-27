import time
from typing import cast, List
from app.deps import get_llm_client
from app.prompts.generation_prompt import generation_system_prompt
from app.schemas.req import QuestionReqPara
from app.schemas.res import QuestionItem
from app.services.helper import get_model_name, _extract_metadata


async def generate_questions(state: QuestionReqPara) -> List[QuestionItem]:
    """
    Generate MCQ questions with comprehensive metadata extraction.

    Args:
        state: QuestionReqPara containing generation parameters

    Returns:
        List of QuestionItem objects
    """
    start_time = time.time()
    model_name = await get_model_name("generation")
    llm = get_llm_client(model_name)
    system_prompt = generation_system_prompt()

    model_with_structure = llm.with_structured_output(list[QuestionItem])

    user_message = f"""Generate {state.no_of_questions} MCQs.

Age: {state.age} | Subject: {state.subject} | Topic: {state.topic}
Stream: {state.stream.value} | Country: {state.country.value} | Difficulty: {state.difficulty.value}
{f"Sub-topic: {state.sub_topic}" if state.sub_topic else ""}"""

    # Invoke the LLM with structured output
    result = model_with_structure.invoke(
        [
            ("system", system_prompt),
            ("user", user_message),
        ]
    )

    generation_time = time.time() - start_time

    print(f"Generation time: {generation_time:.2f} seconds")

    # Handle different response types from LLM
    if isinstance(result, dict) and "iterable" in result:
        # LLM wrapped the response in a dict with 'iterable' key
        raw_questions = result["iterable"]
        print("\n=== DEBUG: Raw questions ===")
        print(f"Type of raw_questions: {type(raw_questions)}")
        print(
            f"Length: {len(raw_questions) if hasattr(raw_questions, '__len__') else 'N/A'}"
        )
        if raw_questions and len(raw_questions) > 0:
            print(f"Type of first item: {type(raw_questions[0])}")
            print(f"First item: {raw_questions[0]}")
        print("============================\n")

        # Convert dicts to QuestionItem objects
        questions: List[QuestionItem] = []
        for q in raw_questions:
            print(f"Processing item type: {type(q)}, value: {q}")
            if isinstance(q, dict):
                questions.append(QuestionItem(**q))
            elif isinstance(q, QuestionItem):
                questions.append(q)
            elif isinstance(q, str):
                print(f"WARNING: Got string instead of dict/QuestionItem: {q}")
            else:
                questions.append(cast(QuestionItem, q))
    elif isinstance(result, dict) and "questions" in result:
        # Alternative dict format
        raw_questions = result["questions"]
        questions: List[QuestionItem] = [
            QuestionItem(**q) if isinstance(q, dict) else q for q in raw_questions
        ]
    elif isinstance(result, list):
        # Already a list - still may need conversion
        questions: List[QuestionItem] = [
            QuestionItem(**q) if isinstance(q, dict) else q for q in result
        ]
    else:
        # Unexpected format - wrap in list
        questions: List[QuestionItem] = [cast(QuestionItem, result)]

    print(f"Extracted {len(questions)} questions")
    if questions and len(questions) > 0:
        print(f"First question type: {type(questions[0])}")
        print(f"First question object: {questions[0]}")

    return questions
