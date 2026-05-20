from typing import List, Optional, Dict, Any
from ai.video_assets.management.models import VideoAsset, AssetSearchResult
from db.repositories.manager import db_manager
from db.models.video import VideoAssetModel
from sqlalchemy import select, or_, and_

class AssetSearchEngine:
    """
    Search engine for retrieving assets from the database with various filters.
    """
    
    async def search_assets(self, 
                            query: Optional[str] = None,
                            category: Optional[str] = None,
                            niche: Optional[str] = None,
                            tags: Optional[List[str]] = None,
                            orientation: Optional[str] = None,
                            min_duration: Optional[float] = None,
                            max_duration: Optional[float] = None) -> List[VideoAssetModel]:
        """
        Executes a database search with filters.
        """
        async with db_manager.session_factory() as session:
            stmt = select(VideoAssetModel)
            filters = []
            
            if category:
                filters.append(VideoAssetModel.category == category)
            if niche:
                filters.append(VideoAssetModel.niche == niche)
            if orientation:
                filters.append(VideoAssetModel.orientation == orientation)
            if min_duration is not None:
                filters.append(VideoAssetModel.duration_seconds >= min_duration)
            if max_duration is not None:
                filters.append(VideoAssetModel.duration_seconds <= max_duration)
            if tags:
                # Assuming tags is a JSON column in DB
                for tag in tags:
                    filters.append(VideoAssetModel.tags.contains([tag]))
            
            if query:
                filters.append(VideoAssetModel.asset_name.ilike(f"%{query}%"))
                
            if filters:
                stmt = stmt.where(and_(*filters))
                
            result = await session.execute(stmt)
            return result.scalars().all()

    async def search_by_tag(self, tag: str) -> List[VideoAssetModel]:
        return await self.search_assets(tags=[tag])

    async def search_by_category(self, category: str) -> List[VideoAssetModel]:
        return await self.search_assets(category=category)
