from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Dict, List, Any

class Settings(BaseSettings):
    # API Settings
    PROJECT_NAME: str = "Zem API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENV: str = "development"
    DEBUG: bool = True
    
    # Database URL
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/zem_db"
    # Postgres Components
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None

    # Redis URL
    REDIS_URL: str = "redis://localhost:6379/0"
    # Redis Components
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[str] = None

    # RabbitMQ Connection URL
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    # RabbitMQ Components
    RABBITMQ_HOST: Optional[str] = None
    RABBITMQ_PORT: Optional[int] = None
    RABBITMQ_USER: Optional[str] = None
    RABBITMQ_PASSWORD: Optional[str] = None
    
    # AI Providers
    HF_ENABLED: bool = True
    HF_DEFAULT_MODEL: str = "Qwen/Qwen2.5-3B-Instruct"
    HF_MODEL_CACHE: str = "./models/huggingface"
    HF_DEVICE: str = "auto"
    HF_ENABLE_QUANTIZATION: bool = True
    HF_MAX_NEW_TOKENS: int = 512
    HF_ENABLE_FALLBACKS: bool = True
    OPENAI_API_KEY: Optional[str] = None
    HF_API_TOKEN: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None
    HF_HOME: str = ".cache/huggingface"
    MISTRAL_API_KEY: Optional[str] = None
    SARVAM_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = "AIzaSyCjGaF7_UffyKcSYKaseFTiGyrVsaaBKMA"
    ELEVENLABS_API_KEY: Optional[str] = "4fcf3611fefbdeb3fa21e2844a2038a36cf595e97ba80f74cf3e2528b7e1c247"
    MURF_API_KEY: Optional[str] = "ap2_284b65bf-5367-4f02-b5b2-541f6c535a8c"
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    KOKORO_MODEL_PATH: Optional[str] = None
    FFMPEG_BINARY: str = "ffmpeg"
    FFPROBE_BINARY: str = "ffprobe"
    WHISPER_MODEL: str = "base"
    LANGGRAPH_CHECKPOINT_BACKEND: str = "redis"

    # Provider Activation Flags
    ENABLE_OPENAI: bool = True
    ENABLE_CLAUDE: bool = True
    ENABLE_MURF: bool = True
    ENABLE_KOKORO: bool = True
    ENABLE_SARVAM: bool = True
    ENABLE_HF: bool = True
    ENABLE_HUGGINGFACE: Optional[bool] = None
    ENABLE_GEMINI: bool = False
    ENABLE_MISTRAL: bool = True
    ENABLE_TWITTER: bool = True
    ENABLE_TWIKIT: bool = True
    ENABLE_SNSCRAPE: bool = True
    ENABLE_GPU_RENDERING: bool = False
    MAX_RENDER_WORKERS: int = 2
    MAX_PIPELINE_WORKERS: Optional[int] = None

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
    DEFAULT_LOCAL_MODEL: str = "Qwen/Qwen2.5-3B-Instruct"
    
    # Task-to-Model Routing
    MODEL_ROUTING: Dict[str, str] = {
        "hook_generation": "mistral",
        "script_generation": "openai",
        "validation": "huggingface",
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
    
    @model_validator(mode="before")
    @classmethod
    def assemble_urls(cls, values: Any) -> Any:
        if isinstance(values, dict):
            # 1. Assemble PostgreSQL URL if components are provided
            pg_user = values.get("POSTGRES_USER")
            pg_pass = values.get("POSTGRES_PASSWORD")
            pg_host = values.get("POSTGRES_HOST")
            pg_port = values.get("POSTGRES_PORT")
            pg_db = values.get("POSTGRES_DB")
            if pg_user and pg_pass and pg_host and pg_port and pg_db:
                values["DATABASE_URL"] = f"postgresql+asyncpg://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"

            # 2. Assemble Redis URL if components are provided
            redis_host = values.get("REDIS_HOST")
            redis_port = values.get("REDIS_PORT")
            if redis_host and redis_port:
                values["REDIS_URL"] = f"redis://{redis_host}:{redis_port}/0"

            # Assemble RabbitMQ URL if components are provided
            rmq_host = values.get("RABBITMQ_HOST")
            rmq_port = values.get("RABBITMQ_PORT")
            rmq_user = values.get("RABBITMQ_USER")
            rmq_pass = values.get("RABBITMQ_PASSWORD")
            if rmq_host and rmq_port and rmq_user and rmq_pass:
                values["RABBITMQ_URL"] = f"amqp://{rmq_user}:{rmq_pass}@{rmq_host}:{rmq_port}/"

            # 3. Map ENABLE_HUGGINGFACE to ENABLE_HF
            if "ENABLE_HUGGINGFACE" in values:
                values["ENABLE_HF"] = values["ENABLE_HUGGINGFACE"]
            elif "ENABLE_HF" in values:
                values["ENABLE_HUGGINGFACE"] = values["ENABLE_HF"]

            # 4. Map HUGGINGFACE_API_KEY to HF_API_TOKEN
            if "HUGGINGFACE_API_KEY" in values and values.get("HUGGINGFACE_API_KEY"):
                values["HF_API_TOKEN"] = values["HUGGINGFACE_API_KEY"]
            elif "HF_API_TOKEN" in values and values.get("HF_API_TOKEN"):
                values["HUGGINGFACE_API_KEY"] = values["HF_API_TOKEN"]

            # 5. Map HF_DEFAULT_MODEL to DEFAULT_LOCAL_MODEL
            if "HF_DEFAULT_MODEL" in values and values.get("HF_DEFAULT_MODEL"):
                values["DEFAULT_LOCAL_MODEL"] = values["HF_DEFAULT_MODEL"]

            # 6. Map MAX_PIPELINE_WORKERS to MAX_RENDER_WORKERS
            if "MAX_PIPELINE_WORKERS" in values and values.get("MAX_PIPELINE_WORKERS"):
                values["MAX_RENDER_WORKERS"] = int(values["MAX_PIPELINE_WORKERS"])

        return values
        
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
