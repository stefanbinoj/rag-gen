from typing import cast
from app.schemas.input_schema import GraphType
from app.schemas.langgraph_schema import (
    GeneratedComprehensionQuestionsStats,
    GeneratedQuestionsStats,
    QuestionState,
)
from app.schemas.output_schema import ComprehensionQuestionItem
from app.helpers.generation_helper import generate_questions


async def generation_node(state: QuestionState) -> QuestionState:
    print("\n1) Generating questions...")

    is_comprehension = state["type"] == GraphType.comprehension
    generated_questions, generation_time, total_token = await generate_questions(
        state["request"],
        is_comprehension=is_comprehension,
        comprehension_passage=state["comprehensive_paragraph"],
    )

    print(f"Generated {len(generated_questions)} questions in {generation_time:.2f}s")

    if not is_comprehension:
        new_state = [
            GeneratedQuestionsStats(
                question=q.question,
                options=q.options,
                correct_option=q.correct_option,
                explanation=q.explanation,
                total_time=generation_time // len(generated_questions),
                retries=0,
                total_tokens=total_token // len(generated_questions),
            )
            for q in generated_questions
        ]

    else:
        comprehension_questions = cast(
            list[ComprehensionQuestionItem], generated_questions
        )
        new_state = [
            GeneratedComprehensionQuestionsStats(
                question=q.question,
                options=q.options,
                correct_option=q.correct_option,
                explanation=q.explanation,
                total_time=generation_time // len(comprehension_questions),
                retries=0,
                comprehension_type=q.comprehension_type,
                total_tokens=total_token // len(comprehension_questions),
            )
            for q in comprehension_questions
        ]

    return {
        **state,
        "question_state": new_state,
    }
