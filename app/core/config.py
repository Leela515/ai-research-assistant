from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    top_k: int = 5
    index_path: str = "library/index"
    model_name: str = "gpt-4o-mini"

    class Config:
        env_file = ".env"

settings = Settings()