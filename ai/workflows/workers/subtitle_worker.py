import logging
import os
import json
from typing import Dict, Any

from ai.workflows.workers.base_worker import run_async, execute_job_wrapper
from ai.workflows.queue.models import JobType

logger = logging.getLogger(__name__)

async def _process_subtitle_async(job_id: str, workflow_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Asynchronous business logic for generating subtitles."""
    from ai.subtitles.timestamps.timestamp_generator import TimestampGenerator
    from ai.subtitles.storage.service import SubtitleStorageService
    from ai.subtitles.formatting.subtitle_exporter import SubtitleExporter
    from db.repositories.manager import db_manager
    from shared.redis.client import redis_manager

    audio_path = payload.get("narration_path")
    script_data = payload.get("generated_script", {})
    script_text = script_data.get("full_script", "") if script_data else payload.get("script_text", "")
    
    if not audio_path or not os.path.exists(audio_path):
        raise FileNotFoundError(f"Narration file not found: {audio_path}")

    output_dir = "assets/subtitles/processed"
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize components
    generator = TimestampGenerator(model_size="base", device="cpu")
    exporter = SubtitleExporter()
    
    # Check cache
    await redis_manager.connect()
    cache_key = f"subtitles:{os.path.basename(audio_path)}"
    
    try:
        cached_result = await redis_manager.get_cache(cache_key)
        
        if cached_result:
            logger.info("Found cached subtitle results")
            results = json.loads(cached_result)
        else:
            logger.info("Running Whisper transcription pipeline...")
            results = await generator.process_pipeline(audio_path, script_text)
            # Cache results
            await redis_manager.set_cache(cache_key, json.dumps(results), expire=86400)
            
        # Store in DB
        async with db_manager.session_factory() as session:
            storage = SubtitleStorageService(session)
            gen_id = await storage.create_generation()
            await storage.store_timestamps(gen_id, results["words"], results["segments"])
            logger.info(f"Stored subtitle metadata with ID: {gen_id}")
            
        # Export formats
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        ass_path = os.path.join(output_dir, f"{base_name}.ass")
        json_path = os.path.join(output_dir, f"{base_name}.json")
        srt_path = os.path.join(output_dir, f"{base_name}.srt")
        
        exporter.to_json(results["segments"], json_path)
        exporter.to_srt(results["segments"], srt_path)
        exporter.to_ass_karaoke(results["segments"], ass_path)
        
        logger.info(f"Subtitles generated successfully: {ass_path}")
        
        metadata = payload.get("execution_metadata", {})
        metadata["subtitle_json_path"] = json_path
        metadata["subtitle_srt_path"] = srt_path
        metadata["subtitle_generation_id"] = gen_id
        
        return {
            "subtitle_path": ass_path,
            "execution_metadata": metadata
        }
        
    finally:
        await redis_manager.disconnect()

def process_job(job_id: str, workflow_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """RQ target function for Subtitle Worker."""
    return run_async(
        execute_job_wrapper(
            job_id=job_id,
            workflow_id=workflow_id,
            payload=payload,
            job_type=JobType.SUBTITLE,
            processor_func=_process_subtitle_async
        )
    )
