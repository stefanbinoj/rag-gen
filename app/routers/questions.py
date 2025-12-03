import time
from fastapi import APIRouter, HTTPException
from app.schemas.input_schema import GraphType, QuestionReqPara, ComprehensionReqPara
from app.schemas.mongo_models import ComprehensionLog, GenerationLog, QuestionLog, FillInTheBlankLog, FillInTheBlankQuestionLog
from app.question_graph import question_graph
from app.schemas.langgraph_schema import QuestionState
from app.helpers.langfuse_helper import create_langfuse_handler

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

    # Create Langfuse handler for this trace
    langfuse_handler = create_langfuse_handler(
        metadata={
            "subject": req.subject,
            "topic": req.topic,
            "difficulty": req.difficulty.value,
            "stream": req.stream.value,
            "country": req.country,
            "no_of_questions": req.no_of_questions,
        },
        tags=["mcq", "question-generation", req.subject],
    )

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
        "final_state": None,
    }

    final_state = await question_graph.ainvoke(
        initial_state, config={"callbacks": [langfuse_handler]}
    )

    print("\n" + "=" * 80)
    print("Pipeline Complete!")
    print(f"   Total Questions: {final_state['request'].no_of_questions}")
    print(
        f"   Successfully Added: {sum(1 for r in final_state['validation_state'] if r.added_to_vectordb)}"
    )
    print(f"   Total Time Taken: {time.time() - final_state['start_time']:.2f} seconds")
    print("=" * 80 + "\n")


    return final_state["final_state"]

@router.post(
    "/generate-fill-blank-questions",
    responses={
        201: {"description": "Fill-in-the-blank questions generated successfully"},
        422: {"description": "Invalid input"},
    },
)
async def generate_fill_blank_questions_endpoint(req: QuestionReqPara):
    start_time = time.time()
    print("\n" + "=" * 80)
    print("Fill-in-the-Blank Question Generation Pipeline")
    print("=" * 80 + "\n")

    # Create Langfuse handler for this trace
    langfuse_handler = create_langfuse_handler(
        metadata={
            "subject": req.subject,
            "topic": req.topic,
            "difficulty": req.difficulty.value,
            "stream": req.stream.value,
            "country": req.country,
            "no_of_questions": req.no_of_questions,
        },
        tags=["fill-in-the-blank", "question-generation", req.subject],
    )

    # Initialize state for the LangGraph workflow
    initial_state: QuestionState = {
        "type": GraphType.fill_in_the_blank,
        "start_time": start_time,
        "request": req,
        "question_state": [],
        "comprehensive_paragraph": None,
        "validation_state": [],
        "current_retry": 0,
        "total_regeneration_attempts": 0,
        "final_state": None,
    }

    final_state = await question_graph.ainvoke(
        initial_state, config={"callbacks": [langfuse_handler]}
    )

    print("\n" + "=" * 80)
    print("Pipeline Complete!")
    print(f"   Total Questions: {final_state['request'].no_of_questions}")
    print(
        f"   Successfully Added: {sum(1 for r in final_state['validation_state'] if r.added_to_vectordb)}"
    )
    print(f"   Total Time Taken: {time.time() - final_state['start_time']:.2f} seconds")
    print("=" * 80 + "\n")


    return final_state["final_state"]

@router.post("/passive_paragraph")
async def passive(req: ComprehensionReqPara):
    start_time = time.time()
    print("\n" + "=" * 80)
    print("Comprehension Generation Pipeline")
    print("=" * 80 + "\n")

    # Create Langfuse handler for this trace
    langfuse_handler = create_langfuse_handler(
        metadata={
            "subject": req.subject,
            "topic": req.topic,
            "difficulty": req.difficulty.value,
            "stream": req.stream.value,
            "country": req.country,
            "no_of_questions": req.no_of_questions,
            "generate_comprehension": req.generate_comprehension,
        },
        tags=["comprehension", "question-generation", req.subject],
    )

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
        "final_state": None,
    }

    final_state = await question_graph.ainvoke(
        initial_state, config={"callbacks": [langfuse_handler]}
    )

    print("\n" + "=" * 80)
    print("Pipeline Complete!")
    print(f"   Total Questions: {final_state['request'].no_of_questions}")
    print(
        f"   Successfully Added: {sum(1 for r in final_state['validation_state'] if r.added_to_vectordb)}"
    )
    print(f"   Total Time Taken: {time.time() - final_state['start_time']:.2f} seconds")
    print("=" * 80 + "\n")


    return final_state["final_state"]

@router.get("/mcq/{id}")
async def read_question(id: str):
    log = await GenerationLog.find_one({"questions.question_id": id})

    if not log:
        raise HTTPException(status_code=404, detail="Question not found")

    res: QuestionLog = [q for q in log.questions if q.question_id == id][0]

    return res


@router.get("/comprehension/{id}")
async def read_comprehension_question(id: str):
    log = await ComprehensionLog.find_one({"questions.question_id": id})

    if not log:
        raise HTTPException(status_code=404, detail="Question not found")

    res: QuestionLog = [q for q in log.questions if q.question_id == id][0]

    return {
        "paragraph": log.paragraph,
        "question": res,
    }


@router.get("/fill-blank/{id}")
async def read_fill_blank_question(id: str):
    log = await FillInTheBlankLog.find_one({"questions.question_id": id})

    if not log:
        raise HTTPException(status_code=404, detail="Question not found")

    res: FillInTheBlankQuestionLog = [q for q in log.questions if q.question_id == id][0]

    return res
