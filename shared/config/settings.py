from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Dict, List

class Settings(BaseSettings):
    # API Settings
    PROJECT_NAME: str = "Zem API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENV: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/zem_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # AI Providers
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OPENAI_API_KEY: Optional[str] = None
    HF_API_TOKEN: Optional[str] = None
    MISTRAL_API_KEY: Optional[str] = None
    
    # Reddit API
    REDDIT_CLIENT_ID: Optional[str] = None
    REDDIT_CLIENT_SECRET: Optional[str] = None
    REDDIT_USER_AGENT: str = "ZemMediaEngine/0.1"
    
    # Discovery Settings
    TARGET_SUBREDDITS: List[str] = ["AskReddit", "confessions", "relationship_advice", "talesfromtechsupport"]
    FETCH_LIMIT: int = 25
    
    # Trend Ranking Weights
    UPVOTES_WEIGHT: float = 0.3
    COMMENTS_WEIGHT: float = 0.4
    RECENCY_WEIGHT: float = 0.2
    EMOTIONAL_WEIGHT: float = 0.1
    
    # Quality Thresholds
    MIN_UPVOTES: int = 50
    MIN_COMMENTS: int = 15
    MIN_CONTENT_LENGTH: int = 100
    SIMILARITY_THRESHOLD: float = 85.0
    
    # Default Models
    DEFAULT_FAST_MODEL: str = "mistral"
    DEFAULT_SMART_MODEL: str = "gpt-4o-mini"
    DEFAULT_LOCAL_MODEL: str = "llama3"
    
    # Task-to-Model Routing
    MODEL_ROUTING: Dict[str, str] = {
        "hook_generation": "mistral",
        "script_generation": "openai",
        "validation": "ollama",
        "classification": "huggingface"
    }

    # Audio Storage
    RAW_AUDIO_PATH: str = "assets/audio/raw"
    PROCESSED_AUDIO_PATH: str = "assets/audio/processed"
    ARCHIVE_PATH: str = "assets/audio/archived"
    TEMP_AUDIO_PATH: str = "assets/audio/temp"

    # Retention Policies
    RETENTION_TEMP_HOURS: int = 24
    RETENTION_FAILED_DAYS: int = 7
    RETENTION_ARCHIVE_DAYS: int = 30
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
