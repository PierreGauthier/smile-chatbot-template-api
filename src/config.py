from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    project_name:str = "scht"
    environment: str = "local"
    debug: bool = False
    
    cors_allowed_origins: Optional[str] = "*"
    
    class Config:
        env_file = ".env.Staging"
        env_file_encoding = 'utf-8'

#@lru_cache
def get_settings():
    return Settings()