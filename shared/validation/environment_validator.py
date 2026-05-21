import os
import sys
import shutil
import asyncio
import logging
import subprocess
from typing import List, Dict, Any, Optional
from pathlib import Path

# Try importing dependencies for validation
try:
    import psutil
except ImportError:
    psutil = None

try:
    import colorama
    from colorama import Fore, Style
    colorama.init(autoreset=True)
except ImportError:
    # Fallback if colorama is not installed yet
    class Fore:
        GREEN = ""
        RED = ""
        YELLOW = ""
        BLUE = ""
        CYAN = ""
    class Style:
        BRIGHT = ""
        RESET = ""

from shared.config.settings import settings
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

logger = logging.getLogger("Zem.EnvironmentValidator")

class EnvironmentValidator:
    """
    Production-ready environment, dependency, infrastructure, API, and runtime validation system.
    Ensures zero runtime configuration/dependency crashes by failing fast with detailed fix instructions.
    """

    def __init__(self):
        self.critical_failures: List[str] = []
        self.warnings: List[str] = []
        self.fix_suggestions: Dict[str, str] = {}

    def _add_failure(self, message: str, category: str, fix_cmd: str):
        self.critical_failures.append(f"[{category}] {message}")
        self.fix_suggestions[message] = fix_cmd

    def _add_warning(self, message: str, category: str, fix_cmd: Optional[str] = None):
        self.warnings.append(f"[{category}] {message}")
        if fix_cmd:
            self.fix_suggestions[message] = fix_cmd

    def validate_libraries(self) -> List[str]:
        """Verify all critical external Python libraries can be imported."""
        required_libraries = {
            "langgraph": "pip install langgraph",
            "langchain": "pip install langchain",
            "openai": "pip install openai",
            "dotenv": "pip install python-dotenv",
            "loguru": "pip install loguru",
            "sqlalchemy": "pip install sqlalchemy",
            "asyncpg": "pip install asyncpg",
            "redis": "pip install redis",
            "rq": "pip install rq",
            "alembic": "pip install alembic",
            "faster_whisper": "pip install faster-whisper",
            "rapidfuzz": "pip install rapidfuzz",
            "numpy": "pip install numpy",
            "tweepy": "pip install tweepy",
            "playwright": "pip install playwright && playwright install",
            "soundfile": "pip install soundfile",
            "librosa": "pip install librosa",
            "pydub": "pip install pydub",
            "psutil": "pip install psutil",
            "colorama": "pip install colorama"
        }

        missing = []
        for lib, install_cmd in required_libraries.items():
            try:
                if lib == "dotenv":
                    import dotenv
                elif lib == "faster_whisper":
                    import faster_whisper
                else:
                    __import__(lib)
            except ImportError:
                missing.append(lib)
                self._add_failure(
                    f"Required library '{lib}' is not installed.",
                    "Python Libraries",
                    install_cmd
                )
        return missing

    def validate_environment(self) -> List[str]:
        """Validate settings, API keys, and environment variables based on enabled flags."""
        # Validate base DB and Redis URLs
        if not settings.DATABASE_URL or "postgresql" not in settings.DATABASE_URL:
            self._add_failure(
                "Invalid DATABASE_URL config. PostgreSQL required.",
                "Environment Config",
                "Set DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>:<port>/<db> in .env"
            )

        if not settings.REDIS_URL or "redis" not in settings.REDIS_URL:
            self._add_failure(
                "Invalid REDIS_URL config. Redis connection string required.",
                "Environment Config",
                "Set REDIS_URL=redis://localhost:6379/0 in .env"
            )

        # Check API keys based on activation flags
        placeholders = ["your_", "here", "api_key", "token"]
        
        def is_placeholder(key: Optional[str]) -> bool:
            if not key:
                return True
            return any(p in key.lower() for p in placeholders)

        # OpenAI
        if settings.ENABLE_OPENAI:
            if is_placeholder(settings.OPENAI_API_KEY):
                self._add_failure(
                    "OpenAI is enabled but OPENAI_API_KEY is missing or invalid.",
                    "API Keys",
                    "Add OPENAI_API_KEY=sk-... to your .env file or set ENABLE_OPENAI=false to run offline"
                )

        # Claude / Anthropic
        if settings.ENABLE_CLAUDE:
            if is_placeholder(settings.ANTHROPIC_API_KEY):
                self._add_failure(
                    "Claude is enabled but ANTHROPIC_API_KEY is missing or invalid.",
                    "API Keys",
                    "Add ANTHROPIC_API_KEY=sk-ant-... to your .env file or set ENABLE_CLAUDE=false"
                )

        # Gemini / Google
        if getattr(settings, "ENABLE_GEMINI", False):
            if is_placeholder(settings.GEMINI_API_KEY) and is_placeholder(settings.GOOGLE_API_KEY):
                self._add_failure(
                    "Gemini is enabled but GEMINI_API_KEY / GOOGLE_API_KEY is missing or invalid.",
                    "API Keys",
                    "Add GEMINI_API_KEY=... to your .env file or set ENABLE_GEMINI=false"
                )

        # Sarvam AI
        if settings.ENABLE_SARVAM:
            if is_placeholder(settings.SARVAM_API_KEY):
                self._add_failure(
                    "Sarvam AI is enabled but SARVAM_API_KEY is missing or invalid.",
                    "API Keys",
                    "Add SARVAM_API_KEY=... to your .env file or set ENABLE_SARVAM=false"
                )

        # ElevenLabs
        if getattr(settings, "ENABLE_ELEVENLABS", False) or is_placeholder(settings.ELEVENLABS_API_KEY) == False:
            if is_placeholder(settings.ELEVENLABS_API_KEY):
                self._add_warning(
                    "ElevenLabs API Key is missing or invalid. Narration fallback will be used.",
                    "API Keys",
                    "Add ELEVENLABS_API_KEY=... to your .env file"
                )

        # Murf AI
        if settings.ENABLE_MURF:
            if is_placeholder(settings.MURF_API_KEY):
                self._add_failure(
                    "Murf AI is enabled but MURF_API_KEY is missing or invalid.",
                    "API Keys",
                    "Add MURF_API_KEY=... to your .env file or set ENABLE_MURF=false"
                )

        # Reddit Credentials (if enabled/referenced)
        if getattr(settings, "ENABLE_REDDIT", False):
            if is_placeholder(settings.REDDIT_CLIENT_ID) or is_placeholder(settings.REDDIT_CLIENT_SECRET):
                self._add_warning(
                    "Reddit client credentials are not fully configured. Trend Discovery might fail.",
                    "API Keys",
                    "Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env"
                )

        # Twitter/X Credentials (if enabled)
        if getattr(settings, "ENABLE_TWITTER", True):
            if is_placeholder(settings.TWITTER_API_KEY) or is_placeholder(settings.TWITTER_BEARER_TOKEN):
                self._add_warning(
                    "Twitter API v2 credentials are not configured. Falling back to Scraper or Mocks.",
                    "API Keys",
                    "Add TWITTER_API_KEY and TWITTER_BEARER_TOKEN to .env for premium trend discovery"
                )

        return self.critical_failures

    async def validate_services(self) -> List[str]:
        """Validate database, Redis, and Ollama connections and status."""
        # 1. PostgreSQL and Alembic Migrations
        try:
            engine = create_async_engine(settings.DATABASE_URL)
            async with engine.connect() as conn:
                # Check basic connection
                await conn.execute(text("SELECT 1"))
                
                # Check if alembic_version table exists
                res = await conn.execute(text(
                    "SELECT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'alembic_version')"
                ))
                table_exists = res.scalar()
                
                if not table_exists:
                    self._add_failure(
                        "PostgreSQL is online but database migrations have not been applied.",
                        "Database Services",
                        "alembic upgrade head"
                    )
                else:
                    # Verify migrations are fully up to date
                    from alembic.config import Config
                    from alembic.script import ScriptDirectory
                    
                    try:
                        alembic_cfg = Config("alembic.ini")
                        script_dir = ScriptDirectory.from_config(alembic_cfg)
                        head_rev = script_dir.get_current_head()
                        
                        db_res = await conn.execute(text("SELECT version_num FROM alembic_version"))
                        db_rev = db_res.scalar()
                        
                        if db_rev != head_rev:
                            self._add_failure(
                                f"Migrations out of date. DB version: {db_rev}, head version: {head_rev}",
                                "Database Services",
                                "alembic upgrade head"
                            )
                    except Exception as migration_err:
                        self._add_warning(
                            f"Could not verify Alembic migration version programmatically: {migration_err}",
                            "Database Services"
                        )
            await engine.dispose()
        except Exception as db_err:
            self._add_failure(
                f"Failed to connect to PostgreSQL: {db_err}",
                "Database Services",
                "docker compose up -d postgres  (or verify database server is running)"
            )

        # 2. Redis Connection
        try:
            import redis
            r = redis.Redis.from_url(settings.REDIS_URL, socket_connect_timeout=2.0)
            r.ping()
            r.close()
        except Exception as redis_err:
            if getattr(settings, "LANGGRAPH_CHECKPOINT_BACKEND", "redis").lower() == "memory":
                self._add_warning(
                    f"Failed to connect to Redis: {redis_err}. Memory checkpointing is active, so pipeline execution is unaffected.",
                    "Redis Service",
                    "docker compose up -d redis  (or run: redis-server) to enable persistent state"
                )
            else:
                self._add_failure(
                    f"Failed to connect to Redis: {redis_err}",
                    "Redis Service",
                    "docker compose up -d redis  (or run: redis-server)"
                )

        # 3. Ollama Connection
        if settings.ENABLE_OLLAMA:
            try:
                import httpx
                async with httpx.AsyncClient(timeout=2.0) as client:
                    resp = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
                    if resp.status_code != 200:
                        self._add_failure(
                            f"Ollama server returned invalid status code: {resp.status_code}",
                            "Ollama Service",
                            "Verify Ollama configuration and port 11434 status."
                        )
            except Exception as ollama_err:
                self._add_failure(
                    f"Failed to connect to Ollama server at {settings.OLLAMA_BASE_URL}: {ollama_err}",
                    "Ollama Service",
                    "Verify Ollama is installed and running: ollama serve"
                )

        return self.critical_failures

    def validate_binaries(self) -> List[str]:
        """Validate FFmpeg and FFprobe binary availability and capabilities."""
        ffmpeg_bin = getattr(settings, "FFMPEG_BINARY", "ffmpeg")
        
        # 1. Verify existence in path
        ffmpeg_path = shutil.which(ffmpeg_bin)
        ffprobe_path = shutil.which("ffprobe")

        if not ffmpeg_path:
            self._add_failure(
                f"FFmpeg binary '{ffmpeg_bin}' was not found in the system PATH.",
                "FFmpeg Binaries",
                "winget install Gyan.FFmpeg  (Windows) or apt install ffmpeg (Linux) or brew install ffmpeg (macOS)"
            )
            return self.critical_failures

        if not ffprobe_path:
            self._add_warning(
                "FFprobe binary was not found in the system PATH. Media metadata validation may fail.",
                "FFmpeg Binaries",
                "Add FFprobe to your system PATH."
            )

        # 2. Check compiled filters (specifically subtitles and libass/ass)
        try:
            result = subprocess.run(
                [ffmpeg_bin, "-filters"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            output = result.stdout
            
            has_subtitles = "subtitles" in output
            has_ass = "ass" in output
            
            if not has_subtitles:
                self._add_failure(
                    "FFmpeg is installed but does not have the 'subtitles' filter enabled.",
                    "FFmpeg Binaries",
                    "Re-install FFmpeg with subtitle filters enabled."
                )
            
            if not has_ass:
                self._add_warning(
                    "FFmpeg is installed but does not support direct ASS subtitle rendering. Text styling may be ignored.",
                    "FFmpeg Binaries"
                )
        except Exception as e:
            self._add_warning(
                f"Failed to check FFmpeg filters list: {e}",
                "FFmpeg Binaries"
            )

        return self.critical_failures

    async def validate_models(self) -> List[str]:
        """Verify Ollama models, Kokoro paths, and hardware resource compatibility."""
        # 1. Ollama Models check
        if settings.ENABLE_OLLAMA:
            try:
                import httpx
                async with httpx.AsyncClient(timeout=3.0) as client:
                    resp = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
                    models_data = resp.json().get("models", [])
                    installed_models = [m["name"].split(":")[0] for m in models_data] + [m["name"] for m in models_data]
                    
                    required_models = ["qwen2.5", settings.DEFAULT_LOCAL_MODEL]
                    for req_model in required_models:
                        # check if matches either direct name or with tags
                        if not any(req_model in m for m in installed_models):
                            self._add_warning(
                                f"Required Ollama model '{req_model}' is not pulled locally.",
                                "Ollama Models",
                                f"ollama pull {req_model}"
                            )
            except Exception:
                pass # Ollama connectivity failure handled in validate_services

        # 2. Kokoro Local Paths Check
        if settings.ENABLE_KOKORO:
            model_path = getattr(settings, "KOKORO_MODEL_PATH", None)
            if model_path:
                path = Path(model_path)
                if not path.exists():
                    self._add_failure(
                        f"Kokoro model path specified but does not exist: {model_path}",
                        "Kokoro TTS",
                        "Provide a valid path to kokoro model files or leave empty for auto-download."
                    )

        # 3. Hardware RAM/VRAM Compatibility
        if psutil:
            total_ram = psutil.virtual_memory().total / (1024 ** 3) # in GB
            if total_ram < 7.0:
                self._add_warning(
                    f"System RAM is low ({total_ram:.1f} GB). Running LLM and TTS locally may cause slowdowns.",
                    "Hardware Check"
                )

        # Torch VRAM check
        try:
            import torch
            if torch.cuda.is_available():
                vram_bytes = torch.cuda.get_device_properties(0).total_memory
                vram_gb = vram_bytes / (1024 ** 3)
                if vram_gb < 4.0:
                    self._add_warning(
                        f"VRAM is low ({vram_gb:.1f} GB). Local quantization models are recommended.",
                        "Hardware Check"
                    )
            elif getattr(settings, "ENABLE_GPU_RENDERING", False):
                self._add_failure(
                    "GPU rendering is enabled in configurations, but CUDA/GPU is not accessible via PyTorch.",
                    "Hardware Check",
                    "Install PyTorch with CUDA support (pip install torch --index-url https://download.pytorch.org/whl/cu121) or set ENABLE_GPU_RENDERING=false"
                )
        except ImportError:
            if getattr(settings, "ENABLE_GPU_RENDERING", False):
                self._add_failure(
                    "GPU rendering is enabled but PyTorch ('torch') is not installed.",
                    "Hardware Check",
                    "pip install torch"
                )

        return self.critical_failures

    def validate_assets(self) -> List[str]:
        """Verify directories and default asset paths exist."""
        required_dirs = [
            "assets/fonts",
            "assets/videos",
            "assets/audio",
            "assets/subtitles",
            "assets/temp",
            "assets/output",
            "assets/audio/raw",
            "assets/audio/processed",
            "assets/audio/temp",
            "assets/videos/temp"
        ]

        for r_dir in required_dirs:
            path = Path(r_dir)
            if not path.exists():
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Auto-created required asset directory: {r_dir}")
                except Exception as e:
                    self._add_failure(
                        f"Could not create required directory '{r_dir}': {e}",
                        "Assets Validation",
                        f"mkdir -p {r_dir}"
                    )

        # Verify at least one font exists
        fonts_dir = Path("assets/fonts")
        font_files = list(fonts_dir.glob("*.ttf")) + list(fonts_dir.glob("*.otf"))
        if not font_files:
            self._add_warning(
                "No custom fonts found in 'assets/fonts/'. Common system fonts (Arial, Helvetica) will be used as fallbacks.",
                "Assets Validation",
                "Download a clean Sans-serif font (e.g. Montserrat or Inter) to assets/fonts/"
            )

        return self.critical_failures

    async def validate_workers(self) -> List[str]:
        """Verify if any queue worker is registered and online."""
        try:
            engine = create_async_engine(settings.DATABASE_URL)
            async with engine.connect() as conn:
                # Query worker_states table (heartbeats)
                res = await conn.execute(text(
                    "SELECT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'worker_states')"
                ))
                table_exists = res.scalar()
                
                if table_exists:
                    # check for workers updated in the last 60 seconds
                    worker_res = await conn.execute(text(
                        "SELECT COUNT(*) FROM worker_states WHERE last_heartbeat >= NOW() - INTERVAL '1 minute'"
                    ))
                    active_workers = worker_res.scalar()
                    
                    if active_workers == 0:
                        self._add_warning(
                            "No active queue workers detected. Background jobs will stay pending.",
                            "Worker Services",
                            "python scripts/run_worker.py  (in another terminal session)"
                        )
                else:
                    self._add_warning(
                        "Worker states table does not exist. First worker run will initialize it.",
                        "Worker Services"
                    )
            await engine.dispose()
        except Exception:
            pass # DB connection error already logged
        return self.critical_failures

    def validate_project_tree(self) -> List[str]:
        """Validate structure integrity of modules and critical execution scripts."""
        critical_files = [
            "scripts/run_pipeline.py",
            "scripts/run_worker.py",
            "ai/workflows/pipeline/langgraph_orchestrator.py",
            "shared/config/settings.py"
        ]

        for file_path in critical_files:
            if not Path(file_path).exists():
                self._add_failure(
                    f"Critical project file is missing: {file_path}",
                    "Project Integrity",
                    "Restore this file from the repository."
                )

        return self.critical_failures

    async def generate_health_report(self) -> bool:
        """Run all validators, print a beautiful CLI report, and return status."""
        print(f"\n{Style.BRIGHT}{Fore.CYAN}==================================================")
        print(f"{Style.BRIGHT}{Fore.CYAN}RUNNING ZEM ENVIRONMENT PRE-FLIGHT VALIDATION")
        print(f"{Style.BRIGHT}{Fore.CYAN}==================================================")

        # Run checks
        self.validate_project_tree()
        self.validate_libraries()
        self.validate_environment()
        await self.validate_services()
        self.validate_binaries()
        await self.validate_models()
        self.validate_assets()
        await self.validate_workers()

        # Print detailed report
        total_issues = len(self.critical_failures) + len(self.warnings)
        
        # Build category status list
        categories = [
            ("Project Integrity", "validate_project_tree"),
            ("Python Libraries", "validate_libraries"),
            ("Environment Config", "validate_environment"),
            ("Database Services", "validate_services"),
            ("Redis Service", "validate_services"),
            ("Ollama Service", "validate_services"),
            ("FFmpeg Binaries", "validate_binaries"),
            ("Assets Validation", "validate_assets"),
            ("Worker Services", "validate_workers")
        ]

        # Deduplicate and group report
        failures_by_cat = {}
        for f in self.critical_failures:
            cat = f.split("]")[0][1:]
            failures_by_cat.setdefault(cat, []).append(f.split("]")[1].strip())

        warnings_by_cat = {}
        for w in self.warnings:
            cat = w.split("]")[0][1:]
            warnings_by_cat.setdefault(cat, []).append(w.split("]")[1].strip())

        # Render statuses
        all_cats = set(failures_by_cat.keys()) | set(warnings_by_cat.keys())
        
        print(f"\n{Style.BRIGHT}SERVICES STATUS:")
        
        # Print green for completely successful areas
        successful_cats = ["Project Integrity", "Python Libraries", "Environment Config", "Database Services", "Redis Service", "Ollama Service", "FFmpeg Binaries", "Assets Validation", "Worker Services", "Hardware Check", "Ollama Models", "API Keys"]
        for cat in successful_cats:
            if cat not in failures_by_cat and cat not in warnings_by_cat:
                # If the service category is enabled (e.g. Ollama service if ENABLE_OLLAMA is true)
                if cat == "Ollama Service" and not settings.ENABLE_OLLAMA:
                    print(f"  {Fore.YELLOW}[-] {cat:<22} (Disabled)")
                else:
                    print(f"  {Fore.GREEN}[OK] {cat:<22} (Ready)")
            elif cat in failures_by_cat:
                print(f"  {Fore.RED}[ERR] {cat:<22} (CRITICAL ERROR)")
            else:
                print(f"  {Fore.YELLOW}[!] {cat:<22} (Warning/Action Required)")

        if self.critical_failures:
            print(f"\n{Style.BRIGHT}{Fore.RED}CRITICAL ISSUES DETECTED ({len(self.critical_failures)}):")
            for f in self.critical_failures:
                print(f"  {Fore.RED}* {f}")
        
        if self.warnings:
            print(f"\n{Style.BRIGHT}{Fore.YELLOW}WARNINGS / CONFIG SUGGESTIONS ({len(self.warnings)}):")
            for w in self.warnings:
                print(f"  {Fore.YELLOW}* {w}")

        if total_issues > 0:
            print(f"\n{Style.BRIGHT}HOW TO FIX:")
            # Deduplicate recommendations
            printed_recs = set()
            for issue, suggestion in self.fix_suggestions.items():
                if suggestion not in printed_recs:
                    clean_issue = issue.replace("Required library '", "").replace("' is not installed.", "")
                    print(f"  {Fore.CYAN}* For {Style.BRIGHT}{clean_issue}{Style.RESET_ALL}{Fore.CYAN}:")
                    print(f"    {Style.BRIGHT}{Fore.GREEN}{suggestion}")
                    printed_recs.add(suggestion)

        print(f"\n{Style.BRIGHT}{Fore.CYAN}==================================================")
        if self.critical_failures:
            print(f"{Style.BRIGHT}{Fore.RED}PRE-FLIGHT CHECK FAILED. PIPELINE BLOCKED.")
            print(f"{Style.BRIGHT}{Fore.CYAN}==================================================\n")
            return False
        else:
            print(f"{Style.BRIGHT}{Fore.GREEN}PRE-FLIGHT CHECK PASSED. SYSTEM STABLE.")
            print(f"{Style.BRIGHT}{Fore.CYAN}==================================================\n")
            return True
