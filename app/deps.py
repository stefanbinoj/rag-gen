import os
from functools import lru_cache
from motor.motor_asyncio import AsyncIOMotorClient

#import chromadb
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
#
#
# _client = None
#
#
# def get_chroma_client():
#     global _client
#     if _client is None:
#         _client = chromadb.CloudClient(
#             api_key=os.getenv("CHROMA_API_KEY"),
#             tenant=os.getenv("CHROMA_TENANT"),
#             database=os.getenv("CHROMA_DATABASE"),
#         )
#     return _client
