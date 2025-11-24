from fastapi import Depends, HTTPException
from typing import Generator
from pymongo import MongoClient
from app.core.config import settings

mongo_client = MongoClient(settings.MONGO_URI)

def get_db() -> Generator:
    db = create_session(settings.DATABASE_URL)
    try:
        yield db
    finally:
        db.close()


def get_mongo_db():
    """Returns the DB object."""
    return mongo_client[settings.MONGO_DB]
