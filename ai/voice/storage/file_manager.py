import os
from pathlib import Path
from typing import Optional

class FileManager:
    """
    Manages audio file paths and directory structures.
    """
    
    BASE_PATH = Path("assets/audio")
    RAW_DIR = BASE_PATH / "raw"
    PROCESSED_DIR = BASE_PATH / "processed"
    TEMP_DIR = BASE_PATH / "temp"
    ARCHIVE_DIR = BASE_PATH / "archived"

    def __init__(self):
        self._ensure_directories()

    def _ensure_directories(self):
        for directory in [self.RAW_DIR, self.PROCESSED_DIR, self.TEMP_DIR, self.ARCHIVE_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

    def get_raw_path(self, filename: str) -> Path:
        return self.RAW_DIR / filename

    def get_processed_path(self, filename: str) -> Path:
        return self.PROCESSED_DIR / filename

    def get_temp_path(self, filename: str) -> Path:
        return self.TEMP_DIR / filename

    def get_archive_path(self, filename: str) -> Path:
        return self.ARCHIVE_DIR / filename

    def generate_filename(self, script_id: str, provider: str, voice: str, version: str = "v1") -> str:
        """Deterministic filename format: {script_id}_{provider}_{voice}_{version}.mp3"""
        clean_voice = voice.lower().replace(" ", "_")
        return f"{script_id}_{provider.lower()}_{clean_voice}_{version}.mp3"
