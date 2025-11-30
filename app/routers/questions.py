import time
from fastapi import APIRouter, HTTPException
from app.helpers.db_helper import get_model_name
from app.schemas.input_schema import GraphType, QuestionReqPara, ComprehensionReqPara
from app.schemas.mongo_models import ComprehensionLog, GenerationLog, QuestionLog
from app.question_graph import question_graph
from app.schemas.langgraph_schema import QuestionState

router = APIRouter()


@router.post(
    "/generate-questions",
    responses={
        201: {"description": "Questions generated successfully"},
        422: {"description": "Invalid input"},
    },
)
async def generate_questions_endpoint(req: QuestionReqPara):
    start_time = time.time()
    print("\n" + "=" * 80)
    print("Question Generation Pipeline")
    print("=" * 80 + "\n")

    # Initialize state for the LangGraph workflow
    initial_state: QuestionState = {
        "type": GraphType.mcq,
        "start_time": start_time,
        "request": req,
        "question_state": [],
        "comprehensive_paragraph": None,
        "validation_state": [],
        "current_retry": 0,
        "total_regeneration_attempts": 0,
    }

    final_state = await question_graph.ainvoke(initial_state)

    print("\n" + "=" * 80)
    print("Pipeline Complete!")
    print(f"   Total Questions: {final_state['request'].no_of_questions}")
    print(
        f"   Successfully Added: {sum(1 for r in final_state['validation_state'] if r.added_to_vectordb)}"
    )
    print(f"   Total Time Taken: {time.time() - final_state['start_time']:.2f} seconds")
    print("=" * 80 + "\n")

    final_response = []
    model_used = await get_model_name("generation")

    for q, v in zip(final_state["question_state"], final_state["validation_state"]):
        if not v.added_to_vectordb or not v.uuid:
            continue  # Skip questions that were not added to the vector DB
        final_response.append(
            {
                "id": v.uuid,
                "question": q.question,
                "options": q.options,
                "correct_option": q.correct_option.value,
                "explanation": q.explanation,
                "validation_score": v.validation_result.score,
                "duplication_chance": v.validation_result.duplication_chance,
                "total_time": q.total_time,
                "total_attempts": q.retries,
                "model_used": model_used,
            }
        )

    return {
        "questions": final_response,
    }


@router.post("/passive_paragraph")
async def passive(req: ComprehensionReqPara):
    start_time = time.time()
    print("\n" + "=" * 80)
    print("Comprehension Generation Pipeline")
    print("=" * 80 + "\n")

    # Initialize state for the LangGraph workflow
    initial_state: QuestionState = {
        "type": GraphType.comprehension,
        "start_time": start_time,
        "request": req,
        "question_state": [],
        "comprehensive_paragraph": (req.comprehensive_paragraph or "")
        if not req.generate_comprehension
        else None,
        "validation_state": [],
        "current_retry": 0,
        "total_regeneration_attempts": 0,
    }

    final_state = await question_graph.ainvoke(initial_state)

    print("\n" + "=" * 80)
    print("Pipeline Complete!")
    print(f"   Total Questions: {final_state['request'].no_of_questions}")
    print(
        f"   Successfully Added: {sum(1 for r in final_state['validation_state'] if r.added_to_vectordb)}"
    )
    print(f"   Total Time Taken: {time.time() - final_state['start_time']:.2f} seconds")
    print("=" * 80 + "\n")

    final_response = []
    model_used = await get_model_name("generation")

    for q, v in zip(final_state["question_state"], final_state["validation_state"]):
        if not v.added_to_vectordb or not v.uuid:
            continue  # Skip questions that were not added to the vector DB
        final_response.append(
            {
                "id": v.uuid,
                "question": q.question,
                "options": q.options,
                "correct_option": q.correct_option.value,
                "explanation": q.explanation,
                "validation_score": v.validation_result.score,
                "duplication_chance": v.validation_result.duplication_chance,
                "total_time": q.total_time,
                "total_attempts": q.retries,
                "comprehension_type": q.comprehension_type,
                "model_used": model_used,

            }
        )

    return {
        "paragraph": final_state["comprehensive_paragraph"],
        "questions": final_response,
    }


@router.get("/mcq/{id}")
async def read_question(id: str):
    log = await GenerationLog.find_one({"questions.chroma_id": id})

    if not log:
        raise HTTPException(status_code=404, detail="Question not found")

    res: QuestionLog = [q for q in log.questions if q.chroma_id == id][0]

    return res


@router.get("/comprehension/{id}")
async def read_comprehension_question(id: str):
    log = await ComprehensionLog.find_one({"questions.chroma_id": id})

    if not log:
        raise HTTPException(status_code=404, detail="Question not found")

    res: QuestionLog = [q for q in log.questions if q.chroma_id == id][0]

    return {
        "paragraph": log.paragraph,
        "question": res,
    }
