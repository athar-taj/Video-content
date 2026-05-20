import os
from pathlib import Path
from typing import List, Optional
from ai.subtitles.formatting.models import SubtitleSegment
from ai.subtitles.formatting.subtitle_serializer import SubtitleSerializer

class SubtitleExporter:
    """
    Handles file export and directory management for subtitles.
    """

    def __init__(self, base_dir: str = "assets/subtitles"):
        self.base_dir = Path(base_dir)
        self.serializer = SubtitleSerializer()
        
        # Create subdirectories
        (self.base_dir / "srt").mkdir(parents=True, exist_ok=True)
        (self.base_dir / "json").mkdir(parents=True, exist_ok=True)
        (self.base_dir / "ass").mkdir(parents=True, exist_ok=True)
        (self.base_dir / "temp").mkdir(parents=True, exist_ok=True)

    def generate_output_path(self, script_id: str, language: str, format_type: str) -> Path:
        """
        Generates a deterministic filename: {script_id}_{language}_{format}.ext
        """
        ext = format_type.lower()
        if ext == "karaoke":
            ext = "ass" # Karaoke is a variation of ASS
            
        subdir = format_type.lower()
        if subdir == "karaoke":
            subdir = "ass"
            
        filename = f"{script_id}_{language}_{format_type.lower()}.{ext}"
        return self.base_dir / subdir / filename

    async def export(self, segments: List[SubtitleSegment], format_type: str, script_id: str, language: str = "en", **kwargs) -> Path:
        """
        Serializes and saves subtitles to the appropriate directory.
        """
        content = self.serializer.serialize(segments, format_type, **kwargs)
        output_path = self.generate_output_path(script_id, language, format_type)
        
        # Ensure parent exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return output_path
