import shutil
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from .file_manager import FileManager
from .checksum import AudioChecksum

logger = logging.getLogger(__name__)

class AudioStorageService:
    """
    Service for saving, moving, and managing audio files.
    """
    
    def __init__(self, file_manager: Optional[FileManager] = None):
        self.fm = file_manager or FileManager()

    async def save_raw_audio(self, source_path: Path, script_id: str, provider: str, voice: str) -> Path:
        """Saves raw audio from a source (temp) to the raw storage."""
        filename = self.fm.generate_filename(script_id, provider, voice)
        target_path = self.fm.get_raw_path(filename)
        
        # Copy file to raw storage
        shutil.copy2(source_path, target_path)
        logger.info(f"Saved raw audio to {target_path}")
        return target_path

    async def save_processed_audio(self, source_path: Path, filename: str) -> Path:
        """Saves processed audio to the processed storage."""
        target_path = self.fm.get_processed_path(filename)
        shutil.copy2(source_path, target_path)
        logger.info(f"Saved processed audio to {target_path}")
        return target_path

    async def archive_audio(self, filename: str) -> Path:
        """Moves a file from processed to archive storage."""
        source_path = self.fm.get_processed_path(filename)
        if not source_path.exists():
            source_path = self.fm.get_raw_path(filename)
            
        if not source_path.exists():
            raise FileNotFoundError(f"Audio file {filename} not found in raw or processed storage.")
            
        target_path = self.fm.get_archive_path(filename)
        shutil.move(str(source_path), str(target_path))
        logger.info(f"Archived audio file to {target_path}")
        return target_path

    async def delete_audio(self, filename: str):
        """Removes audio files from all local storage layers."""
        paths = [
            self.fm.get_raw_path(filename),
            self.fm.get_processed_path(filename),
            self.fm.get_temp_path(filename)
        ]
        
        for path in paths:
            if path.exists():
                path.unlink()
                logger.info(f"Deleted audio file: {path}")

    async def validate_file(self, file_path: Path) -> Dict[str, Any]:
        """Validates file existence, size, and integrity."""
        if not file_path.exists():
            return {"valid": False, "error": "file_not_found"}
            
        size = file_path.stat().st_size
        if size == 0:
            return {"valid": False, "error": "empty_file"}
            
        checksum = AudioChecksum.generate_sha256(file_path)
        
        return {
            "valid": True,
            "size_bytes": size,
            "checksum": checksum
        }
