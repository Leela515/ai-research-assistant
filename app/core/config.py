from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    top_k: int = 5
    index_path: str = "library/index"
    model_name: str = "gpt-4o-mini"

    min_relevance_score: float = 0.40

    class Config:
        env_file = ".env"

settings = Settings()