import os
from dotenv import load_dotenv

from app.schemas.output_schema import ComprehensionType


def load_environment_variables():
    load_dotenv(".env")
    print("Environment variables loaded from .env file.")
    if not os.getenv("MONGO_URI"):
        raise EnvironmentError("MONGO_URI is not set in the environment variables.")
    if not os.getenv("MONGO_DB"):
        raise EnvironmentError("MONGO_DB is not set in the environment variables.")
    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError(
            "OPEN_ROUTER_API_KEY is not set in the environment variables. Please pass open router API key here."
        )
    if not os.getenv("CHROMA_API_KEY"):
        raise EnvironmentError(
            "CHROMA_API_KEY is not set in the environment variables."
        )
    if not os.getenv("CHROMA_TENANT"):
        raise EnvironmentError("CHROMA_TENANT is not set in the environment variables.")
    if not os.getenv("CHROMA_DATABASE"):
        raise EnvironmentError(
            "CHROMA_DATABASE is not set in the environment variables."
        )


DUPLICATE_THRESHOLD = 0.4
SCORE_THRESHOLD = 0.7
MAX_RETRIES = 3

weights = {
    ComprehensionType.direct_retrieval.value: 0.25,
    ComprehensionType.inference_questions.value: 0.25,
    ComprehensionType.vocabulary_meaning.value: 0.10,
    ComprehensionType.summary.value: 0.10,
    ComprehensionType.author_intent.value: 0.10,
    ComprehensionType.character_analysis.value: 0.10,
    ComprehensionType.evidence_based_reasoning.value: 0.10,
}
