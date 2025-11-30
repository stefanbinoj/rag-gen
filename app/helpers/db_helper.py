
import json
from app.schemas.mongo_models import Model, Prompt



async def get_model_name(type: str) -> str:
    models = await Model.find_one()

    if not models:
        raise ValueError("No model configuration found in the database.")

    if type == "generation":
        return models.generation_model
    elif type == "validation":
        return models.validation_model
    else:
        return "openai/gpt-5-mini"


async def get_prompt(type: str):
    prompts = await Prompt.find_one()

    if not prompts:
        raise ValueError("No prompt configuration found in the database.")

    if type == "generation":
        return prompts.generation_prompt
    elif type == "regeneration":
        return prompts.regeneration_prompt
    elif type == "validation":
        return prompts.validation_prompt
    elif type == "comprehension":
        return prompts.comprehensive_generation_prompt
    elif type == "comprehensive_question_generation":
        return prompts.comprehensive_question_generation_prompt
    elif type == "comprehensive_question_validation":
        return prompts.comprehensive_question_validation_prompt
    elif type == "comprehensive_question_regeneration":
        return prompts.comprehensive_question_regeneration_prompt
    else:
        raise ValueError(f"Unknown prompt type: {type}")


def _extract_metadata(
    llm_result: dict, expected_questions: int
) -> tuple[list, int, float]:

    questions: list = []
    tokens_used: int = 0
    cost: float = 0.0

    try:
        # Extract parsed questions
        if isinstance(llm_result, dict) and "parsed" in llm_result:
            parsed = llm_result.get("parsed", [])
            print(f"Parsed type: {type(parsed)}")
            if isinstance(parsed, list):
                questions = parsed

        if isinstance(llm_result, dict) and "raw" in llm_result:
            raw_output = llm_result.get("raw", {})

            # Get usage metadata
            usage_metadata = raw_output.get("usage_metadata", {})
            print(f"Usage metadata type: {type(usage_metadata)}")
            print(f"Usage metadata content: {usage_metadata}")

            if usage_metadata:
                print(f"Token Usage:{usage_metadata.get('total_tokens', 0)}")
                print(f"  - Input tokens: {usage_metadata.get('input_tokens', 0)}")
                print(f"  - Output tokens: {usage_metadata.get('output_tokens', 0)}")
                print(f"  - Total tokens: {tokens_used}")

            # Get cost metadata
            response_metadata = raw_output.get("response_metadata", {})
            if response_metadata:
                cost = response_metadata.get("cost", 0.0)
                print(f"Cost: ${cost:.6f}")

        # Validate question count
        if len(questions) != expected_questions:
            print(
                f"Warning: Expected {expected_questions} questions, got {len(questions)}"
            )

        # Debug: Print extracted structure
        print("\nExtracted Metadata:")
        print(f"  - Questions parsed: {len(questions)}")
        print(f"  - Tokens used: {tokens_used}")
        print(f"  - Cost: ${cost:.6f}")

    except Exception as e:
        print(f"Error extracting metadata: {e}")
        print(f"Raw result type: {type(llm_result)}")
        print(f"Raw result: {json.dumps(llm_result, indent=2, default=str)}")

        # Fallback: try direct extraction
        if isinstance(llm_result, list):
            questions = llm_result

    return questions, tokens_used, cost

