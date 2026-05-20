import asyncio
import argparse
import os
import sys
import json
from typing import Optional

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.subtitles.styling.caption_style_manager import CaptionStyleManager
from ai.subtitles.formatting.models import SubtitleSegment, SubtitleWord
from shared.logging.logger import log
from shared.redis.client import redis_manager

async def run_styling(subtitle_json_path: str, style_name: str, output_path: str):
    log.info(f"Starting caption styling with template: {style_name}")
    
    if not os.path.exists(subtitle_json_path):
        log.error(f"Subtitle JSON not found: {subtitle_json_path}")
        return

    with open(subtitle_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # Convert to segments
    segments = []
    for seg_data in data["segments"]:
        words = [SubtitleWord(**w) for w in seg_data["words"]]
        segments.append(SubtitleSegment(
            segment_id=seg_data["segment_id"],
            text=seg_data["text"],
            words=words,
            start_time=seg_data["start_time"],
            end_time=seg_data["end_time"],
            duration=seg_data["duration"]
        ))

    manager = CaptionStyleManager()
    
    # Check cache
    await redis_manager.connect()
    cache_key = f"styled_ass:{os.path.basename(subtitle_json_path)}:{style_name}"
    cached_output = await redis_manager.get_cache(cache_key)
    
    if cached_output:
        log.info("Found cached styled ASS output")
        # In a real scenario, you might just return the path
        
    # Generate ASS
    ass_content = manager.generate_styled_ass(segments, style_name)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(ass_content)
        
    # Cache path
    await redis_manager.set_cache(cache_key, output_path, expire=86400)
    
    log.info(f"Styled ASS exported to {output_path}")
    await redis_manager.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zem Caption Styling Engine")
    parser.add_argument("--json", required=True, help="Path to subtitle JSON")
    parser.add_argument("--style", default="reels_clean", help="Style template name")
    parser.add_argument("--output", required=True, help="Output ASS path")
    
    args = parser.parse_args()
    
    asyncio.run(run_styling(args.json, args.style, args.output))
