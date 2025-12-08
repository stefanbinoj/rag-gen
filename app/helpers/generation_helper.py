import time
from typing import List
from pydantic import BaseModel
from app.deps import get_llm_client
from app.schemas.input_schema import ComprehensionReqPara, QuestionReqPara
from app.schemas.output_schema import ComprehensionQuestionItem, QuestionItem, FillInTheBlankQuestionItem, SubjectiveQuestionItem
from app.helpers.db_helper import get_model_name, get_prompt


class QuestionsList(BaseModel):
    questions: List[QuestionItem]


class ComprehensionQuestionsList(BaseModel):
    questions: List[ComprehensionQuestionItem]


class FillInTheBlankQuestionsList(BaseModel):
    questions: List[FillInTheBlankQuestionItem]


class SubjectiveQuestionsList(BaseModel):
    questions: List[SubjectiveQuestionItem]


async def generate_questions(
    state: QuestionReqPara | ComprehensionReqPara,
    is_comprehension: bool = False,
    comprehension_passage: str | None = None,
    is_fill_blank: bool = False,
    is_subjective: bool = False,
) -> tuple[List[QuestionItem] | List[ComprehensionQuestionItem] | List[FillInTheBlankQuestionItem] | List[SubjectiveQuestionItem], float, int, int]:
    start_time = time.time()
    model_name = await get_model_name("generation")
    llm = get_llm_client(model_name)

    # Determine system prompt based on question type
    if is_subjective:
        system_prompt_name = "subjective_generation"
    elif is_fill_blank:
        system_prompt_name = "fill_blank_generation"
    elif is_comprehension:
        system_prompt_name = "comprehensive_question_generation"
    else:
        system_prompt_name = "generation"
    
    system_prompt = await get_prompt(system_prompt_name)
    
    # Enforce language in system prompt
    system_prompt += f"\n\n**LANGUAGE REQUIREMENT:** All content MUST be generated in {state.language}. Questions, options, explanations, and all text must strictly be in {state.language} language."
    
    # Add special_instructions to system prompt if present
    if state.special_instructions:
        system_prompt += f"\n\n**SPECIAL INSTRUCTIONS FROM USER (HIGHEST PRIORITY):**\n{state.special_instructions}"

    # Choose the appropriate structured output model
    if is_subjective:
        model_with_structure = llm.with_structured_output(SubjectiveQuestionsList, include_raw=True)
    elif is_fill_blank:
        model_with_structure = llm.with_structured_output(FillInTheBlankQuestionsList, include_raw=True)
    elif is_comprehension:
        model_with_structure = llm.with_structured_output(ComprehensionQuestionsList, include_raw=True)
    else:
        model_with_structure = llm.with_structured_output(QuestionsList, include_raw=True)
    # Build separate user messages for normal vs comprehensive generation
    user_message_normal = f"""
Generate {state.no_of_questions} MCQs.
{f"Age: {state.age} | " if state.age else ""}Subject: {state.subject} | Topic: {state.topic}
Stream: {state.stream} | Country: {state.country} | Difficulty: {state.difficulty.value}
Language: {state.language}
{f"Sub-topic: {state.sub_topic}" if state.sub_topic else ""}

Instructions:
- Produce {state.no_of_questions} distinct MCQs with 4 options (A-D).
- Provide one correct option, and a brief explanation for the correct answer.
- Don't use any emojis and always ensure passage is in {state.country} respective context.
- CRITICAL: All content MUST be in {state.language} language.
{f"\n\nSPECIAL INSTRUCTIONS (MUST FOLLOW): {state.special_instructions}" if state.special_instructions else ""}
"""

    user_message_comprehensive = f"""
Generate {state.no_of_questions} MCQs based on the provided comprehension passage.
{f"Age: {state.age} | " if state.age else ""}Subject: {state.subject} | Topic: {state.topic}
Stream: {state.stream} | Country: {state.country} | Difficulty: {state.difficulty.value}
Language: {state.language}
{f"Sub-topic: {state.sub_topic}" if state.sub_topic else ""}

{f"Comprehension Passage: {comprehension_passage}" if is_comprehension else "N/A"}

Instructions:
- Generate {state.no_of_questions} MCQs that are answerable from the passage above.
- Use explicit references to the passage where appropriate (e.g., "According to the passage...").
- Provide 4 options (A-D), mark the correct option, and include a concise explanation referencing the passage.
- Don't use any emojis and always ensure passage is in {state.country} respective context.
- CRITICAL: All content MUST be in {state.language} language.
{f"\n\nSPECIAL INSTRUCTIONS (MUST FOLLOW): {state.special_instructions}" if state.special_instructions else ""}
"""

    user_message_fill_blank = f"""
Generate {state.no_of_questions} fill-in-the-blank questions.
{f"Age: {state.age} | " if state.age else ""}Subject: {state.subject} | Topic: {state.topic}
Stream: {state.stream} | Country: {state.country} | Difficulty: {state.difficulty.value}
Language: {state.language}
{f"Sub-topic: {state.sub_topic}" if state.sub_topic else ""}

Instructions:
- Produce {state.no_of_questions} distinct fill-in-the-blank questions with exactly ONE blank per question (use _____).
- Provide the correct answer and any acceptable alternative answers.
- Include a brief explanation for the correct answer.
- Don't use any emojis and always ensure content is in {state.country} respective context.
- CRITICAL: All content MUST be in {state.language} language.
{f"\n\nSPECIAL INSTRUCTIONS (MUST FOLLOW): {state.special_instructions}" if state.special_instructions else ""}
"""

    user_message_subjective = f"""
Generate {state.no_of_questions} subjective questions.
{f"Age: {state.age} | " if state.age else ""}Subject: {state.subject} | Topic: {state.topic}
Stream: {state.stream} | Country: {state.country} | Difficulty: {state.difficulty.value}
Language: {state.language}
{f"Sub-topic: {state.sub_topic}" if state.sub_topic else ""}

Instructions:
- Produce {state.no_of_questions} distinct subjective questions requiring detailed explanatory answers.
- Provide a comprehensive expected answer showing all steps/reasoning.
- Include a detailed marking scheme with specific criteria and mark allocation.
- Don't use any emojis and always ensure content is in {state.country} respective context.
- CRITICAL: All content MUST be in {state.language} language.
{f"\n\nSPECIAL INSTRUCTIONS (MUST FOLLOW): {state.special_instructions}" if state.special_instructions else ""}
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
    total_input = result["raw"].response_metadata["token_usage"]["prompt_tokens"]
    total_output = result["raw"].response_metadata["token_usage"]["completion_tokens"]
    parsed = result["parsed"]
    # Extract questions from the result
    if isinstance(parsed, (QuestionsList, ComprehensionQuestionsList, FillInTheBlankQuestionsList, SubjectiveQuestionsList)):
        questions = parsed.questions
    else:
        # Fallback for unexpected formats
        print(f"Unexpected result type: {type(result)}")
        raise ValueError("Failed to parse generated questions.")

    generation_time = time.time() - start_time
    return questions, generation_time, total_input, total_output
