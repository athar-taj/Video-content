import logging
import os
from typing import Dict, Any
from ai.subtitles.timestamps.timestamp_generator import TimestampGenerator
from ai.subtitles.storage.service import SubtitleStorageService
from ai.subtitles.formatting.subtitle_exporter import SubtitleExporter
from db.repositories.manager import db_manager
from shared.redis.client import redis_manager

logger = logging.getLogger(__name__)

async def subtitle_generation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Executing Subtitle Generation Node...")
    
    audio_path = state.get("narration_path")
    script_data = state.get("generated_script", {})
    script_text = script_data.get("full_script", "")
    
    if not audio_path or not os.path.exists(audio_path):
        logger.error(f"Narration file not found: {audio_path}")
        return {"errors": state.get("errors", []) + ["Narration audio missing for subtitle generation"]}

    output_dir = "assets/subtitles/processed"
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Initialize components
        generator = TimestampGenerator(model_size="base", device="cpu")
        exporter = SubtitleExporter()
        
        # Check cache
        await redis_manager.connect()
        cache_key = f"subtitles:{os.path.basename(audio_path)}"
        cached_result = await redis_manager.get_cache(cache_key)
        
        if cached_result:
            logger.info("Found cached subtitle results")
            import json
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
        
        state_metadata = state.get("execution_metadata", {})
        state_metadata["subtitle_json_path"] = json_path
        state_metadata["subtitle_srt_path"] = srt_path
        
        return {
            "subtitle_path": ass_path,
            "execution_metadata": state_metadata
        }
        
    except Exception as e:
        logger.exception(f"Subtitle generation node failed: {e}")
        return {
            "errors": state.get("errors", []) + [f"Subtitle generation failed: {str(e)}"]
        }
    finally:
        await redis_manager.disconnect()
