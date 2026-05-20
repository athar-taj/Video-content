from typing import List, Dict

class CategoryManager:
    """
    Manages asset categories and their corresponding paths.
    """
    
    DEFAULT_CATEGORIES = {
        "gameplay": "assets/videos/gameplay",
        "cinematic": "assets/videos/cinematic",
        "memes": "assets/videos/memes",
        "stock": "assets/videos/stock",
        "loops": "assets/videos/loops",
        "ai_generated": "assets/videos/ai_generated",
        "archived": "assets/videos/archived"
    }

    def __init__(self, custom_categories: Dict[str, str] = None):
        self.categories = {**self.DEFAULT_CATEGORIES, **(custom_categories or {})}

    def get_all_categories(self) -> List[str]:
        return list(self.categories.keys())

    def get_path(self, category: str) -> str:
        return self.categories.get(category)
