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
        # Guardar siempre en Documentos/Datos Parroquia para fácil respaldo por la secretaria
        documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        base_dir = os.path.join(documents_path, "Datos Parroquia")
        if not os.path.exists(base_dir):
            try:
                os.makedirs(base_dir)
            except Exception:
                pass
        
        # En caso de error, el fallback es la carpeta actual
        if not os.path.exists(base_dir):
            return os.path.abspath(".")
        return base_dir

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"sqlite:///{os.path.join(self.BASE_DATA_DIR, 'parroquia.db')}"

    # Security
    SECRET_KEY: str = "parroquia-secret-key-2025"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30 # 30 days

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # Correos (SMTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "sistemas.parroquial.sb@gmail.com"
    SMTP_PASSWORD: str = "kidzrxpykrmoztsp"
    SMTP_TLS: bool = True
    EMAILS_FROM_EMAIL: str = "sistemas.parroquial.sb@gmail.com"
    EMAILS_FROM_NAME: str = "Parroquia Dulce Nombre"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
