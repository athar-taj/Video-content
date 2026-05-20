import asyncio
import argparse
import os
import sys
import uuid
from typing import List

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.subtitles.formatting.models import SubtitleSegment, SubtitleWord
from ai.subtitles.formatting.subtitle_exporter import SubtitleExporter
from ai.subtitles.formatting.validators import SubtitleValidator
from db.repositories.manager import db_manager
from db.models.subtitles import SubtitleGeneration, SubtitleSegmentModel, FormattedSubtitleModel, SubtitleExportModel
from sqlalchemy import select
from shared.logging.logger import log
from shared.redis.client import redis_manager

async def run_formatter(generation_id: str, script_id: str, formats: List[str] = ["srt", "json"]):
    log.info(f"Starting subtitle formatting for generation: {generation_id}")
    
    exporter = SubtitleExporter()
    validator = SubtitleValidator()
    
    await redis_manager.connect()
    
    async with db_manager.session_factory() as session:
        # Load segments from DB
        result = await session.execute(
            select(SubtitleSegmentModel).where(SubtitleSegmentModel.subtitle_generation_id == generation_id)
        )
        db_segments = result.scalars().all()
        
        if not db_segments:
            log.error(f"No segments found for generation: {generation_id}")
            return

        # Convert to Pydantic models
        segments = []
        for db_seg in db_segments:
            words = [SubtitleWord(**w) for w in db_seg.word_data]
            segments.append(SubtitleSegment(
                segment_id=str(db_seg.id),
                text=db_seg.text,
                words=words,
                start_time=db_seg.start_time,
                end_time=db_seg.end_time,
                duration=db_seg.duration
            ))

        # Validate
        if not validator.validate_segments(segments):
            log.error("Subtitle segments validation failed")
            return

        # Export formats
        for fmt in formats:
            try:
                # Check cache
                cache_key = f"subtitle_output:{generation_id}:{fmt}"
                cached_path = await redis_manager.get_cache(cache_key)
                if cached_path:
                    log.info(f"Found cached {fmt} output at {cached_path}")
                    continue

                output_path = await exporter.export(segments, fmt, script_id)
                log.info(f"Exported {fmt} to {output_path}")

                # Store metadata
                fmt_id = str(uuid.uuid4())
                fmt_model = FormattedSubtitleModel(
                    id=fmt_id,
                    subtitle_generation_id=generation_id,
                    format=fmt,
                    output_path=str(output_path),
                    file_size=os.path.getsize(output_path)
                )
                session.add(fmt_model)
                
                export_model = SubtitleExportModel(
                    id=str(uuid.uuid4()),
                    subtitle_id=fmt_id,
                    export_type=fmt,
                    status="completed"
                )
                session.add(export_model)
                
                # Cache path
                await redis_manager.set_cache(cache_key, str(output_path), expire=86400)
                
            except Exception as e:
                log.error(f"Failed to export {fmt}: {e}")

        await session.commit()
        log.info("Subtitle formatting completed successfully")

    await redis_manager.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zem Subtitle Formatter")
    parser.add_argument("--gen_id", required=True, help="Subtitle generation ID")
    parser.add_argument("--script_id", required=True, help="Script ID for naming")
    parser.add_argument("--formats", nargs="+", default=["srt", "json", "karaoke"], help="Formats to export")
    
    args = parser.parse_args()
    
    asyncio.run(run_formatter(args.gen_id, args.script_id, args.formats))
