from typing import cast
from fastapi import APIRouter, HTTPException

from app.schemas.mongo_models import ComprehensionLog, GenerationLog, QuestionLog
from app.schemas.input_schema import ComprehensionReqPara, QuestionReqPara
from app.schemas.output_schema import (
    ComprehensionQuestionItem,
    QuestionItem,
    OptionLabel,
)
from app.helpers.chroma_helper import search_similar_questions
from app.helpers.validation_helper import validate_questions
from app.schemas.langgraph_schema import GeneratedComprehensionQuestionsStats

router = APIRouter()


@router.post("/validate-question")
async def validate_question(question_id: str):
    log = await GenerationLog.find_one({"questions.question_id": question_id})

    if not log:
        raise HTTPException(status_code=404, detail="Question not found for validation")

    res: QuestionLog = [q for q in log.questions if q.question_id == question_id][0]
    question = QuestionItem(
        question=res.question,
        options=res.options,
        correct_option=OptionLabel(res.correct_option),
        explanation=res.explanation,
    )

    req: QuestionReqPara = log.request

    print(f"\n\n    --->Validating single question {question.question}")

    similar_questions = await search_similar_questions(
        question=question.question, subject=req.subject, topic=req.topic, top_k=3
    )

    check_validation, validation_time, total_token = await validate_questions(
        req, question, similar_questions[1:], add_to_db=False
    )
    return {
        "question_id": res.question_id,
        "validation_score": check_validation.validation_result.score,
        "duplication_chance": check_validation.validation_result.duplication_chance,
        "issues": check_validation.validation_result.issues,
        "similar_questions": similar_questions,
        "validation_time": validation_time,
        "total_tokens": total_token,
    }


@router.post("/validate-passage")
async def validate_passage(question_id: str):
    log = await ComprehensionLog.find_one({"questions.question_id": question_id})

    if not log:
        raise HTTPException(status_code=404, detail="Question not found for validation")

    res: QuestionLog = [q for q in log.questions if q.question_id == question_id][0]
    comp_q = cast(GeneratedComprehensionQuestionsStats, res)
    question = ComprehensionQuestionItem(
        question=comp_q.question,
        options=comp_q.options,
        correct_option=OptionLabel(comp_q.correct_option),
        explanation=comp_q.explanation,
        comprehension_type=comp_q.comprehension_type,
    )

    req: ComprehensionReqPara = log.request

    print(f"\n\n    --->Validating single question {question.question}")

    similar_questions = await search_similar_questions(
        question=question.question, subject=req.subject, topic=req.topic, top_k=3
    )

    check_validation, validation_time, total_tokens = await validate_questions(
        req,
        question,
        similar_questions[1:],
        add_to_db=False,
        is_comprehension=True,
        comprehension_passage=log.paragraph,
    )
    return {
        "comprehensive_passage": log.paragraph,
        "question_id": res.question_id,
        "validation_score": check_validation.validation_result.score,
        "duplication_chance": check_validation.validation_result.duplication_chance,
        "issues": check_validation.validation_result.issues,
        "similar_questions": similar_questions,
        "validation_time": validation_time,
        "total_tokens": total_tokens,
    }
