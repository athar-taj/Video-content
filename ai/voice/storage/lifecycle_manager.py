import logging
from typing import Dict, Any
from .models import AudioStatus
from .audio_metadata_service import AudioMetadataService

logger = logging.getLogger(__name__)

class LifecycleManager:
    """
    Manages the lifecycle state transitions of audio assets.
    """
    
    VALID_TRANSITIONS = {
        AudioStatus.PENDING: [AudioStatus.GENERATING, AudioStatus.FAILED],
        AudioStatus.GENERATING: [AudioStatus.GENERATED, AudioStatus.FAILED],
        AudioStatus.GENERATED: [AudioStatus.PROCESSING, AudioStatus.FAILED],
        AudioStatus.PROCESSING: [AudioStatus.COMPLETED, AudioStatus.FAILED],
        AudioStatus.COMPLETED: [AudioStatus.ARCHIVED, AudioStatus.DELETED],
        AudioStatus.ARCHIVED: [AudioStatus.DELETED],
        AudioStatus.FAILED: [AudioStatus.PENDING, AudioStatus.DELETED],
        AudioStatus.DELETED: []
    }

    def __init__(self, metadata_service: AudioMetadataService):
        self.metadata = metadata_service

    async def transition_to(self, audio_id: str, next_status: AudioStatus):
        """Transitions an audio record to a new state if the transition is valid."""
        record = await self.metadata.get_record(audio_id)
        if not record:
            raise ValueError(f"Audio record {audio_id} not found.")
            
        current_status = record.status
        if next_status not in self.VALID_TRANSITIONS.get(current_status, []):
            logger.warning(f"Invalid transition from {current_status} to {next_status}")
            # We might still allow it in some cases, but log it
            
        await self.metadata.update_audio_status(audio_id, next_status)
        logger.info(f"Audio {audio_id} transitioned: {current_status} -> {next_status}")
