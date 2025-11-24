import os
from functools import lru_cache
from motor.motor_asyncio import AsyncIOMotorClient


@lru_cache()
def get_mongo_db():
    """Return a cached Motor DB instance.

    Caches the DB object so an AsyncIOMotorClient is created only once
    (on first call). Use this with FastAPI's `Depends` to get the DB.
    """
    client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("MONGO_DB")] #pyright: ignore[reportArgumentType]
    return db

