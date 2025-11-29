from fastapi import APIRouter, HTTPException
from app.schemas.output_schema import ValidationNodeReturn
from app.schemas.input_schema import QuestionReqPara, ComprehensionReqPara
from app.schemas.mongo_models import GenerationLog, QuestionLog

from app.services.generation_helper import generate_questions
from app.services.regeneration_helper import regenerate_question
from app.services.validation_helper import validate_questions
from app.services.chroma_helper import search_similar_questions

router = APIRouter()


@router.post(
    "/generate-questions",
    responses={
        201: {"description": "Questions generated successfully"},
        422: {"description": "Invalid input"},
    },
)
async def generate_questions_endpoint(req: QuestionReqPara):
    # GENERATION NODE
    generated_questions, generation_time = await generate_questions(req)
    print(
        f"Generated {len(generated_questions)} Generation time: {generation_time:.2f} seconds"
    )
    # VALIDATION NODE
    validated_results: list[ValidationNodeReturn] = []
    for idx, question in enumerate(generated_questions):
        similar_questions = await search_similar_questions(
            question=question, subject=req.subject, topic=req.topic, top_k=3
        )

        check_validation: ValidationNodeReturn = await validate_questions(
            req, question, similar_questions
        )

        print(f"\n\n    --->Validating question {idx + 1}")
        print(f"Generated Question: {question.question}")
        print(f"score: {check_validation.validation_result.score}, duplication chance: {check_validation.validation_result.duplication_chance}")
        print(f"Took time: {check_validation.validation_time:.2f} seconds")
        print(
            f"--->validation issues : {check_validation.validation_result.issues}"
        )
        if not check_validation.added_to_vectordb:
            print(
                f"XXX Question not added to ChromaDB due to low score ({check_validation.validation_result.score}) or high duplication chance ({check_validation.validation_result.duplication_chance})"
            )
        else :
            print(
                f"||| Question added to ChromaDB with score {check_validation.validation_result.score} and duplication chance {check_validation.validation_result.duplication_chance}"
            )
        validated_results.append(check_validation)
        validated_results[idx].retries = 1

    # REGENERATION NODE
    for idx, result in enumerate(validated_results):
        if not result.added_to_vectordb:
            regenerated_question , regeneration_time = await regenerate_question(
                req, generated_questions[idx], result
            )
            print(f"\n\n    --->Regenerating question {idx + 1}")
            print(f"Original Question: {generated_questions[idx].question}")
            print(f"Regenerated Question: {regenerated_question.question}")
            print(f"Regeneration took time: {regeneration_time:.2f} seconds")

            similar_questions = await search_similar_questions(
                question=regenerated_question,
                subject=req.subject,
                topic=req.topic,
                top_k=3,
            )

            check_regeneration_validation: ValidationNodeReturn = (
                await validate_questions(req, regenerated_question, similar_questions)
            )
            print(f"score: {check_regeneration_validation.validation_result.score}, duplication chance: {check_regeneration_validation.validation_result.duplication_chance} ")
            print(
                f"--->validation-for-regeneration issues : {check_regeneration_validation.validation_result.issues}"
            )
            print(f"Took time: {check_regeneration_validation.validation_time:.2f} seconds")
            if not check_regeneration_validation.added_to_vectordb:
                print(
                    f"XXX Regenerated question not added to ChromaDB due to low score ({check_regeneration_validation.validation_result.score}) or high duplication chance ({check_regeneration_validation.validation_result.duplication_chance})"
                )
            else :
                print(
                    f"||| Regenerated question added to ChromaDB with score {check_regeneration_validation.validation_result.score} and duplication chance {check_regeneration_validation.validation_result.duplication_chance}"
                )
            validated_results[idx] = check_regeneration_validation
            validated_results[idx].retries = 2
            generated_questions[idx] = regenerated_question

    print(
        f"\n\n------Validation and generation completed for all {len(validated_results)} questions------\n\n"
    )

    # Save to MongoDB
    question_logs = []
    for q, v in zip(generated_questions, validated_results):
        question_logs.append(
            QuestionLog(
                question=q.question,
                options=q.options,
                correct_option=q.correct_option.value,
                explanation=q.explanation,
                validation_score=v.validation_result.score,
                duplication_chance=v.validation_result.duplication_chance,
                issues=v.validation_result.issues,
                retries=v.retries,
                chroma_id=v.uuid,
                total_time=v.validation_time + generation_time,
                similar_questions=v.similar_section,
            )
        )

    log = GenerationLog(
        request=req, questions=question_logs, total_questions=len(question_logs)
    )
    await log.insert()

    for i, question in enumerate(generated_questions):
        generated_questions[i].id = validated_results[i].uuid

    return generated_questions


@router.post("/passive_paragraph")
async def passive(req: ComprehensionReqPara):
    return {"status": "To be implemented"}


@router.get("/questions/{id}")
async def read_question(id: str):
    log = await GenerationLog.find_one({"questions.chroma_id": id})

    if not log:
        raise HTTPException(status_code=404, detail="Question not found")

    res: QuestionLog = [q for q in log.questions if q.chroma_id == id][0]

    return {
        "question": res.question,
        "options": res.options,
        "correct_option": res.correct_option,
        "explanation": res.explanation,
        "_id": res.chroma_id,
    }
