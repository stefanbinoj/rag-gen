from app.schemas.input_schema import GraphType
from app.schemas.langgraph_schema import GeneratedQuestionsStats, QuestionState
from app.helpers.generation_helper import generate_questions


async def generation_node(state: QuestionState) -> QuestionState:
    print("\n1) Generating questions...")

    is_comprehension = state["type"] == GraphType.comprehension
    generated_questions, generation_time = await generate_questions(state["request"], is_comprehension=is_comprehension,
                                                                    comprehension_passage=state["comprehensive_paragraph"])

    print(f"Generated {len(generated_questions)} questions in {generation_time:.2f}s")

    new_state: list[GeneratedQuestionsStats] = [
        GeneratedQuestionsStats(
            question=q.question,
            options=q.options,
            correct_option=q.correct_option,
            explanation=q.explanation,
            total_time=generation_time,
            retries=0,
        )
        for q in generated_questions
    ]

    return {
        **state,
        "question_state": new_state,
    }
