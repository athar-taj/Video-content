import os
import sys
import shutil
import subprocess
import logging
from pathlib import Path

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Zem.Bootstrap")

def print_banner():
    print("""
======================================================================
ZEM AUTONOMOUS MEDIA OPERATING SYSTEM -- BOOTSTRAP & INITIALIZATION
======================================================================
This script initializes folders, configuration, and database schemas.
""")

def create_directory_layout():
    logger.info("Step 1: Initializing directory layout...")
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
    for d in required_dirs:
        path = Path(d)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"  Created: {d}")
        else:
            logger.info(f"  Exists:  {d}")

def setup_environment_file():
    logger.info("Step 2: Setting up environment configuration (.env)...")
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            shutil.copy(".env.example", ".env")
            logger.info("  Copied .env.example to .env")
            print("[!] New '.env' file created. Please open it and configure your custom API keys if needed.")
        else:
            logger.error("  Error: .env.example file not found in root directory!")
    else:
        logger.info("  .env file already exists.")

def run_migrations():
    logger.info("Step 3: Running database schema migrations...")
    alembic_ini = Path("alembic.ini")
    if not alembic_ini.exists():
        logger.error("  Error: alembic.ini not found. Cannot apply database migrations.")
        return
        
    try:
        # Run alembic upgrade head using the active Python executable module
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        if result.returncode == 0:
            logger.info("  Database migrations successfully applied (Alembic Head).")
            print(result.stdout)
        else:
            logger.error("  Alembic migration failed:")
            print(result.stderr)
            logger.warning("Please verify your PostgreSQL database is running and credentials in .env are correct.")
    except Exception as e:
        logger.error(f"  Failed to run alembic: {e}")

def check_external_dependencies():
    logger.info("Step 4: Checking external system binaries...")
    ffmpeg_path = shutil.which("ffmpeg")
    ffprobe_path = shutil.which("ffprobe")
    
    if ffmpeg_path:
        logger.info(f"  FFmpeg is installed: {ffmpeg_path}")
    else:
        logger.warning("  FFmpeg is NOT found in PATH. Please install FFmpeg (e.g. winget install Gyan.FFmpeg or apt install ffmpeg).")
        
    if ffprobe_path:
        logger.info(f"  FFprobe is installed: {ffprobe_path}")
    else:
        logger.warning("  FFprobe is NOT found in PATH. Media metadata validations might fail.")

def main():
    print_banner()
    create_directory_layout()
    setup_environment_file()
    run_migrations()
    check_external_dependencies()
    
    print("\n======================================================================")
    print("SUCCESS: ZEM ENVIRONMENT BOOTSTRAPPED SUCCESSFULLY!")
    print("======================================================================")
    print("To test the pre-flight checks and pipeline routing:")
    print("  python scripts/run_pipeline.py")
    print("To run the X/Twitter discovery integration test:")
    print("  python scripts/test_twitter_pipeline.py")
    print("======================================================================\n")

if __name__ == "__main__":
    main()
