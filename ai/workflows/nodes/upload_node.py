import logging
import asyncio
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def upload_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Executing Upload Node...")
    
    render_output_path = state.get("render_output_path")
    if not render_output_path:
        logger.warning("No video to upload. Skipping upload stage.")
        return {}
        
    logger.info(f"Uploading {render_output_path} to YouTube Shorts & TikTok...")
    # Simulate upload latency
    await asyncio.sleep(1.0)
    
    logger.info("Upload completed successfully!")
    
    state_metadata = state.get("execution_metadata", {})
    state_metadata["upload_status"] = "success"
    state_metadata["youtube_video_id"] = "shorts_mock_12345"
    state_metadata["tiktok_video_id"] = "tiktok_mock_67890"
    
    return {
        "execution_metadata": state_metadata
    }
