from ai.subtitles.styling.models import CaptionStyle
from ai.subtitles.styling.font_manager import FontManager

class StyleValidator:
    def __init__(self):
        self.font_manager = FontManager()

    def validate_style(self, style: CaptionStyle) -> bool:
        """
        Validates a caption style configuration.
        """
        # Validate font
        if not self.font_manager.validate_font(style.font_config.font_family):
            return False
            
        # Validate colors (basic regex for &HAABBGGRR)
        import re
        color_pattern = r'^&H[0-9A-Fa-f]{8}$'
        for color in [style.primary_color, style.secondary_color, style.outline_color, style.shadow_color]:
            if not re.match(color_pattern, color):
                return False
                
        return True
