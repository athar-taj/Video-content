import asyncio
import logging
import json
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.video_assets.scene_mapping import SceneMapper

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("run_scene_mapping")

async def main():
    logger.info("Starting Scene Mapping Execution Script")
    
    # Dummy script data for execution
    script_data = {
        "sections": [
            {"type": "hook", "text": "Are you making these 3 mistakes in Minecraft?"},
            {"type": "setup", "text": "Most players ignore the Y-level when mining for diamonds."},
            {"type": "climax", "text": "But the truth is, the new update changed everything!"},
            {"type": "emotional", "text": "Stop wasting hours and try this instead."},
            {"type": "cta", "text": "Subscribe for more tips!"}
        ]
    }
    
    narration_duration = 15.0 # seconds
    script_id = "test_script_001"
    
    try:
        mapper = SceneMapper()
        timeline_json = await mapper.generate_timeline(
            script_id=script_id,
            script_data=script_data,
            narration_duration=narration_duration
        )
        
        output_path = os.path.join("assets", "timelines", f"{script_id}.json")
        with open(output_path, "w") as f:
            f.write(timeline_json)
            
        logger.info(f"Successfully generated timeline: {output_path}")
        print("\nTimeline JSON Output:\n")
        print(timeline_json)
        
    except Exception as e:
        logger.error(f"Failed to generate scene mapping: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
