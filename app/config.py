from pydantic_settings import BaseSettings, SettingsConfigDict
import os

ENV_FILE = os.getenv("ENV_FILE", ".env.local")

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        extra="ignore"
    )

settings = Settings()
