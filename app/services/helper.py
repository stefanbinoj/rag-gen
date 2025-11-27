
import json
from app.schemas.models import Model, Prompt



async def get_model_name(type: str):
    models = await Model.find_one()

    if not models:
        raise ValueError("No model configuration found in the database.")

    if type == "generation":
        return models.generation_model
    else:
        return models.validation_model


async def get_prompt(type: str):
    prompt = await Prompt.find_one(Prompt.name == type)

    if not prompt:
        raise ValueError(f"No prompt found for type: {type}")

    return prompt.content


def _extract_metadata(
    llm_result: dict, expected_questions: int
) -> tuple[list, int, float]:
    """
    Extract parsed questions, token usage, and cost from LLM response.

    Structure of llm_result with include_raw=True:
    {
        'parsing_type': 'langchain_structured',
        'raw': {
            'content': '...',
            'usage_metadata': {
                'input_tokens': int,
                'output_tokens': int,
                'total_tokens': int
            },
            'response_metadata': {
                'cost': float
            }
        },
        'parsed': [QuestionItem, ...]
    }

    Args:
        llm_result: Raw result from LLM with include_raw=True
        expected_questions: Expected number of questions

    Returns:
        Tuple of (questions, tokens_used, cost)
    """
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

