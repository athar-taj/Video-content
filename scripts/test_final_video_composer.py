import asyncio
import logging
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.rendering.composer import FinalVideoComposer, RenderJob

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_final_video_composer")

async def test_composer():
    logger.info("Executing test_final_video_composer.py")
    
    ffmpeg_path = "C:\\Users\\athar\\AppData\\Local\\Microsoft\\WinGet\\Packages\\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\\ffmpeg-8.1.1-full_build\\bin\\ffmpeg.exe"
    
    # We will use the assets generated previously
    video_path = os.path.join("assets", "input", "video", "gameplay_test.mp4")
    narration_path = os.path.join("assets", "input", "audio", "narration_test.mp3")
    subtitle_path = os.path.join("assets", "ass", "test_captions.ass") # Assuming this exists from previous step
    
    # Create an empty overlay PNG for testing if watermark doesn't exist
    overlay_path = os.path.join("assets", "input", "video", "watermark.png")
    
    final_output_path = os.path.join("assets", "renders", "test_final_composed_video.mp4")
    os.makedirs(os.path.dirname(final_output_path), exist_ok=True)

    job = RenderJob(
        job_id="test_composer_001",
        script_id="test_script_001",
        narration_path=narration_path,
        background_video_path=video_path,
        subtitle_path=subtitle_path if os.path.exists(subtitle_path) else None,
        output_path=final_output_path,
        resolution="1080x1920"
    )

    try:
        composer = FinalVideoComposer(ffmpeg_path=ffmpeg_path)
        
        logger.info("Orchestrating the final composition...")
        
        # Test with or without overlay depending on presence
        overlays = [overlay_path] if os.path.exists(overlay_path) else []
        
        output = await composer.compose_video(job, overlay_paths=overlays)
        
        logger.info(f"Test passed. Output video generated at: {output}")
        print(f"\n=== TEST SUCCESS: {output} ===\n")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_composer())
