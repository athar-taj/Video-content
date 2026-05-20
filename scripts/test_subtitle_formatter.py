import asyncio
import os
import sys
from typing import List

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.subtitles.formatting.models import SubtitleSegment, SubtitleWord
from ai.subtitles.formatting.subtitle_exporter import SubtitleExporter
from ai.subtitles.formatting.validators import SubtitleValidator

async def test_formatter():
    print("Testing Subtitle Formatter System...")
    
    # Mock data
    words = [
        SubtitleWord(word="Hello", start_time=1.0, end_time=1.5, confidence=0.99),
        SubtitleWord(word="world", start_time=1.6, end_time=2.0, confidence=0.98),
        SubtitleWord(word="this", start_time=2.1, end_time=2.3, confidence=0.97),
        SubtitleWord(word="is", start_time=2.4, end_time=2.5, confidence=0.96),
        SubtitleWord(word="Zem", start_time=2.6, end_time=3.0, confidence=0.95),
    ]
    
    segments = [
        SubtitleSegment(
            segment_id="test_1",
            text="Hello world this is Zem",
            words=words,
            start_time=1.0,
            end_time=3.0,
            duration=2.0
        )
    ]
    
    exporter = SubtitleExporter(base_dir="assets/subtitles_test")
    validator = SubtitleValidator()
    
    # 1. Validate
    if validator.validate_segments(segments):
        print("✅ Segments validation passed")
    else:
        print("❌ Segments validation failed")
        return

    # 2. Export SRT
    srt_path = await exporter.export(segments, "srt", "test_script")
    print(f"✅ SRT exported to {srt_path}")
    
    # 3. Export JSON
    json_path = await exporter.export(segments, "json", "test_script")
    print(f"✅ JSON exported to {json_path}")
    
    # 4. Export Karaoke (ASS)
    karaoke_path = await exporter.export(segments, "karaoke", "test_script")
    print(f"✅ Karaoke ASS exported to {karaoke_path}")

    # Print previews
    print("\n--- SRT PREVIEW ---")
    with open(srt_path, "r") as f:
        print(f.read())

    print("\n--- JSON PREVIEW ---")
    with open(json_path, "r") as f:
        import json
        data = json.load(f)
        print(json.dumps(data, indent=2))

    print("\n--- KARAOKE ASS PREVIEW (First few lines) ---")
    with open(karaoke_path, "r") as f:
        lines = f.readlines()
        print("".join(lines[-3:])) # Show the events

if __name__ == "__main__":
    asyncio.run(test_formatter())
