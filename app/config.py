import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'change-me')
    DEBUG: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    APP_TITLE: str = os.getenv('APP_TITLE', 'Apartment Hub')
    OLLAMA_API_URL: str = os.getenv('OLLAMA_API_URL', 'http://ollama:11434')
    LLM_MODEL_NAME: str = os.getenv('LLM_MODEL_NAME', 'tinyllama')
    LLM_DAILY_LIMIT: int = int(os.getenv('LLM_DAILY_LIMIT', '10'))
    MAX_FILE_SIZE_MB: int = int(os.getenv('MAX_FILE_SIZE_MB', '100'))
    MAX_STORAGE_MB: int = int(os.getenv('MAX_STORAGE_MB', '5000'))
    UPLOAD_DIR: str = os.getenv('UPLOAD_DIR', '/uploads')
    BACKUP_DIR: str = os.getenv('BACKUP_DIR', '/backups')
    DATABASE_PATH: str = os.getenv('DATABASE_PATH', '/app/data/apartment_hub.db')
    ACCESS_TOKEN_EXPIRE_DAYS: int = 30

settings = Settings()
