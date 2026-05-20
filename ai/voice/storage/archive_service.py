import logging
from pathlib import Path
from .file_manager import FileManager

logger = logging.getLogger(__name__)

class ArchiveService:
    """
    Handles long-term archival logic, including compression and remote storage preparation.
    """
    
    def __init__(self, file_manager: FileManager):
        self.fm = file_manager

    async def compress_archive(self, filename: str):
        """Optional: Compress archived files to save space."""
        # Implementation using zipfile or tarfile
        pass

    async def prepare_for_cloud(self, filename: str):
        """Prepares metadata for uploading to S3 or R2."""
        # Placeholder for future cloud integration
        pass
