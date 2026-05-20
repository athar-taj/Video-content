import asyncio
import logging
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.rendering.captions import CaptionBurner, CaptionRenderJob, AnimationProfile

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_caption_burn")

async def test_burn():
    logger.info("Executing test_caption_burn.py")
    
    ffmpeg_path = "C:\\Users\\athar\\AppData\\Local\\Microsoft\\WinGet\\Packages\\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\\ffmpeg-8.1.1-full_build\\bin\\ffmpeg.exe"
    
    # We will use the gameplay_test.mp4 generated in the previous task as the input
    video_path = os.path.join("assets", "input", "video", "gameplay_test.mp4")
    ass_output_path = os.path.join("assets", "ass", "test_captions.ass")
    final_output_path = os.path.join("assets", "rendered_captions", "test_captioned_output.mp4")
    
    # Ensure directories exist
    os.makedirs(os.path.dirname(ass_output_path), exist_ok=True)
    os.makedirs(os.path.dirname(final_output_path), exist_ok=True)

    # Basic ASS Validation by actually generating and burning
    job = CaptionRenderJob(
        job_id="test_job_001",
        render_id="test_render_001",
        subtitle_path=ass_output_path,
        video_path=video_path,
        output_path=final_output_path,
        animation_profile=AnimationProfile.HORROR
    )
    
    dialogue_data = [
        {
            "start": "0:00:00.00",
            "end": "0:00:03.00",
            "words": [
                {"word": "Spooky", "duration_ms": 1000},
                {"word": "animated", "duration_ms": 1000},
                {"word": "text...", "duration_ms": 1000}
            ]
        }
    ]

    try:
        burner = CaptionBurner(ffmpeg_path=ffmpeg_path)
        
        logger.info("Generating ASS Captions...")
        burner.generate_ass_file(
            job=job,
            dialogue_lines=dialogue_data,
            animation_type="fade",
            position="center"
        )
        
        logger.info("Burning Captions Into Video...")
        output = await burner.burn_subtitles(job)
        
        logger.info(f"Test passed. Output video generated at: {output}")
        print(f"\n=== TEST SUCCESS: {output} ===\n")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_burn())
