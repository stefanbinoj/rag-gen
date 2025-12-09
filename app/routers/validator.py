from typing import cast
from fastapi import APIRouter, HTTPException

from app.schemas.mongo_models import (
    ComprehensionLog,
    GenerationLog,
    QuestionLog,
    FillInTheBlankLog,
    FillInTheBlankQuestionLog,
    SubjectiveLog,
    SubjectiveQuestionLog,
)
from app.schemas.input_schema import ComprehensionReqPara, QuestionReqPara
from app.schemas.output_schema import (
    ComprehensionQuestionItem,
    QuestionItem,
    OptionLabel,
    FillInTheBlankQuestionItem,
    SubjectiveQuestionItem,
    MarkingScheme,
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
        question=question.question,
        subject=req.subject,
        topic=req.topic,
        question_type="mcq",
        top_k=3,
    )

    check_validation, validation_time, total_input_tokens,total_output_tokens = await validate_questions(
        req, question, similar_questions[1:], add_to_db=False, question_type="mcq"
    )
    return {
        "question_id": res.question_id,
        "validation_score": check_validation.validation_result.score,
        "duplication_chance": check_validation.validation_result.duplication_chance,
        "issues": check_validation.validation_result.issues,
        "similar_questions": similar_questions,
        "validation_time": validation_time,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
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
        question=question.question,
        subject=req.subject,
        topic=req.topic,
        question_type="comprehension",
        top_k=3,
    )

    check_validation, validation_time, total_input_tokens,total_output_tokens = await validate_questions(
        req,
        question,
        similar_questions[1:],
        add_to_db=False,
        is_comprehension=True,
        comprehension_passage=log.paragraph,
        question_type="comprehension",
    )
    return {
        "comprehensive_passage": log.paragraph,
        "question_id": res.question_id,
        "validation_score": check_validation.validation_result.score,
        "duplication_chance": check_validation.validation_result.duplication_chance,
        "issues": check_validation.validation_result.issues,
        "similar_questions": similar_questions,
        "validation_time": validation_time,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
    }


@router.post("/validate-fill-in-the-blank")
async def validate_fill_in_the_blank(question_id: str):
    log = await FillInTheBlankLog.find_one({"questions.question_id": question_id})

    if not log:
        raise HTTPException(status_code=404, detail="Question not found for validation")

    res: FillInTheBlankQuestionLog = [
        q for q in log.questions if q.question_id == question_id
    ][0]
    question = FillInTheBlankQuestionItem(
        question=res.question,
        answer=res.answer,
        acceptable_answers=res.acceptable_answers,
        explanation=res.explanation,
    )

    req: QuestionReqPara = log.request

    print(
        f"\n\n    --->Validating single fill-in-the-blank question {question.question}"
    )

    similar_questions = await search_similar_questions(
        question=question.question,
        subject=req.subject,
        topic=req.topic,
        question_type="fill_in_the_blank",
        top_k=3,
    )

    check_validation, validation_time, total_input_tokens,total_output_tokens = await validate_questions(
        req,
        question,
        similar_questions[1:],
        add_to_db=False,
        question_type="fill_in_the_blank",
    )
    return {
        "question_id": res.question_id,
        "validation_score": check_validation.validation_result.score,
        "duplication_chance": check_validation.validation_result.duplication_chance,
        "issues": check_validation.validation_result.issues,
        "similar_questions": similar_questions,
        "validation_time": validation_time,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
    }


@router.post("/validate-subjective")
async def validate_subjective(question_id: str):
    log = await SubjectiveLog.find_one({"questions.question_id": question_id})

    if not log:
        raise HTTPException(status_code=404, detail="Question not found for validation")

    res: SubjectiveQuestionLog = [
        q for q in log.questions if q.question_id == question_id
    ][0]
    question = SubjectiveQuestionItem(
        question=res.question,
        expected_answer=res.expected_answer,
        marking_scheme=MarkingScheme(**res.marking_scheme),
    )

    req: QuestionReqPara = log.request

    print(f"\n\n    --->Validating single subjective question {question.question}")

    similar_questions = await search_similar_questions(
        question=question.question,
        subject=req.subject,
        topic=req.topic,
        question_type="subjective",
        top_k=3,
    )

    check_validation, validation_time, total_input_tokens,total_output_tokens = await validate_questions(
        req,
        question,
        similar_questions[1:],
        add_to_db=False,
        question_type="subjective",
    )
    return {
        "question_id": res.question_id,
        "validation_score": check_validation.validation_result.score,
        "duplication_chance": check_validation.validation_result.duplication_chance,
        "issues": check_validation.validation_result.issues,
        "similar_questions": similar_questions,
        "validation_time": validation_time,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
    }
