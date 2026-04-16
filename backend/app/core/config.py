from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os
import sys

class Settings(BaseSettings):
    PROJECT_NAME: str = "Parroquia Records System"
    API_V1_STR: str = "/api/v1"
    
    POSTGRES_SERVER: str = "127.0.0.1"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "123456"
    POSTGRES_DB: str = "parroquia_db"
    
    @property
    def BASE_DATA_DIR(self) -> str:
        if getattr(sys, 'frozen', False):
            app_data = os.getenv('APPDATA')
            base_dir = os.path.join(app_data, "SistemaParroquia")
            if not os.path.exists(base_dir):
                os.makedirs(base_dir)
            return base_dir
        return os.path.abspath(".")

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"sqlite:///{os.path.join(self.BASE_DATA_DIR, 'parroquia.db')}"

    # Security
    SECRET_KEY: str = "parroquia-secret-key-2025"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30 # 30 days

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
