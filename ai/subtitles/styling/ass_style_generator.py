from ai.subtitles.styling.models import CaptionStyle

class ASSStyleGenerator:
    """
    Generates ASS style definitions from CaptionStyle models.
    """
    
    def generate_style_line(self, style: CaptionStyle) -> str:
        """
        Formats: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, 
        Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, 
        Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
        """
        # Primary, Secondary, Outline, Back are &HAABBGGRR
        # Bold: -1 for True, 0 for False
        bold = -1 if style.font_config.font_weight >= 700 else 0
        italic = -1 if style.font_config.is_italic else 0
        underline = -1 if style.font_config.is_underline else 0
        
        parts = [
            f"Style: {style.style_name}",
            style.font_config.font_family,
            str(style.font_config.font_size),
            style.primary_color,
            style.secondary_color,
            style.outline_color,
            style.shadow_color,
            str(bold),
            str(italic),
            str(underline),
            "0", # StrikeOut
            "100", # ScaleX
            "100", # ScaleY
            "0", # Spacing
            "0", # Angle
            "1", # BorderStyle (1=Outline+Shadow)
            str(style.outline_width),
            str(style.shadow_depth),
            str(style.alignment),
            str(style.margin_x),
            str(style.margin_x),
            str(style.margin_y),
            "1" # Encoding
        ]
        return ",".join(parts)

    def generate_header(self, styles: list[CaptionStyle]) -> str:
        lines = [
            "[Script Info]",
            "Title: Zem Styled Subtitles",
            "ScriptType: v4.00+",
            "PlayResX: 1920",
            "PlayResY: 1080",
            "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding"
        ]
        for style in styles:
            lines.append(self.generate_style_line(style))
            
        lines.extend([
            "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
        ])
        return "\n".join(lines)
