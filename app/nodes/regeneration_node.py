from app.schemas.langgraph_schema import QuestionState
from app.helpers.regeneration_helper import regenerate_question
from app.helpers.validation_helper import validate_questions
from app.helpers.chroma_helper import search_similar_questions


async def regeneration_node(state: QuestionState) -> QuestionState:
    print("\n3) Regenerating failed questions...")

    req = state["request"]
    generated_questions = state["question_state"].copy()
    validated_results = state["validation_state"].copy()
    total_regeneration_attempts = state.get("total_regeneration_attempts")

    regenerated_count = 0

    for idx, result in enumerate(validated_results):
        if not result.added_to_vectordb:
            print(f"  → Regenerating question {idx + 1}")
            print(f"    Original: {generated_questions[idx].question[:60]}...")

            regenerated_q, regen_time = await regenerate_question(
                req,
                generated_questions[idx],
                result,
                temperature=state["current_retry"] * 0.3,
            )

            generated_questions[idx].question = regenerated_q.question
            generated_questions[idx].options = regenerated_q.options
            generated_questions[idx].correct_option = regenerated_q.correct_option
            generated_questions[idx].explanation = regenerated_q.explanation
            generated_questions[idx].total_time += regen_time
            generated_questions[idx].retries += 1

            print(f"    Regenerated: {regenerated_q.question[:60]}...")
            print(f"    Regeneration time: {regen_time:.2f}s")

            # Search for similar questions with the regenerated question
            similar = await search_similar_questions(
                question=regenerated_q, subject=req.subject, topic=req.topic, top_k=3
            )

            new_validation, validation_time = await validate_questions(
                req, regenerated_q, similar
            )

            generated_questions[idx].total_time += validation_time

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
