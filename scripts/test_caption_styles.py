import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.subtitles.styling.caption_style_manager import CaptionStyleManager
from ai.subtitles.formatting.models import SubtitleSegment, SubtitleWord

async def test_styles():
    print("Testing Caption Styling System...")
    
    # Mock data
    words = [
        SubtitleWord(word="Success", start_time=1.0, end_time=1.5, confidence=0.99),
        SubtitleWord(word="is", start_time=1.6, end_time=1.8, confidence=0.98),
        SubtitleWord(word="not", start_time=1.9, end_time=2.1, confidence=0.97),
        SubtitleWord(word="final", start_time=2.2, end_time=3.0, confidence=0.96),
    ]
    
    segments = [
        SubtitleSegment(
            segment_id="test_s1",
            text="Success is not final",
            words=words,
            start_time=1.0,
            end_time=3.0,
            duration=2.0
        )
    ]
    
    manager = CaptionStyleManager()
    
    styles_to_test = ["tiktok_bold", "reels_clean", "horror_red", "motivational_pop"]
    
    for style in styles_to_test:
        print(f"\n--- Testing Style: {style} ---")
        try:
            ass_content = manager.generate_styled_ass(segments, style)
            # Print first 20 lines of header and first event
            lines = ass_content.split("\n")
            print("\n".join(lines[:12])) # Header
            print("...")
            for line in lines:
                if line.startswith("Dialogue:"):
                    print(line)
                    break
            print(f"✅ {style} generated successfully")
        except Exception as e:
            print(f"❌ {style} failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_styles())
