import time
from typing import Optional, cast
from app.deps import get_llm_client
from app.schemas.input_schema import QuestionReqPara, ComprehensionReqPara
from app.schemas.output_schema import ComprehensionQuestionItem, ComprehensionType, FillInTheBlankQuestionItem, QuestionItem, SubjectiveQuestionItem, ValidationNodeReturn
from app.helpers.db_helper import get_model_name, get_prompt


async def regenerate_question(
    req: QuestionReqPara | ComprehensionReqPara,
    question: QuestionItem | ComprehensionQuestionItem | FillInTheBlankQuestionItem | SubjectiveQuestionItem,
    validation_result: ValidationNodeReturn,
    temperature: float = 0.3,
    is_comprehension: bool = False,
    comprehension_passage: str | None = None,
    is_fill_blank: bool = False,
    is_subjective: bool = False,
) -> tuple[QuestionItem | FillInTheBlankQuestionItem | SubjectiveQuestionItem, float, int,int]:
    start_time = time.time()
    comprehension_type: Optional[ComprehensionType]= None
    if is_comprehension:
        question = cast(ComprehensionQuestionItem, question)
        comprehension_type = question.comprehension_type

    model_name = await get_model_name("generation")
    llm = get_llm_client(model_name, temperatur=temperature)

    # Determine system prompt based on question type
    if is_subjective:
        system_prompt_name = "subjective_regeneration"
    elif is_fill_blank:
        system_prompt_name = "fill_blank_regeneration"
    elif is_comprehension:
        system_prompt_name = "comprehensive_question_regeneration"
    else:
        system_prompt_name = "regeneration"
    
    system_prompt = await get_prompt(system_prompt_name)
    
    # Enforce language in system prompt
    system_prompt += f"\n\n**LANGUAGE REQUIREMENT:** All regenerated content MUST be in {req.language}. Questions, options, explanations, and all text must strictly be in {req.language} language."
    
    # Add special_instructions to system prompt if present
    if req.special_instructions:
        system_prompt += f"\n\n**SPECIAL INSTRUCTIONS FROM USER (HIGHEST PRIORITY - Must be followed in regenerated question):**\n{req.special_instructions}"

    # Choose the appropriate structured output model
    if is_subjective:
        model_with_structure = llm.with_structured_output(SubjectiveQuestionItem, include_raw=True)
    elif is_fill_blank:
        model_with_structure = llm.with_structured_output(FillInTheBlankQuestionItem, include_raw=True)
    else:
        model_with_structure = llm.with_structured_output(QuestionItem, include_raw=True)
    # Create different user messages for normal vs comprehension regeneration
    user_message_subjective = f"""
REGENERATION TASK - Subjective Question
----------------------------------------
ORIGINAL REQUIREMENTS:
Subject: {req.subject}
Topic: {req.topic}
Sub-topic: {req.sub_topic if req.sub_topic else "N/A"}
Difficulty: {req.difficulty.value}
Stream: {req.stream.value}
Country: {req.country}
Language: {req.language}
Age Group: {req.age if req.age else "N/A"}

FAULTY QUESTION:
Question: {question.question}
Expected Answer: {cast(SubjectiveQuestionItem, question).expected_answer if is_subjective else "N/A"}
Marking Scheme: {cast(SubjectiveQuestionItem, question).marking_scheme.model_dump() if is_subjective else "N/A"}

VALIDATION FEEDBACK:
Score: {validation_result.validation_result.score}
Duplication Chance: {validation_result.validation_result.duplication_chance}
Issues: {", ".join(validation_result.validation_result.issues)}

Please regenerate a single clear, comprehensive subjective question that addresses the issues above. Keep format consistent.
- Don't use any emojis and always ensure content is in {req.country} respective context.
- CRITICAL: All content MUST be in {req.language} language.
{f"\n\nSPECIAL INSTRUCTIONS (MUST FOLLOW): {req.special_instructions}" if req.special_instructions else ""}
"""

    user_message_fill_blank = f"""
REGENERATION TASK - Fill-in-the-Blank Question
-----------------------------------------------
ORIGINAL REQUIREMENTS:
Subject: {req.subject}
Topic: {req.topic}
Sub-topic: {req.sub_topic if req.sub_topic else "N/A"}
Difficulty: {req.difficulty.value}
Stream: {req.stream.value}
Country: {req.country}
Language: {req.language}
Age Group: {req.age if req.age else "N/A"}

FAULTY QUESTION:
Question: {question.question}
Answer: {cast(FillInTheBlankQuestionItem, question).answer if is_fill_blank else "N/A"}
Acceptable Answers: {cast(FillInTheBlankQuestionItem, question).acceptable_answers if is_fill_blank else "N/A"}
Explanation: {cast(FillInTheBlankQuestionItem, question).explanation if is_fill_blank else "N/A"}

VALIDATION FEEDBACK:
Score: {validation_result.validation_result.score}
Duplication Chance: {validation_result.validation_result.duplication_chance}
Issues: {", ".join(validation_result.validation_result.issues)}

Please regenerate a single clear, unambiguous fill-in-the-blank question that addresses the issues above. Keep format consistent.
- Don't use any emojis and always ensure content is in {req.country} respective context.
- CRITICAL: All content MUST be in {req.language} language.
{f"\n\nSPECIAL INSTRUCTIONS (MUST FOLLOW): {req.special_instructions}" if req.special_instructions else ""}
"""

    user_message_normal = f"""
REGENERATION TASK - Normal MCQ
-----------------------------
ORIGINAL REQUIREMENTS:
Subject: {req.subject}
Topic: {req.topic}
Sub-topic: {req.sub_topic if req.sub_topic else "N/A"}
Difficulty: {req.difficulty.value}
Stream: {req.stream.value}
Country: {req.country}
Language: {req.language}
Age Group: {req.age if req.age else "N/A"}

FAULTY QUESTION:
Question: {question.question}
Options: {cast(QuestionItem, question).options if not is_fill_blank and not is_subjective else "N/A"}
Correct Option: {cast(QuestionItem, question).correct_option if not is_fill_blank and not is_subjective else "N/A"}
Explanation: {cast(QuestionItem | FillInTheBlankQuestionItem, question).explanation if not is_subjective else "N/A"}

VALIDATION FEEDBACK:
Score: {validation_result.validation_result.score}
Duplication Chance: {validation_result.validation_result.duplication_chance}
Issues: {", ".join(validation_result.validation_result.issues)}

Please regenerate a single clear, unambiguous MCQ that addresses the issues above. Keep format consistent.
- Don't use any emojis and always ensure passage is in {req.country} respective context.
- CRITICAL: All content MUST be in {req.language} language.
{f"\n\nSPECIAL INSTRUCTIONS (MUST FOLLOW): {req.special_instructions}" if req.special_instructions else ""}
"""

    user_message_comprehensive = f"""
REGENERATION TASK - Comprehension-based MCQ
-------------------------------------------
ORIGINAL REQUIREMENTS:
Subject: {req.subject}
Topic: {req.topic}
Sub-topic: {req.sub_topic if req.sub_topic else "N/A"}
Difficulty: {req.difficulty.value}
Stream: {req.stream.value}
Country: {req.country}
Language: {req.language}
Age Group: {req.age if req.age else "N/A"}

COMPREHENSION PASSAGE:
{comprehension_passage if is_comprehension else "N/A"}
QUESTION TYPE: {comprehension_type.value if comprehension_type else "N/A"}

FAULTY QUESTION:
Question: {question.question}
Options: {cast(ComprehensionQuestionItem, question).options if is_comprehension else "N/A"}
Correct Option: {cast(ComprehensionQuestionItem, question).correct_option if is_comprehension else "N/A"}
Explanation: {cast(ComprehensionQuestionItem, question).explanation if is_comprehension else "N/A"}

VALIDATION FEEDBACK:
Score: {validation_result.validation_result.score}
Duplication Chance: {validation_result.validation_result.duplication_chance}
Issues: {", ".join(validation_result.validation_result.issues)}

Please regenerate the question so that the correct answer is directly supported by the passage. Avoid ambiguity and ensure distractors are plausible but clearly incorrect when compared with the passage.
- Don't use any emojis and always ensure passage is in {req.country} respective context.
- CRITICAL: All content MUST be in {req.language} language.
{f"\n\nSPECIAL INSTRUCTIONS (MUST FOLLOW): {req.special_instructions}" if req.special_instructions else ""}
"""

    # Select the appropriate user message
    if is_subjective:
        user_message = user_message_subjective
    elif is_fill_blank:
        user_message = user_message_fill_blank
    elif is_comprehension:
        user_message = user_message_comprehensive
    else:
        user_message = user_message_normal

    result = model_with_structure.invoke(
        [
            ("system", system_prompt),
            ("user", user_message),
        ]
    )

    generation_time = time.time() - start_time
    total_input = result["raw"].response_metadata["token_usage"]["prompt_tokens"]
    total_output = result["raw"].response_metadata["token_usage"]["completion_tokens"]
    parsed = result["parsed"]

    if isinstance(parsed, (QuestionItem, ComprehensionQuestionItem, FillInTheBlankQuestionItem, SubjectiveQuestionItem)):
        questions = parsed
    else:
        print(f"Unexpected result type: {type(result)}")
        raise ValueError("Failed to parse generated questions.")

    return questions, generation_time, total_input, total_output

