import asyncio
import sys
import uuid
from pathlib import Path
import logging

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from db.repositories.manager import db_manager
from ai.voice.storage.audio_storage_service import AudioStorageService
from ai.voice.storage.audio_metadata_service import AudioMetadataService
from ai.voice.storage.cleanup_service import CleanupService
from ai.voice.storage.file_manager import FileManager
from ai.voice.storage.validators import AudioValidator
from ai.voice.storage.checksum import AudioChecksum
from ai.voice.storage.models import AudioMetadata, AudioStatus
from shared.logging.logger import log

async def main():
    log.info("Starting Audio Storage System Test...")
    
    # 1. Initialize Services
    file_manager = FileManager()
    storage_service = AudioStorageService(file_manager)
    
    # 2. Generate Test Audio (mocking)
    script_id = "test_script_" + str(uuid.uuid4())[:8]
    provider = "kokoro"
    voice = "am_adam"
    
    # Create a mock raw audio file in temp
    temp_filename = f"temp_{uuid.uuid4()}.mp3"
    temp_path = file_manager.get_temp_path(temp_filename)
    
    # Write some dummy data to simulate an MP3
    with open(temp_path, "wb") as f:
        f.write(b"MOCK_AUDIO_DATA_FOR_TESTING_" * 100)
        
    log.info(f"Generated mock temp audio at {temp_path}")
    
    async for session in db_manager.get_session():
        metadata_service = AudioMetadataService(session)
        cleanup_service = CleanupService(storage_service, file_manager)
        
        # 3. Save Audio (Raw)
        raw_path = await storage_service.save_raw_audio(temp_path, script_id, provider, voice)
        
        # 4. Process Audio (Mock processing by just copying)
        # We will use the raw audio as processed for this test
        processed_filename = raw_path.name
        processed_path = await storage_service.save_processed_audio(raw_path, processed_filename)
        
        # 5. Store Metadata
        checksum = AudioChecksum.generate_sha256(processed_path)
        
        metadata = AudioMetadata(
            script_id=script_id,
            provider=provider,
            voice_name=voice,
            preset_name="horror_narrator",
            emotional_tone="suspense",
            raw_audio_path=str(raw_path),
            processed_audio_path=str(processed_path),
            duration_seconds=15.5,
            file_size_bytes=processed_path.stat().st_size,
            checksum=checksum,
            status=AudioStatus.COMPLETED
        )
        
        record_id = await metadata_service.create_audio_record(metadata)
        log.info(f"Stored metadata with record ID: {record_id}")
        
        # 6. Validate Integrity
        is_valid, reason = AudioValidator.is_valid_audio(processed_path)
        log.info(f"Audio validation result: Valid={is_valid}, Reason={reason}")
        
        verify_checksum = AudioChecksum.verify_checksum(processed_path, checksum)
        log.info(f"Checksum verification: {verify_checksum}")
        
        # 7. Fetch Metadata
        fetched_record = await metadata_service.get_record(record_id)
        log.info(f"Fetched record: ID={fetched_record.id}, Status={fetched_record.status}")
        
        # 8. Archive Audio
        archived_path = await storage_service.archive_audio(processed_filename)
        await metadata_service.update_audio_status(record_id, AudioStatus.ARCHIVED)
        
        fetched_record = await metadata_service.get_record(record_id)
        log.info(f"Record status after archive: {fetched_record.status}")
        
        # 9. Cleanup Temp Files
        log.info("Running cleanup for temp files (using 0 hours to force cleanup of our new temp file)...")
        await cleanup_service.cleanup_temp_files(older_than_hours=0)
        
        log.info("Audio Storage System Test Completed Successfully.")
        break # Only need one session loop

if __name__ == "__main__":
    asyncio.run(main())
