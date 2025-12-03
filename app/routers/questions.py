import time
from fastapi import APIRouter, HTTPException
from app.schemas.input_schema import GraphType, QuestionReqPara, ComprehensionReqPara
from app.schemas.mongo_models import ComprehensionLog, GenerationLog, QuestionLog, FillInTheBlankLog, FillInTheBlankQuestionLog, SubjectiveLog, SubjectiveQuestionLog
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
    
    # Map QuestionType to GraphType
    type_mapping = {
        "mcq": GraphType.mcq,
        "fill_in_the_blank": GraphType.fill_in_the_blank,
        "subjective": GraphType.subjective,
    }
    
    graph_type = type_mapping.get(req.type.value)
    if not graph_type:
        raise HTTPException(status_code=400, detail=f"Invalid question type: {req.type}")
    
    # Pipeline names for logging
    pipeline_names = {
        "mcq": "MCQ Question Generation Pipeline",
        "fill_in_the_blank": "Fill-in-the-Blank Question Generation Pipeline",
        "subjective": "Subjective Question Generation Pipeline",
    }
    
    print("\n" + "=" * 80)
    print(pipeline_names[req.type.value])
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
            "question_type": req.type.value,
        },
        tags=[req.type.value, "question-generation", req.subject],
    )

    # Initialize state for the LangGraph workflow
    initial_state: QuestionState = {
        "type": graph_type,
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



@router.post("/generate-comprehension")
async def generate_comprehension_endpoint(req: ComprehensionReqPara):
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


@router.get("/subjective/{id}")
async def read_subjective_question(id: str):
    log = await SubjectiveLog.find_one({"questions.question_id": id})

    if not log:
        raise HTTPException(status_code=404, detail="Question not found")

    res: SubjectiveQuestionLog = [q for q in log.questions if q.question_id == id][0]

    return res
