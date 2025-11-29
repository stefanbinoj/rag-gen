import time
from fastapi import APIRouter, HTTPException
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

    return final_state["question_state"]


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
        "comprehensive_paragraph": (req.comprehension_paragraph or "")
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

    return {
        "paragraph": final_state["comprehensive_paragraph"],
        "questions": final_state["question_state"],
    }


@router.get("/mcq/{id}")
async def read_question(id: str):
    log = await GenerationLog.find_one({"questions.chroma_id": id})

    if not log:
        raise HTTPException(status_code=404, detail="Question not found")

    res: QuestionLog = [q for q in log.questions if q.chroma_id == id][0]

    return {
        "_id": res.chroma_id,
        "question": res.question,
        "options": res.options,
        "correct_option": res.correct_option,
        "explanation": res.explanation,
        "validation_score": res.validation_score,
        "duplication_chance": res.duplication_chance,
        "total_time": res.total_time,
        "total_attempts": res.total_attempts,
        "issues": res.issues,
    }


@router.get("/comprehension/{id}")
async def read_comprehension_question(id: str):
    log = await ComprehensionLog.find_one({"questions.chroma_id": id})

    if not log:
        raise HTTPException(status_code=404, detail="Question not found")

    res: QuestionLog = [q for q in log.questions if q.chroma_id == id][0]

    return {
        "_id": res.chroma_id,
        "paragraph": log.paragraph,
        "question": res.question,
        "options": res.options,
        "correct_option": res.correct_option,
        "explanation": res.explanation,
        "validation_score": res.validation_score,
        "duplication_chance": res.duplication_chance,
        "total_time": res.total_time,
        "total_attempts": res.total_attempts,
        "issues": res.issues,
    }
