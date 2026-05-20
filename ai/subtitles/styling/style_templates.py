from ai.subtitles.styling.models import CaptionStyle, FontConfig, HighlightConfig, AnimationConfig, TransitionType

TIKTOK_BOLD = CaptionStyle(
    style_name="tiktok_bold",
    font_config=FontConfig(font_family="Arial Black", font_size=70),
    primary_color="&H0000FFFF", # Yellow
    outline_color="&H00000000",
    outline_width=4,
    highlight_config=HighlightConfig(highlight_style="scale", scale_factor=1.3)
)

REELS_CLEAN = CaptionStyle(
    style_name="reels_clean",
    font_config=FontConfig(font_family="Roboto", font_size=55),
    primary_color="&H00FFFFFF", # White
    outline_color="&H00333333",
    outline_width=2,
    highlight_config=HighlightConfig(highlight_style="active_color", active_color="&H00FF9900") # Blue-ish
)

HORROR_RED = CaptionStyle(
    style_name="horror_red",
    font_config=FontConfig(font_family="Courier New", font_size=65),
    primary_color="&H000000FF", # Red
    outline_color="&H00000000",
    shadow_depth=3,
    animation_config=AnimationConfig(animation_name="shake", transition_type=TransitionType.SHAKE)
)

MOTIVATIONAL_POP = CaptionStyle(
    style_name="motivational_pop",
    font_config=FontConfig(font_family="Impact", font_size=80),
    primary_color="&H00FFFFFF",
    outline_color="&H00000000",
    animation_config=AnimationConfig(animation_name="pop", transition_type=TransitionType.POP)
)

STYLE_TEMPLATES = {
    "tiktok_bold": TIKTOK_BOLD,
    "reels_clean": REELS_CLEAN,
    "horror_red": HORROR_RED,
    "motivational_pop": MOTIVATIONAL_POP
}
