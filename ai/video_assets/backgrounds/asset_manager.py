import os
import hashlib
import uuid
import logging
from pathlib import Path
from typing import List, Optional, Dict
from ai.video_assets.backgrounds.models import VideoAsset
from ai.video_assets.backgrounds.metadata_extractor import MetadataExtractor
from ai.video_assets.backgrounds.validators import AssetValidator

logger = logging.getLogger(__name__)

class AssetManager:
    """
    Manages the lifecycle and indexing of background video assets.
    """
    
    def __init__(self, base_dir: str = "assets/videos"):
        self.base_dir = Path(base_dir)
        self.extractor = MetadataExtractor()
        self.validator = AssetValidator()

    def _calculate_checksum(self, file_path: str) -> str:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    async def register_asset(self, file_path: str, category: str, niche: Optional[str] = None, tags: List[str] = []) -> VideoAsset:
        """
        Extracts metadata, validates, and creates a VideoAsset model.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Asset file not found: {file_path}")
            
        metadata = self.extractor.get_metadata(file_path)
        if not self.validator.validate(metadata):
            raise ValueError(f"Asset validation failed for {file_path}")
            
        checksum = self._calculate_checksum(file_path)
        
        asset = VideoAsset(
            id=str(uuid.uuid4())[:8],
            asset_name=path.name,
            category=category,
            niche=niche,
            source="local",
            resolution=metadata['resolution'],
            fps=metadata['fps'],
            duration_seconds=metadata['duration'],
            file_size=path.stat().st_size,
            aspect_ratio=metadata['aspect_ratio'],
            tags=tags,
            local_path=str(path.absolute()),
            checksum=checksum
        )
        return asset

    async def scan_directory(self, category: str) -> List[VideoAsset]:
        """
        Scans a specific category directory and registers new assets.
        """
        dir_path = self.base_dir / category
        if not dir_path.exists():
            return []
            
        assets = []
        for file in dir_path.glob("*.mp4"):
            try:
                # In a real system, we'd check if checksum already exists in DB
                asset = await self.register_asset(str(file), category)
                assets.append(asset)
            except Exception as e:
                logger.error(f"Error scanning {file}: {e}")
                
        return assets
