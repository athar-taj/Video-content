import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
from .file_manager import FileManager
from .audio_storage_service import AudioStorageService

logger = logging.getLogger(__name__)

class CleanupService:
    """
    Automates the cleanup of temporary, failed, and old audio assets.
    """
    
    def __init__(self, storage_service: AudioStorageService, file_manager: FileManager):
        self.storage = storage_service
        self.fm = file_manager

    async def cleanup_temp_files(self, older_than_hours: int = 24):
        """Deletes temp files older than a certain age."""
        cutoff = time.time() - (older_than_hours * 3600)
        count = 0
        
        for file_path in self.fm.TEMP_DIR.glob("*.*"):
            if file_path.stat().st_mtime < cutoff:
                file_path.unlink()
                count += 1
                
        logger.info(f"Cleaned up {count} temporary files.")
        return count

    async def cleanup_failed_audio(self, older_than_days: int = 7):
        """
        In a real scenario, this would check the database for FAILED status.
        For now, we'll implement the file-level cleanup.
        """
        # Implementation would involve querying DB for records where status=FAILED
        pass

    async def archive_old_audio(self, older_than_days: int = 30):
        """Moves completed files older than N days to archival storage."""
        cutoff = time.time() - (older_than_days * 86400)
        count = 0
        
        for file_path in self.fm.PROCESSED_DIR.glob("*.*"):
            if file_path.stat().st_mtime < cutoff:
                await self.storage.archive_audio(file_path.name)
                count += 1
                
        logger.info(f"Archived {count} old audio files.")
        return count
