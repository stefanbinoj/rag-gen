from typing import cast
from app.schemas.input_schema import GraphType
from app.schemas.langgraph_schema import (
    GeneratedComprehensionQuestionsStats,
    GeneratedFillInTheBlankQuestionsStats,
    GeneratedSubjectiveQuestionsStats,
    QuestionItem,
    GeneratedQuestionsStats,
    QuestionState,
)
from app.schemas.output_schema import ComprehensionQuestionItem, FillInTheBlankQuestionItem, SubjectiveQuestionItem
from app.helpers.generation_helper import generate_questions


async def generation_node(state: QuestionState) -> QuestionState:
    print("\n1) Generating questions...")

    is_comprehension = state["type"] == GraphType.comprehension
    is_fill_blank = state["type"] == GraphType.fill_in_the_blank
    is_subjective = state["type"] == GraphType.subjective
    generated_questions, generation_time, total_token = await generate_questions(
        state["request"],
        is_comprehension=is_comprehension,
        comprehension_passage=state["comprehensive_paragraph"],
        is_fill_blank=is_fill_blank,
        is_subjective=is_subjective,
    )

    print(f"Generated {len(generated_questions)} questions in {generation_time:.2f}s")

    if is_subjective:
        subjective_questions = cast(
            list[SubjectiveQuestionItem], generated_questions
        )
        new_state = [
            GeneratedSubjectiveQuestionsStats(
                question=q.question,
                expected_answer=q.expected_answer,
                marking_scheme=q.marking_scheme,
                total_time=generation_time // len(subjective_questions),
                retries=0,
                total_tokens=total_token // len(subjective_questions),
            )
            for q in subjective_questions
        ]
    elif is_fill_blank:
        fill_blank_questions = cast(
            list[FillInTheBlankQuestionItem], generated_questions
        )
        new_state = [
            GeneratedFillInTheBlankQuestionsStats(
                question=q.question,
                answer=q.answer,
                acceptable_answers=q.acceptable_answers,
                explanation=q.explanation,
                total_time=generation_time // len(fill_blank_questions),
                retries=0,
                total_tokens=total_token // len(fill_blank_questions),
            )
            for q in fill_blank_questions
        ]
    elif not is_comprehension:
        mcq_questions = cast(
            list[QuestionItem], generated_questions
        )
        new_state = [
            GeneratedQuestionsStats(
                question=q.question,
                options=q.options,
                correct_option=q.correct_option,
                explanation=q.explanation,
                total_time=generation_time // len(mcq_questions),
                retries=0,
                total_tokens=total_token // len(mcq_questions),
            )
            for q in mcq_questions
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
