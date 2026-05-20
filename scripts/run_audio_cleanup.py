import asyncio
import sys
from pathlib import Path
import logging

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from shared.config.settings import settings
from ai.voice.storage.audio_storage_service import AudioStorageService
from ai.voice.storage.file_manager import FileManager
from ai.voice.storage.cleanup_service import CleanupService
from shared.logging.logger import log

async def main():
    log.info("Starting Audio Storage Cleanup...")

    # 1. Load Config (from settings)
    retention_temp = settings.RETENTION_TEMP_HOURS
    retention_failed = settings.RETENTION_FAILED_DAYS
    retention_archive = settings.RETENTION_ARCHIVE_DAYS

    # 2. Initialize Services
    file_manager = FileManager()
    storage_service = AudioStorageService(file_manager)
    cleanup_service = CleanupService(storage_service, file_manager)

    # 3. Find and Delete Expired Temp Files
    log.info(f"Cleaning temp files older than {retention_temp} hours...")
    temp_cleaned = await cleanup_service.cleanup_temp_files(older_than_hours=retention_temp)

    # 4. Delete Failed Audio (mock implementation currently)
    log.info(f"Cleaning failed audio older than {retention_failed} days...")
    # failed_cleaned = await cleanup_service.cleanup_failed_audio(older_than_days=retention_failed)
    failed_cleaned = 0

    # 5. Archive Old Audio
    log.info(f"Archiving processed audio older than {retention_archive} days...")
    archived_count = await cleanup_service.archive_old_audio(older_than_days=retention_archive)

    # 6. Generate Cleanup Report
    log.info("========================================")
    log.info("          CLEANUP REPORT                ")
    log.info("========================================")
    log.info(f"Temp Files Deleted:     {temp_cleaned}")
    log.info(f"Failed Audio Deleted:   {failed_cleaned}")
    log.info(f"Audio Files Archived:   {archived_count}")
    log.info("========================================")
    log.info("Cleanup completed successfully.")

if __name__ == "__main__":
    asyncio.run(main())
