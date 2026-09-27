import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Multi-Agent AI Research System"
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./research.db")
    MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS", "3"))
    CRITIC_MIN_SCORE: int = int(os.getenv("CRITIC_MIN_SCORE", "7"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
