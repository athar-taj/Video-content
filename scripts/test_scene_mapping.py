import asyncio
import logging
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.video_assets.scene_mapping import SceneMapper

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_scene_mapping")

async def test_mapping():
    logger.info("Executing test_scene_mapping.py")
    
    script_data = {
        "sections": [
            {"type": "hook", "text": "This is a scary hook!"},
            {"type": "climax", "text": "And here is the scary climax!"}
        ]
    }
    
    narration_duration = 8.0 # seconds
    script_id = "test_horror_001"
    
    try:
        mapper = SceneMapper()
        timeline_json = await mapper.generate_timeline(
            script_id=script_id,
            script_data=script_data,
            narration_duration=narration_duration
        )
        
        logger.info("Test passed. Timeline successfully generated.")
        print("\n=== TEST OUTPUT ===")
        print(timeline_json)
        print("===================\n")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_mapping())
