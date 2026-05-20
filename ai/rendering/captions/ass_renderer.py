import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class ASSRenderer:
    """Renders ASS subtitle strings from text and animations."""
    
    # Predefined styles based on profiles (Step 8)
    STYLES = {
        "tiktok_bold": "Style: Default,Arial,60,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,2,2,10,10,100,1",
        "horror_glow": "Style: Default,Impact,70,&H000000FF,&H000000FF,&H000000FF,&H00000000,-1,0,0,0,100,100,0,0,1,4,4,2,10,10,100,1",
        "motivational_pop": "Style: Default,Verdana,65,&H0000FFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,3,3,2,10,10,100,1",
        "storytelling_classic": "Style: Default,Arial,50,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,1,1,2,10,10,100,1"
    }

    def _get_header(self, width: int = 1080, height: int = 1920) -> str:
        return f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
"""

    def generate_ass_content(self, dialogue_lines: List[Dict], profile: str = "tiktok_bold") -> str:
        """Generate full ASS file content."""
        logger.info(f"Generating ASS content for profile: {profile}")
        
        style_line = self.STYLES.get(profile, self.STYLES["tiktok_bold"])
        content = self._get_header() + style_line + "\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        
        for line in dialogue_lines:
            # Example line: {"start": "0:00:00.00", "end": "0:00:02.00", "text": "Hello world", "effect": ""}
            start = line.get("start", "0:00:00.00")
            end = line.get("end", "0:00:01.00")
            text = line.get("text", "")
            effect = line.get("effect", "")
            
            content += f"Dialogue: 0,{start},{end},Default,,0,0,0,,{effect}{text}\n"
            
        return content
