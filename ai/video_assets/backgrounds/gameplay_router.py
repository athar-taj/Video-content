from typing import Dict, List, Optional

class GameplayRouter:
    """
    Routes content niches to appropriate video categories or tags.
    """
    
    DEFAULT_ROUTING = {
        "horror": {"category": "gameplay", "tags": ["dark", "suspense"]},
        "relationship": {"category": "cinematic", "tags": ["slow", "emotional"]},
        "motivation": {"category": "gameplay", "tags": ["fast", "energetic"]},
        "confessions": {"category": "gameplay", "tags": ["satisfying", "subway_surfers"]},
        "talesfromtechsupport": {"category": "gameplay", "tags": ["satisfying", "minecraft"]},
        "storytelling": {"category": "cinematic", "tags": ["nature", "loops"]}
    }

    def __init__(self, custom_routing: Optional[Dict[str, Dict]] = None):
        self.routing = {**self.DEFAULT_ROUTING, **(custom_routing or {})}

    def get_route(self, niche: str) -> Dict[str, Any]:
        """
        Returns the category and tags for a given niche.
        """
        return self.routing.get(niche.lower(), {"category": "gameplay", "tags": []})
