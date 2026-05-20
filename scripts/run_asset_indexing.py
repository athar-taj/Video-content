import asyncio
import argparse
import os
import sys
from typing import List

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.video_assets.management.asset_indexer import AssetIndexer
from ai.video_assets.management.category_manager import CategoryManager
from db.repositories.manager import db_manager
from db.models.video import VideoAssetModel
from shared.logging.logger import log
from sqlalchemy import select

async def run_indexing(categories: List[str] = None):
    log.info("Starting automated asset indexing...")
    
    cat_manager = CategoryManager()
    if not categories:
        categories = cat_manager.get_all_categories()
        
    indexer = AssetIndexer()
    assets = await indexer.scan_assets(categories)
    
    async with db_manager.session_factory() as session:
        # Get existing checksums to avoid duplicates
        result = await session.execute(select(VideoAssetModel.checksum))
        existing_checksums = set(result.scalars().all())
        
        new_count = 0
        for asset in assets:
            if asset.checksum in existing_checksums:
                continue
                
            model = VideoAssetModel(
                id=asset.id,
                asset_name=asset.asset_name,
                category=asset.category,
                local_path=asset.local_path,
                checksum=asset.checksum,
                resolution=asset.resolution,
                fps=asset.fps,
                bitrate=asset.bitrate,
                codec=asset.codec,
                duration_seconds=asset.duration_seconds,
                aspect_ratio=asset.aspect_ratio,
                orientation=asset.orientation,
                tags=asset.tags,
                status=asset.status.value
            )
            session.add(model)
            new_count += 1
            
        await session.commit()
        log.info(f"Indexing complete. Indexed {len(assets)} assets, {new_count} new assets added to DB.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zem Asset Indexing Engine")
    parser.add_argument("--categories", nargs="+", help="Specific categories to scan")
    
    args = parser.parse_args()
    
    asyncio.run(run_indexing(args.categories))
