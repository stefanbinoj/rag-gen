from app.schemas.input_schema import GraphType
from app.schemas.langgraph_schema import QuestionState
from app.helpers.validation_helper import validate_questions
from app.helpers.chroma_helper import search_similar_questions


async def validation_node(state: QuestionState) -> QuestionState:
    print("\n2) Validating generated_questions...")

    validated_results = []
    req = state["request"]
    generated_questions = state["question_state"]
    comprehension_passage = state.get("comprehensive_paragraph")
    is_comprehension = state["type"] == GraphType.comprehension

    for idx, question in enumerate(generated_questions):
        print(f"  → Validating question {idx + 1}/{len(generated_questions)}")

        similar_questions = await search_similar_questions(
            question=question, subject=req.subject, topic=req.topic, top_k=3
        )

        # Validate the question
        validation_result, validation_time, total_token = await validate_questions(
            req,
            question,
            similar_questions,
            is_comprehension=is_comprehension,
            comprehension_passage=comprehension_passage,
        )
        generated_questions[idx].total_time += validation_time
        generated_questions[idx].total_tokens += total_token

        # Log validation results
        status = "✅ ADDED" if validation_result.added_to_vectordb else "❌ REJECTED"
        print(
            f"  {status} | Score: {validation_result.validation_result.score:.2f} | "
            f"Duplication: {validation_result.validation_result.duplication_chance:.2f} | "
            f"Time: {validation_time:.2f}s"
        )

        if validation_result.validation_result.issues:
            print(
                f"    Issues: {', '.join(validation_result.validation_result.issues)}"
            )

        validated_results.append(validation_result)

    # Summary
    added_count = sum(1 for r in validated_results if r.added_to_vectordb)
    rejected_count = len(validated_results) - added_count
    print(f"\n  ✅ Added: {added_count} | ❌ Rejected: {rejected_count}")

    return {
        **state,
        "validation_state": validated_results,
        "question_state": generated_questions,
    }
