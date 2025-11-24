import os
from fastapi import  HTTPException
from typing import Generator, Any
from pymongo import MongoClient

def get_mongo_db() -> Generator[Any, None, None]:
    client = MongoClient(os.getenv("MONGO_URI"))
    try:
        print("Successfully connected to MongoDB")
        yield client[os.getenv("MONGO_DB")]  # pyright: ignore[reportArgumentType]
    except Exception as e:
        print(f"Connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")
    finally:
        client.close()
