from typing import cast
from app.schemas.input_schema import GraphType
from app.schemas.langgraph_schema import (
    QuestionState,
    GeneratedFillInTheBlankQuestionsStats,
    GeneratedQuestionsStats,
    GeneratedComprehensionQuestionsStats,
    GeneratedSubjectiveQuestionsStats,
)
from app.schemas.output_schema import (
    FillInTheBlankQuestionItem,
    QuestionItem,
    ComprehensionQuestionItem,
    SubjectiveQuestionItem,
)
from app.helpers.regeneration_helper import regenerate_question
from app.helpers.validation_helper import validate_questions
from app.helpers.chroma_helper import search_similar_questions


async def regeneration_node(state: QuestionState) -> QuestionState:
    print("\n3) Regenerating failed questions...")

    req = state["request"]
    generated_questions = state["question_state"].copy()
    validated_results = state["validation_state"].copy()
    total_regeneration_attempts = state["total_regeneration_attempts"]

    regenerated_count = 0
    is_comprehension = state["type"] == GraphType.comprehension
    is_fill_blank = state["type"] == GraphType.fill_in_the_blank
    is_subjective = state["type"] == GraphType.subjective
    question_type = state["type"].value

    for idx, result in enumerate(validated_results):
        if not result.added_to_vectordb:
            print(f"  → Regenerating question {idx + 1}")
            print(f"    Original: {generated_questions[idx].question[:60]}...")

            regenerated_q, regen_time, total_input, total_output = await regenerate_question(
                req,
                generated_questions[idx],
                result,
                temperature=state["current_retry"] * 0.3,
                is_comprehension=is_comprehension,
                comprehension_passage=state["comprehensive_paragraph"],
                is_fill_blank=is_fill_blank,
                is_subjective=is_subjective,
            )

            generated_questions[idx].question = regenerated_q.question

            if is_subjective:
                subj_regen = cast(SubjectiveQuestionItem, regenerated_q)
                subj_state = cast(
                    GeneratedSubjectiveQuestionsStats, generated_questions[idx]
                )
                subj_state.expected_answer = subj_regen.expected_answer
                subj_state.marking_scheme = subj_regen.marking_scheme
            elif is_fill_blank:
                fill_regen = cast(FillInTheBlankQuestionItem, regenerated_q)
                fill_state = cast(
                    GeneratedFillInTheBlankQuestionsStats, generated_questions[idx]
                )
                fill_state.answer = fill_regen.answer
                fill_state.acceptable_answers = fill_regen.acceptable_answers
                fill_state.explanation = fill_regen.explanation
            else:
                mcq_regen = cast(
                    QuestionItem | ComprehensionQuestionItem, regenerated_q
                )
                mcq_state = cast(
                    GeneratedQuestionsStats | GeneratedComprehensionQuestionsStats,
                    generated_questions[idx],
                )
                mcq_state.options = mcq_regen.options
                mcq_state.correct_option = mcq_regen.correct_option
                mcq_state.explanation = mcq_regen.explanation
            generated_questions[idx].total_time += regen_time
            generated_questions[idx].total_input_tokens += total_input
            generated_questions[idx].total_output_tokens += total_output
            generated_questions[idx].retries += 1

            print(f"    Regenerated: {regenerated_q.question[:60]}...")
            print(f"    Regeneration time: {regen_time:.2f}s")

            # Search for similar questions with the regenerated question
            similar = await search_similar_questions(
                question=regenerated_q.question,
                subject=req.subject,
                topic=req.topic,
                question_type=question_type,
                top_k=3,
            )

            (
                new_validation,
                validation_time,
                total_input_validation,
                total_output_validation,
            ) = await validate_questions(
                req,
                regenerated_q,
                similar,
                is_comprehension=is_comprehension,
                is_fill_blank=is_fill_blank,
                is_subjective=is_subjective,
                question_type=question_type,
            )

            generated_questions[idx].total_time += validation_time
            generated_questions[idx].total_input_tokens += total_input_validation
            generated_questions[idx].total_output_tokens += total_output_validation

            # Log re-validation results
            status = (
                "✅ ADDED" if new_validation.added_to_vectordb else "❌ STILL REJECTED"
            )
            print(
                f"    {status} | Score: {new_validation.validation_result.score:.2f} | "
                f"Duplication: {new_validation.validation_result.duplication_chance:.2f}"
            )

            print(
                f"    Remaining issues: {', '.join(new_validation.validation_result.issues)}"
            )

            # Update the question and validation result
            validated_results[idx] = new_validation
            regenerated_count += 1

    total_regeneration_attempts += regenerated_count
    if regenerated_count > 0:
        print(f"\n  🔄 Regenerated {regenerated_count} question(s)")
        added_count = sum(1 for r in validated_results if r.added_to_vectordb)
        print(
            f"  ✅ Total added after regeneration: {added_count}/{len(validated_results)}"
        )
    else:
        print("\n  ℹ️  No questions needed regeneration")

    return {
        **state,
        "question_state": generated_questions,
        "validation_state": validated_results,
        "total_regeneration_attempts": total_regeneration_attempts,
        "current_retry": state["current_retry"] + 1,
    }
