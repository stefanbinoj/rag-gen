import os
from functools import lru_cache
from motor.motor_asyncio import AsyncIOMotorClient

import chromadb
from langchain_openai import ChatOpenAI


@lru_cache()
def get_mongo_db():
    """Return a cached Motor DB instance.

    Caches the DB object so an AsyncIOMotorClient is created only once
    (on first call). Use this with FastAPI's `Depends` to get the DB.
    """
    client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("MONGO_DB")]  # pyright: ignore[reportArgumentType]
    return db


def get_llm_client(model_name: str) -> ChatOpenAI:
    llm = ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        model=model_name,
    )
    return llm


_chroma_client = None


def get_chroma_client():
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.Client()
    return _chroma_client
