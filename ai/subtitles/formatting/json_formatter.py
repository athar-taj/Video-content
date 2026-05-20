import json
from typing import List, Dict, Any
from ai.subtitles.formatting.models import SubtitleSegment

class JSONFormatter:
    """
    Generates structured subtitle JSON for frontend/rendering.
    """

    def generate_json(self, segments: List[SubtitleSegment], metadata: Dict[str, Any] = None) -> str:
        """
        Generates a JSON string representing the subtitles.
        """
        data = {
            "segments": [seg.model_dump() for seg in segments],
            "metadata": metadata or {}
        }
        return json.dumps(data, indent=2, ensure_ascii=False)
