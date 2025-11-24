import os
from dotenv import load_dotenv


def load_environment_variables():
    load_dotenv(".env")
    print("Environment variables loaded from .env file.")
    if not os.getenv("MONGO_URI"):
        raise EnvironmentError("MONGO_URI is not set in the environment variables.")
    if not os.getenv("CHROMA_DB_URI"):
        raise EnvironmentError("CHROMA_DB_URI is not set in the environment variables.")
    if not os.getenv("OPEN_ROUTER_API_KEY"):
        raise EnvironmentError("OPEN_ROUTER_API_KEY is not set in the environment variables.")
    if not os.getenv("MONGO_DB"):
        raise EnvironmentError("MONGO_DB is not set in the environment variables.")

