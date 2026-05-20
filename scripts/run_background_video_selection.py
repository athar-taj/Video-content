import asyncio
import argparse
import os
import sys
import uuid
from typing import Optional

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.video_assets.backgrounds.asset_manager import AssetManager
from ai.video_assets.backgrounds.video_selector import VideoSelector
from ai.video_assets.backgrounds.gameplay_router import GameplayRouter
from ai.video_assets.backgrounds.duration_trimmer import DurationTrimmer
from db.repositories.manager import db_manager
from db.models.video import VideoAssetModel, VideoClipModel, AssetUsageLog
from sqlalchemy import select
from shared.logging.logger import log
from shared.redis.client import redis_manager

async def run_selection(script_id: int, niche: str, duration: float, output_dir: str = "assets/videos/processed"):
    log.info(f"Starting background video selection for script {script_id}, niche {niche}, duration {duration}s")
    
    manager = AssetManager()
    router = GameplayRouter()
    trimmer = DurationTrimmer()
    
    # 1. Fetch assets from DB (or scan if empty)
    async with db_manager.session_factory() as session:
        result = await session.execute(select(VideoAssetModel))
        db_assets = result.scalars().all()
        
        # Simple conversion for selector (in a real system, we'd use Pydantic models throughout)
        from ai.video_assets.backgrounds.models import VideoAsset
        assets = []
        for db_a in db_assets:
            assets.append(VideoAsset(
                id=db_a.id,
                asset_name=db_a.asset_name,
                category=db_a.category,
                niche=db_a.niche,
                resolution=db_a.resolution,
                fps=db_a.fps,
                duration_seconds=db_a.duration_seconds,
                file_size=0, # Not needed for selection
                aspect_ratio="",
                tags=db_a.tags or [],
                local_path=db_a.local_path,
                checksum=db_a.checksum
            ))
            
        if not assets:
            log.warning("No assets in DB. Scanning assets/videos/gameplay...")
            assets = await manager.scan_directory("gameplay")
            # Store in DB
            for a in assets:
                model = VideoAssetModel(
                    id=a.id, asset_name=a.asset_name, category=a.category,
                    niche=a.niche, resolution=a.resolution, duration_seconds=a.duration_seconds,
                    fps=a.fps, checksum=a.checksum, local_path=a.local_path, tags=a.tags
                )
                session.add(model)
            await session.commit()

        # 2. Route and Select
        route = router.get_route(niche)
        selector = VideoSelector(assets)
        
        await redis_manager.connect()
        selected_asset = await selector.select_video(route["category"], duration, route["tags"])
        
        if not selected_asset:
            log.error("Failed to select a suitable video asset")
            return

        log.info(f"Selected asset: {selected_asset.asset_name} ({selected_asset.id})")
        
        # 3. Trim
        os.makedirs(output_dir, exist_ok=True)
        clip_id = str(uuid.uuid4())[:8]
        output_path = os.path.join(output_dir, f"clip_{script_id}_{clip_id}.mp4")
        
        processed_path = trimmer.trim_video(selected_asset.local_path, duration, output_path)
        
        # 4. Store Metadata
        clip_model = VideoClipModel(
            id=clip_id,
            asset_id=selected_asset.id,
            clip_start=0, # Trim script doesn't return exact start yet, but we could add it
            clip_end=duration,
            output_path=processed_path
        )
        session.add(clip_model)
        
        usage_log = AssetUsageLog(
            asset_id=selected_asset.id,
            script_id=script_id,
            usage_duration=duration
        )
        session.add(usage_log)
        
        # Update Redis usage
        cache_key = f"asset_usage:{selected_asset.id}"
        await redis_manager.client.incr(cache_key)
        
        await session.commit()
        log.info(f"Background video processing complete. Clip saved to {processed_path}")
        
    await redis_manager.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zem Background Video Selection Engine")
    parser.add_argument("--script_id", type=int, required=True)
    parser.add_argument("--niche", required=True)
    parser.add_argument("--duration", type=float, required=True)
    parser.add_argument("--output", default="assets/videos/processed")
    
    args = parser.parse_args()
    
    asyncio.run(run_selection(args.script_id, args.niche, args.duration, args.output))
