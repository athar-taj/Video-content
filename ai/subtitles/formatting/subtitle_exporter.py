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

    def _parse_segments(self, segments) -> List[SubtitleSegment]:
        from ai.subtitles.formatting.models import SubtitleSegment as FormattedSubtitleSegment, SubtitleWord
        parsed = []
        for s in segments:
            if isinstance(s, dict):
                words = []
                for w in s.get("words", []):
                    if isinstance(w, dict):
                        words.append(SubtitleWord(
                            word=w.get("word", ""),
                            start_time=w.get("start_time", 0.0),
                            end_time=w.get("end_time", 0.0),
                            confidence=w.get("confidence", 1.0)
                        ))
                    else:
                        words.append(SubtitleWord(
                            word=getattr(w, "word", ""),
                            start_time=getattr(w, "start_time", 0.0),
                            end_time=getattr(w, "end_time", 0.0),
                            confidence=getattr(w, "confidence", 1.0)
                        ))
                parsed.append(FormattedSubtitleSegment(
                    segment_id=str(s.get("segment_id", "")),
                    text=s.get("text", ""),
                    words=words,
                    start_time=s.get("start_time", 0.0),
                    end_time=s.get("end_time", 0.0),
                    duration=s.get("duration", 0.0)
                ))
            else:
                words = []
                for w in getattr(s, "words", []):
                    words.append(SubtitleWord(
                        word=getattr(w, "word", ""),
                        start_time=getattr(w, "start_time", 0.0),
                        end_time=getattr(w, "end_time", 0.0),
                        confidence=getattr(w, "confidence", 1.0)
                    ))
                parsed.append(FormattedSubtitleSegment(
                    segment_id=str(getattr(s, "segment_id", "")),
                    text=getattr(s, "text", ""),
                    words=words,
                    start_time=getattr(s, "start_time", 0.0),
                    end_time=getattr(s, "end_time", 0.0),
                    duration=getattr(s, "duration", 0.0)
                ))
        return parsed

    def to_json(self, segments, path: str):
        parsed = self._parse_segments(segments)
        content = self.serializer.serialize(parsed, "json")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def to_srt(self, segments, path: str):
        parsed = self._parse_segments(segments)
        content = self.serializer.serialize(parsed, "srt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def to_ass_karaoke(self, segments, path: str):
        parsed = self._parse_segments(segments)
        content = self.serializer.serialize(parsed, "karaoke")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
