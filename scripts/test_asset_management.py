import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.video_assets.management.asset_indexer import AssetIndexer
from ai.video_assets.management.asset_search_engine import AssetSearchEngine
from ai.video_assets.management.category_manager import CategoryManager
from ai.video_assets.management.tag_manager import TagManager

async def test_management():
    print("Testing Asset Management System...")
    
    # 1. Indexing Test
    print("\n--- Testing Indexer ---")
    cat_manager = CategoryManager()
    indexer = AssetIndexer()
    
    # Mock some data if folder empty
    test_categories = ["gameplay"]
    assets = await indexer.scan_assets(test_categories)
    print(f"✅ Scanned {len(assets)} assets in categories: {test_categories}")
    
    # 2. Tag Manager Test
    print("\n--- Testing Tag Manager ---")
    tag_manager = TagManager()
    suggestions = tag_manager.suggest_tags("horror")
    print(f"✅ Suggested tags for 'horror': {suggestions}")
    
    # 3. Search Engine Test
    print("\n--- Testing Search Engine ---")
    search_engine = AssetSearchEngine()
    
    # Try searching (will query DB)
    try:
        results = await search_engine.search_assets(category="gameplay")
        print(f"✅ Search found {len(results)} assets in 'gameplay' category")
        
        vertical_results = await search_engine.search_assets(orientation="vertical")
        print(f"✅ Search found {len(vertical_results)} vertical assets")
    except Exception as e:
        print(f"⚠️ Search engine test skipped or failed (DB connection needed): {e}")

if __name__ == "__main__":
    asyncio.run(test_management())
