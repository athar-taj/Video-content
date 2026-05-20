import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from db.models.audio import AudioGenerationModel, AudioStatus
from .models import AudioMetadata

class AudioMetadataService:
    """
    Handles database operations for audio generation metadata.
    """
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_audio_record(self, metadata: AudioMetadata) -> str:
        """Creates a new record in the audio_generations table."""
        record_id = metadata.id or str(uuid.uuid4())
        
        db_record = AudioGenerationModel(
            id=record_id,
            script_id=metadata.script_id,
            provider=metadata.provider,
            voice_name=metadata.voice_name,
            preset_name=metadata.preset_name,
            emotional_tone=metadata.emotional_tone,
            narration_style=metadata.narration_style,
            raw_audio_path=metadata.raw_audio_path,
            processed_audio_path=metadata.processed_audio_path,
            duration_seconds=metadata.duration_seconds,
            file_size_bytes=metadata.file_size_bytes,
            checksum=metadata.checksum,
            sample_rate=metadata.sample_rate,
            bitrate=metadata.bitrate,
            generation_time_ms=metadata.generation_time_ms,
            status=metadata.status,
            metadata_json=metadata.metadata
        )
        
        self.db.add(db_record)
        await self.db.commit()
        return record_id

    async def update_audio_status(self, audio_id: str, status: AudioStatus):
        """Updates the status of an audio record."""
        stmt = update(AudioGenerationModel).where(AudioGenerationModel.id == audio_id).values(status=status)
        await self.db.execute(stmt)
        await self.db.commit()

    async def update_audio_metrics(self, audio_id: str, metrics: Dict[str, Any]):
        """Updates metrics like duration, file size, and checksum."""
        stmt = update(AudioGenerationModel).where(AudioGenerationModel.id == audio_id).values(**metrics)
        await self.db.execute(stmt)
        await self.db.commit()

    async def get_audio_by_script(self, script_id: str) -> List[AudioGenerationModel]:
        """Fetches all audio records associated with a script."""
        result = await self.db.execute(select(AudioGenerationModel).where(AudioGenerationModel.script_id == script_id))
        return result.scalars().all()

    async def get_record(self, audio_id: str) -> Optional[AudioGenerationModel]:
        """Fetches a single record by ID."""
        result = await self.db.execute(select(AudioGenerationModel).where(AudioGenerationModel.id == audio_id))
        return result.scalar_one_or_none()
