import asyncio
import argparse
import os
import sys
from typing import Optional

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.subtitles.timestamps.timestamp_generator import TimestampGenerator
from ai.subtitles.storage.service import SubtitleStorageService
from ai.subtitles.formatting.exporter import SubtitleExporter
from db.repositories.manager import db_manager
from shared.redis.client import redis_manager
from shared.logging.logger import log

async def main(audio_path: str, script_path: Optional[str] = None, output_dir: str = "assets/subtitles/processed"):
    log.info(f"Starting word timestamp generation for {audio_path}")
    
    # Load script if provided
    script_content = None
    if script_path and os.path.exists(script_path):
        with open(script_path, "r", encoding="utf-8") as f:
            script_content = f.read()
            
    # Initialize components
    generator = TimestampGenerator(model_size="base", device="cpu")
    exporter = SubtitleExporter()
    
    # Check cache first (using audio file hash or path)
    await redis_manager.connect()
    cache_key = f"subtitles:{os.path.basename(audio_path)}"
    cached_result = await redis_manager.get_cache(cache_key)
    
    if cached_result:
        log.info("Found cached subtitle results")
        # Could parse and return here, but for now we'll re-run or just log
        
    # Run pipeline
    results = await generator.process_pipeline(audio_path, script_content)
    
    # Store in DB
    async with db_manager.session_factory() as session:
        storage = SubtitleStorageService(session)
        gen_id = await storage.create_generation()
        await storage.store_timestamps(gen_id, results["words"], results["segments"])
        log.info(f"Stored subtitle metadata with ID: {gen_id}")
        
    # Export formats
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    
    json_path = os.path.join(output_dir, f"{base_name}.json")
    srt_path = os.path.join(output_dir, f"{base_name}.srt")
    ass_path = os.path.join(output_dir, f"{base_name}.ass")
    
    exporter.to_json(results["segments"], json_path)
    exporter.to_srt(results["segments"], srt_path)
    exporter.to_ass_karaoke(results["segments"], ass_path)
    
    # Cache results
    import json
    await redis_manager.set_cache(cache_key, json.dumps(results), expire=86400)
    
    log.info(f"Subtitle generation complete. Outputs: {json_path}, {srt_path}, {ass_path}")
    await redis_manager.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zem Word Timestamp Generation")
    parser.add_argument("--audio", required=True, help="Path to narration audio")
    parser.add_argument("--script", help="Path to original script text")
    parser.add_argument("--output", default="assets/subtitles/processed", help="Output directory")
    
    args = parser.parse_args()
    
    asyncio.run(main(args.audio, args.script, args.output))
