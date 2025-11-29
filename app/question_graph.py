from time import time
from langgraph.graph import StateGraph, END
from app.schemas.langgraph_schema import QuestionState
from app.nodes.generation_node import generation_node
from app.nodes.validation_node import validation_node
from app.nodes.regeneration_node import regeneration_node
from app.schemas.mongo_models import GenerationLog, QuestionLog
from config import MAX_RETRIES


async def save_to_db_node(state: QuestionState) -> QuestionState:
    print("\n4) Saving to database...")

    question_logs = []

    # Create QuestionLog entries for each question
    for q, v in zip(state["question_state"], state["validation_state"]):
        if not v.added_to_vectordb or not v.uuid:
            continue  # Skip questions that were not added to the vector DB
        question_logs.append(
            QuestionLog(
                chroma_id=v.uuid,
                question=q.question,
                options=q.options,
                correct_option=q.correct_option.value,
                explanation=q.explanation,
                validation_score=v.validation_result.score,
                duplication_chance=v.validation_result.duplication_chance,
                total_time=q.total_time,
                total_attempts=q.retries,
                issues=v.validation_result.issues,
                similar_questions=v.similar_section,
            )
        )

    # Create and save the generation log
    log = GenerationLog(
        request=state["request"],
        questions=question_logs,
        total_questions=state["request"].no_of_questions,
        total_questions_generated=len(question_logs),
        total_regeneration_attempts=state["total_regeneration_attempts"],
        total_retries=state["current_retry"],
        total_time=time() - state["start_time"],
    )
    await log.insert()

    # Update the generated questions with their ChromaDB IDs

    print(f"✅ Saved {len(question_logs)} questions to MongoDB")

    return {
        **state,
    }


def should_regenerate(state: QuestionState) -> str:
    has_failed = any(
        not result.added_to_vectordb
        for result in state["validation_state"]
    )


    if has_failed and state["current_retry"] < MAX_RETRIES:
        failed_count = sum(
            1 for r in state["validation_state"]
            if not r.added_to_vectordb
        )
        print(f"\n🔄 Routing to regeneration ({failed_count} questions need regeneration) with curent retry {state['current_retry']}/{MAX_RETRIES}")
        return "regenerate"
    else:
        if has_failed:
            failed_count = sum(
                1 for r in state["validation_state"]
                if not r.added_to_vectordb
            )
            print(f"\n⚠️  Max retries reached, saving anyway ({failed_count} questions still rejected)")
        else:
            print("\n||||Exiting regeneration loop, all questions validated successfully||||")
        return "save"


def create_question_generation_graph():
    workflow = StateGraph(QuestionState)

    # Add all nodes to the graph
    workflow.add_node("generate", generation_node)
    workflow.add_node("validate", validation_node)
    workflow.add_node("regenerate", regeneration_node)
    workflow.add_node("save", save_to_db_node)


    # Start with generation
    workflow.set_entry_point("generate")

    # After generation, always validate
    workflow.add_edge("generate", "validate")

    # After validation, conditionally route to regeneration or save
    workflow.add_conditional_edges(
        "validate",
        should_regenerate,
        {
            "regenerate": "regenerate",
            "save": "save"
        }
    )

    # After regeneration, validate again (creating a feedback loop)
    workflow.add_conditional_edges(
        "regenerate",
        should_regenerate,
        {
            "regenerate": "regenerate",
            "save": "save"
        }
    )
    # After saving, end the workflow
    workflow.add_edge("save", END)

    # Compile and return the graph
    return workflow.compile()


# Create a singleton instance of the compiled graph
question_graph = create_question_generation_graph()
