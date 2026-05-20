import asyncio
import logging
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.rendering.captions import CaptionBurner, CaptionRenderJob, AnimationProfile
from ai.rendering.captions.models import RenderStatus

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("run_caption_burn")

async def main():
    logger.info("Starting Caption Burn Execution Script")
    
    ffmpeg_path = "C:\\Users\\athar\\AppData\\Local\\Microsoft\\WinGet\\Packages\\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\\ffmpeg-8.1.1-full_build\\bin\\ffmpeg.exe"
    
    # Input/Output paths
    video_path = os.path.join("assets", "input", "video", "gameplay_test.mp4")
    ass_output_path = os.path.join("assets", "ass", "generated_captions.ass")
    final_output_path = os.path.join("assets", "rendered_captions", "captioned_output.mp4")
    
    # Ensure directories exist
    os.makedirs(os.path.dirname(ass_output_path), exist_ok=True)
    os.makedirs(os.path.dirname(final_output_path), exist_ok=True)

    job = CaptionRenderJob(
        job_id="job_001",
        render_id="render_test_001",
        subtitle_path=ass_output_path,
        video_path=video_path,
        output_path=final_output_path,
        animation_profile=AnimationProfile.MOTIVATION
    )
    
    # Dummy dialogue data with karaoke timing
    dialogue_data = [
        {
            "start": "0:00:00.00",
            "end": "0:00:02.50",
            "words": [
                {"word": "This", "duration_ms": 300},
                {"word": "is", "duration_ms": 200},
                {"word": "an", "duration_ms": 300},
                {"word": "animated", "duration_ms": 700},
                {"word": "caption!", "duration_ms": 1000}
            ]
        },
        {
            "start": "0:00:02.50",
            "end": "0:00:05.00",
            "text": "It uses ASS styling and effects.", # Plain text fallback
        }
    ]

    try:
        burner = CaptionBurner(ffmpeg_path=ffmpeg_path)
        
        # 1. Generate ASS
        burner.generate_ass_file(
            job=job,
            dialogue_lines=dialogue_data,
            animation_type="pop",
            position="center"
        )
        
        # 2. Burn into video
        logger.info(f"Burning captions using profile: {job.animation_profile.value}")
        await burner.burn_subtitles(job)
        
        logger.info(f"Render completed: {final_output_path}")
        
    except Exception as e:
        logger.error(f"Render pipeline failed: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
