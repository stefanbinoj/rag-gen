import os
from motor.motor_asyncio import AsyncIOMotorClient
import chromadb
from langchain_openai import ChatOpenAI

_mongo_client = None
_mongo_db = None


def get_mongo_db():
    global _mongo_client, _mongo_db
    if _mongo_client is None or _mongo_db is None:
        _mongo_client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
        _mongo_db = _mongo_client[os.getenv("MONGO_DB")]  # pyright: ignore[reportArgumentType]
    return _mongo_db


_llm_client = None


def get_llm_client(model_name: str) -> ChatOpenAI:
    global _llm_client
    if _llm_client is None:
        _llm_client = ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            model=model_name,
        )
    return _llm_client


_chroma_client = None


def get_chroma_client():
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.Client()
    return _chroma_client
