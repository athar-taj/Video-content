from typing import List, Set

class TagManager:
    """
    Manages asset tagging and niche association.
    """
    
    COMMON_TAGS = {
        "horror", "emotional", "suspense", "fast_paced", 
        "dark", "satisfying", "storytelling", "motivational", "funny"
    }

    def __init__(self):
        self.tags: Set[str] = self.COMMON_TAGS

    def add_tag(self, tag: str):
        self.tags.add(tag.lower())

    def get_common_tags(self) -> List[str]:
        return sorted(list(self.tags))

    def suggest_tags(self, niche: str) -> List[str]:
        """
        Suggests tags based on content niche.
        """
        suggestions = {
            "horror": ["dark", "suspense"],
            "motivation": ["fast_paced", "motivational"],
            "relationship": ["emotional", "storytelling"],
            "confessions": ["satisfying", "funny"]
        }
        return suggestions.get(niche.lower(), [])
