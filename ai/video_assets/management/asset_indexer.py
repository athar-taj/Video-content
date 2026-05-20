import os
import uuid
import logging
import asyncio
from pathlib import Path
from typing import List, Dict, Optional
from ai.video_assets.management.models import VideoAsset, AssetStatus
from ai.video_assets.management.metadata_extractor import MetadataExtractor
from ai.video_assets.management.validators import AssetValidator
from ai.video_assets.management.duplicate_detector import DuplicateDetector

logger = logging.getLogger(__name__)

class AssetIndexer:
    """
    Indexes local video assets by scanning directories and extracting metadata.
    """
    
    def __init__(self, base_dir: str = "assets/videos"):
        self.base_dir = Path(base_dir)
        self.extractor = MetadataExtractor()
        self.validator = AssetValidator()
        self.duplicate_detector = DuplicateDetector()

    async def scan_assets(self, categories: List[str]) -> List[VideoAsset]:
        """
        Recursively scans directories for each category.
        """
        indexed_assets = []
        for category in categories:
            cat_path = self.base_dir / category
            if not cat_path.exists():
                logger.warning(f"Category path does not exist: {cat_path}")
                continue
                
            logger.info(f"Scanning category: {category}")
            for file_path in cat_path.rglob("*.mp4"):
                try:
                    asset = await self.index_asset(str(file_path), category)
                    if asset:
                        indexed_assets.append(asset)
                except Exception as e:
                    logger.error(f"Failed to index {file_path}: {e}")
                    
        return indexed_assets

    async def index_asset(self, file_path: str, category: str) -> Optional[VideoAsset]:
        """
        Extracts metadata, calculates checksum, validates, and returns VideoAsset.
        """
        # Metadata
        metadata = self.extractor.get_metadata(file_path)
        
        # Validation
        if not self.validator.validate(metadata):
            logger.warning(f"Asset validation failed: {file_path}")
            return None
            
        # Checksum
        checksum = self.duplicate_detector.calculate_checksum(file_path)
        
        # Create Asset Model
        asset = VideoAsset(
            id=str(uuid.uuid4())[:8],
            asset_name=os.path.basename(file_path),
            category=category,
            local_path=str(Path(file_path).absolute()),
            checksum=checksum,
            resolution=metadata['resolution'],
            fps=metadata['fps'],
            bitrate=metadata['bitrate'],
            codec=metadata['codec'],
            duration_seconds=metadata['duration_seconds'],
            aspect_ratio=metadata['aspect_ratio'],
            orientation=metadata['orientation'],
            status=AssetStatus.INDEXED,
            tags=[category] # Default tag
        )
        return asset
