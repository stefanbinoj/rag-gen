import os
from motor.motor_asyncio import AsyncIOMotorClient
import chromadb
from langchain_openai import ChatOpenAI
from app.helpers.langfuse_helper import get_langfuse_handler

_mongo_client = None
_mongo_db = None


def get_mongo_db():
    global _mongo_client, _mongo_db
    if _mongo_client is None or _mongo_db is None:
        _mongo_client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
        _mongo_db = _mongo_client[os.getenv("MONGO_DB")]  # pyright: ignore[reportArgumentType]
    return _mongo_db


_llm_clients = {}


def get_llm_client(model_name: str, temperatur: float = 0) -> ChatOpenAI:
    """
    Get or create a cached LLM client for the given model and temperature.
    Caches clients per unique model+temperature combination to avoid auth errors.
    """
    global _llm_clients
    cache_key = f"{model_name}:{temperatur}"
    
    if cache_key not in _llm_clients:
        langfuse_handler = get_langfuse_handler()
        _llm_clients[cache_key] = ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            model=model_name,
            temperature=temperatur,
            api_key=os.environ["OPENAI_API_KEY"], # pyright: ignore[reportArgumentType]
            callbacks=[langfuse_handler],
        )
    return _llm_clients[cache_key]


_chroma_client = None


def get_chroma_client():
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.CloudClient(
            api_key=os.getenv("CHROMA_API_KEY"),
            tenant=os.getenv("CHROMA_TENANT"),
            database=os.getenv("CHROMA_DATABASE"),
        )
    return _chroma_client
