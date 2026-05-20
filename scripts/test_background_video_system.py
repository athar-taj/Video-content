import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.video_assets.backgrounds.asset_manager import AssetManager
from ai.video_assets.backgrounds.video_selector import VideoSelector
from ai.video_assets.backgrounds.duration_trimmer import DurationTrimmer
from ai.video_assets.backgrounds.gameplay_router import GameplayRouter

async def test_video_system():
    print("Testing Background Video System...")
    
    # Check for test video
    test_video = "assets/videos/gameplay/test_background.mp4"
    if not os.path.exists(test_video):
        print(f"⚠️ Test video not found at {test_video}. Please place an mp4 file there to run the full test.")
        return

    manager = AssetManager()
    router = GameplayRouter()
    trimmer = DurationTrimmer(temp_dir="assets/videos_test/temp")
    
    # 1. Register
    print(f"Registering {test_video}...")
    asset = await manager.register_asset(test_video, "gameplay", niche="horror", tags=["dark"])
    print(f"✅ Registered: {asset.asset_name} ({asset.resolution}, {asset.duration_seconds}s)")
    
    # 2. Select
    print("Testing Selection...")
    selector = VideoSelector([asset])
    # Mock redis for test
    from unittest.mock import MagicMock
    import shared.redis.client as redis_client
    redis_client.redis_manager.connect = MagicMock(return_value=asyncio.Future())
    redis_client.redis_manager.connect.return_value.set_result(None)
    redis_client.redis_manager.get_cache = MagicMock(return_value=asyncio.Future())
    redis_client.redis_manager.get_cache.return_value.set_result(None)
    
    selected = await selector.select_video("gameplay", 5.0, ["dark"])
    if selected:
        print(f"✅ Selected: {selected.asset_name}")
    else:
        print("❌ Selection failed")
        return
        
    # 3. Trim
    print("Testing Trimming (5 seconds)...")
    output_path = "assets/videos_test/test_clip.mp4"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        processed = trimmer.trim_video(selected.local_path, 5.0, output_path)
        print(f"✅ Trimmed clip created at {processed}")
        print(f"File size: {os.path.getsize(processed)} bytes")
    except Exception as e:
        print(f"❌ Trimming failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_video_system())
