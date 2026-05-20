import asyncio
import logging
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.rendering.composer import FinalVideoComposer, RenderJob, ExportManager

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("run_final_video_composer")

async def main():
    logger.info("Starting Final Video Composer Execution Script")
    
    ffmpeg_path = "C:\\Users\\athar\\AppData\\Local\\Microsoft\\WinGet\\Packages\\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\\ffmpeg-8.1.1-full_build\\bin\\ffmpeg.exe"
    
    # Input/Output paths
    video_path = os.path.join("assets", "input", "video", "gameplay_test.mp4")
    narration_path = os.path.join("assets", "input", "audio", "narration_test.mp3")
    subtitle_path = os.path.join("assets", "ass", "test_captions.ass") # From previous task
    overlay_path = os.path.join("assets", "input", "video", "watermark.png")
    final_output_path = os.path.join("assets", "renders", "final_composed_video.mp4")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(final_output_path), exist_ok=True)

    job = RenderJob(
        job_id="final_job_001",
        script_id="script_test_001",
        narration_path=narration_path,
        background_video_path=video_path,
        subtitle_path=subtitle_path if os.path.exists(subtitle_path) else None,
        output_path=final_output_path,
        resolution="1080x1920"
    )
    
    try:
        composer = FinalVideoComposer(ffmpeg_path=ffmpeg_path)
        
        logger.info("Composing final video...")
        
        # We pass the overlay path if it exists
        overlays = [overlay_path] if os.path.exists(overlay_path) else []
        
        output = await composer.compose_video(job, overlay_paths=overlays)
        
        # Export / Archive
        export_mgr = ExportManager()
        archive_path = export_mgr.archive_render(job)
        
        logger.info(f"Final composition complete. Rendered to: {output}")
        logger.info(f"Archived to: {archive_path}")
        
    except Exception as e:
        logger.error(f"Final render pipeline failed: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
