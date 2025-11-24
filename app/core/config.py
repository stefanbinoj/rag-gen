from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Question Generator"
    DEBUG: bool = False

    # MongoDB
    MONGO_URI: str
    MONGO_DB: str = "questions_db"

    # Vector DB
    VECTOR_DB_URL: str | None = None

    # AI config example
    OPENAI_API_KEY: str | None = None

    class Config:
        env_file = ".env"  # loads automatically

settings = Settings()

