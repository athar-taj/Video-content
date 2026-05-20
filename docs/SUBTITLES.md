# Subtitle & Word Timestamp Generation System

This system is the core of subtitle synchronization and caption timing for the Zem AI Media Engine. It ensures that every word spoken in the narration is perfectly timed for rendering and animation.

## Architecture

The system is located in `ai/subtitles/` and is divided into several modules:

### 1. Timing Generation (`ai/subtitles/timestamps/`)
- **`TimestampGenerator`**: Orchestrates the transcription pipeline. Uses `faster-whisper` for high-performance local transcription.
- **`TranscriptMatcher`**: A robust alignment tool that compares the original script with the transcription. It uses fuzzy matching to fix gaps where the narrator might have skipped words or changed phrasing.
- **`WordAligner`**: Cleans up raw timestamps, ensures no overlaps, and makes them "rendering-safe".
- **`SilenceDetector`**: Identifies pauses in the audio to improve subtitle duration logic and support dramatic pacing.
- **`TimingOptimizer`**: Transforms raw word timings into readable subtitle segments. It follows "retention-optimized" rules:
    - Max words per segment (e.g., 5 words).
    - Minimum and maximum durations.
    - Punctuation-aware breaking.

### 2. Caption Styling & Animation (`ai/subtitles/styling/`)
- **`CaptionStyleManager`**: The core orchestrator that applies visual themes to subtitles.
- **`FontManager`**: Handles font registration and validation.
- **`AnimationEngine`**: Generates Advanced Substation Alpha (ASS) tags for animations like `fade`, `bounce`, `pop`, `shake`, etc.
- **`HighlightEngine`**: Manages word-level highlighting (e.g., active word color, scaling) and karaoke sync.
- **`ASSStyleGenerator`**: Produces the style headers required for FFmpeg-compatible ASS files.
- **`StyleTemplates`**: Pre-configured visual presets (TikTok Bold, Reels Clean, Horror Red).

### 3. Formatting & Export (`ai/subtitles/formatting/`)
- **`SubtitleSerializer`**: The central engine that coordinates all formatting outputs.
- **`SRTFormatter`**: Generates standard-compliant SRT files with millisecond precision (`HH:MM:SS,mmm`).
- **`JSONFormatter`**: Creates structured JSON payloads preserving full word-level metadata for frontends.
- **`ASSFormatter`**: Prepares Advanced Substation Alpha files for complex styling.
- **`KaraokeFormatter`**: A specialized ASS formatter that injects `\k` centisecond tags for animated "karaoke" highlighting.
- **`SubtitleExporter`**: Handles the physical storage layer:
    - **Deterministic Naming**: Files follow `{script_id}_{language}_{format}.ext`.
    - **Directory Management**: Organizes files into `assets/subtitles/{srt,json,ass,temp}/`.
- **`SubtitleValidator`**: Validates segments for overlaps, empty text, and format-specific structural integrity.

### 3. Storage & Caching
- **Database**: Integrated into PostgreSQL via:
    - `SubtitleGeneration`: Parent record.
    - `FormattedSubtitleModel`: Metadata for each generated file (path, format, size).
    - `SubtitleExportModel`: Tracks individual export operations and status.
- **Redis Caching**: Caches output paths for rapid retrieval by the renderer.

## Usage

### Prerequisites
- **FFmpeg**: Must be installed and available in the system PATH.
- **Dependencies**: `faster-whisper`, `rapidfuzz`.

### Running the Pipeline
To generate raw subtitles for an audio file:
```powershell
python scripts/run_word_timestamp_generation.py --audio <audio_path> --script <script_path>
```

To apply visual styling to existing subtitle JSON:
```powershell
python scripts/run_caption_styling.py --json assets/subtitles/json/sample.json --style tiktok_bold --output assets/subtitles/ass/sample_styled.ass
```

### Testing
- **Pipeline Test**: `python scripts/test_word_timestamps.py`
- **Formatting Test**: `python scripts/test_subtitle_formatter.py`
- **Styling Test**: `python scripts/test_caption_styles.py`

## Style Templates

The system comes with pre-configured templates in `ai/subtitles/styling/style_templates.py`:

- **`tiktok_bold`**: Large font, yellow text, heavy black outline, scaling highlights.
- **`reels_clean`**: Modern font, white text, subtle outlines, active-word color highlighting.
- **`horror_red`**: Courier-style font, red text, shaking animations, dramatic shadows.
- **`motivational_pop`**: Impact font, energetic "pop" transition effects.

## Data Models

### WordTimestamp
- `word`: The text of the word.
- `start_time`: Start in seconds.
- `end_time`: End in seconds.
- `confidence`: Whisper confidence score.
- `position`: Index in the sequence.

### SubtitleSegment
- `text`: Full text of the segment.
- `start_time`: Segment start.
- `end_time`: Segment end.
- `words`: List of word timestamps within this segment.
- `duration`: Total visibility time.
