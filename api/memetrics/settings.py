from pydantic import BaseSettings


class Settings(BaseSettings):
    # uvicorn
    MEME_HOST: str = "0.0.0.0"
    MEME_PORT: int = 8000
    MEME_RELOAD: bool = False
    MEME_WORKERS: int = 8

    # mongodb
    MEME_MONGODB_DBNAME: str = "memetrics"
    MEME_MONGODB_URI: str = "mongodb://localhost:27017"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
