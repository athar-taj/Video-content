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
    SARVAM_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = "AIzaSyCjGaF7_UffyKcSYKaseFTiGyrVsaaBKMA"
    ELEVENLABS_API_KEY: Optional[str] = "4fcf3611fefbdeb3fa21e2844a2038a36cf595e97ba80f74cf3e2528b7e1c247"
    MURF_API_KEY: Optional[str] = "ap2_284b65bf-5367-4f02-b5b2-541f6c535a8c"
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    KOKORO_MODEL_PATH: Optional[str] = None
    FFMPEG_BINARY: str = "ffmpeg"
    LANGGRAPH_CHECKPOINT_BACKEND: str = "redis"

    # Provider Activation Flags
    ENABLE_OPENAI: bool = True
    ENABLE_CLAUDE: bool = True
    ENABLE_MURF: bool = True
    ENABLE_OLLAMA: bool = True
    ENABLE_KOKORO: bool = True
    ENABLE_SARVAM: bool = True
    ENABLE_HF: bool = True
    ENABLE_GEMINI: bool = False
    ENABLE_MISTRAL: bool = True
    ENABLE_TWITTER: bool = True
    ENABLE_TWIKIT: bool = True
    ENABLE_SNSCRAPE: bool = True
    ENABLE_GPU_RENDERING: bool = False
    MAX_RENDER_WORKERS: int = 2

    # Twitter API v2 Credentials
    TWITTER_API_KEY: Optional[str] = None
    TWITTER_API_SECRET: Optional[str] = None
    TWITTER_BEARER_TOKEN: Optional[str] = None
    TWITTER_ACCESS_TOKEN: Optional[str] = None
    TWITTER_ACCESS_SECRET: Optional[str] = None

    # Resource Constraints for Local Models
    MAX_VRAM_GB: float = 8.0
    LOCAL_MODEL_SIZE: str = "auto"

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
