import os
import logging
from typing import Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class FontManager:
    """
    Manages font loading, registration, and validation.
    """
    def __init__(self, font_dir: str = "assets/fonts"):
        self.font_dir = Path(font_dir)
        self.font_dir.mkdir(parents=True, exist_ok=True)
        self.registry: Dict[str, Path] = {}
        self._load_local_fonts()

    def _load_local_fonts(self):
        """
        Scans the font directory for available fonts.
        """
        for ext in [".ttf", ".otf"]:
            for font_file in self.font_dir.glob(f"*{ext}"):
                self.registry[font_file.stem.lower()] = font_file
        logger.info(f"Loaded {len(self.registry)} fonts from {self.font_dir}")

    def load_font(self, font_name: str) -> Optional[Path]:
        return self.registry.get(font_name.lower())

    def register_font(self, font_path: str) -> bool:
        path = Path(font_path)
        if not path.exists():
            return False
        
        # Copy to font dir if not already there? 
        # For now, just register the path
        self.registry[path.stem.lower()] = path
        return True

    def validate_font(self, font_name: str) -> bool:
        """
        Checks if the font exists in the registry or system (rough check).
        """
        if font_name.lower() in self.registry:
            return True
        
        # Simple fallback check for common system fonts
        common_fonts = ["arial", "roboto", "inter", "helvetica", "verdana", "tahoma"]
        return font_name.lower() in common_fonts

    def get_fallback_font(self) -> str:
        return "Arial"
