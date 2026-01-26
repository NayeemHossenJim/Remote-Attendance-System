import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./attendance.db")
    
    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-use-env-variable")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Password Reset
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 24
    
    # Check-in Time Window
    CHECK_IN_START_HOUR: int = 8
    CHECK_IN_START_MINUTE: int = 0
    CHECK_IN_END_HOUR: int = 9
    CHECK_IN_END_MINUTE: int = 30
    
    # Default Location Radius
    DEFAULT_RADIUS_METERS: int = 50
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
