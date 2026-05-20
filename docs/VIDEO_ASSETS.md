# Background Video Asset System

The Background Video Asset System is responsible for managing, selecting, and processing background footage for the Zem AI Media Engine. It ensures that every video has a relevant, high-quality visual backdrop that matches the narration length and content niche.

## Architecture

The system is located in `ai/video_assets/backgrounds/` and consists of the following components:

### 1. Asset Management & Indexing (`ai/video_assets/management/`)
- **`AssetIndexer`**: Recursively scans configured directories, extracts metadata, and registers assets in the database.
- **`AssetSearchEngine`**: A database-backed retrieval engine that supports complex filters (tags, category, niche, duration, orientation).
- **`MetadataExtractor`**: Uses FFmpeg (`ffprobe`) to extract technical details: resolution, FPS, bitrate, duration, codec, and orientation.
- **`DuplicateDetector`**: Ensures media library integrity using SHA256 checksums to detect identical files.
- **`TagManager` & `CategoryManager`**: Manages the media taxonomy, suggesting niche-relevant tags and organizing files into logical buckets.

### 2. Selection & Routing (`ai/video_assets/backgrounds/`)
- **`GameplayRouter`**: Maps content niches to video categories. 
    - *Example*: `horror` -> `gameplay` with `dark` tags.
    - *Example*: `relationship` -> `cinematic` loops.
- **`VideoSelector`**: Selects the best candidate based on category, duration, and tags.
- **Repetition Avoidance**: Integrated with Redis to track asset usage.

### 3. Scene Mapping & Synchronization (`ai/video_assets/scene_mapping/`)
- **`SceneMapper`**: Splits scripts into narrative sections (Hook, Story, CTA) based on markers.
- **`NarrationAligner`**: Synchronizes visual scene changes with narration audio timings.
- **`PacingEngine`**: Determines the visual rhythm (Fast-paced, Suspense, Dramatic) based on content niche and section type.
- **`TransitionManager`**: Manages visual transitions (Fade, Zoom, Flash, Hard-cut) between scenes.
- **`SceneTimelineBuilder`**: The final orchestrator that produces a render-ready JSON timeline.

### 4. Processing Engine (`ai/video_assets/backgrounds/`)
- **`DurationTrimmer`**: A wrapper around FFmpeg for:
    - **Random Trimming**: Cutting a segment of specific duration from a longer video at a random start point.
    - **Seamless Looping**: Looping short assets (like cinematic loops) to reach the required narration duration.
    - **Clip Generation**: Creating specific sub-clips for complex compositions.

### 4. Storage & Persistence
- Subtitle data is stored in PostgreSQL via SQLAlchemy:
    - `VideoAssetModel`: Technical metadata and local path.
    - `VideoClipModel`: Metadata for processed/trimmed clips.
    - `AssetUsageLog`: Tracking history of which assets were used for which scripts.

## Directory Structure

Assets are organized in `assets/videos/`:
- `gameplay/`: General gaming footage (Minecraft, Subway Surfers, etc.).
- `cinematic/`: Atmospheric loops and scenic shots.
- `stock/`: Standard stock footage.
- `memes/`: Short reaction or viral clips.
- `loops/`: Specifically designed seamless loops.
- `processed/`: Final trimmed/looped outputs ready for rendering.
- `temp/`: Intermediate processing files.

## Usage

### Prerequisites
- **FFmpeg**: Required for metadata extraction and video processing.
- **Redis**: Required for usage tracking and repetition avoidance.

### Running the System
To index your local media library:
```powershell
python scripts/run_asset_indexing.py
```

To select and process a background video for a script:
```powershell
python scripts/run_background_video_selection.py --script_id <ID> --niche <NICHE> --duration <SECONDS>
```

To generate a full visual timeline for a script:
```powershell
python scripts/run_scene_mapping.py --script_id <ID> --script_text "<TEXT>" --segments <PATH_TO_JSON> --niche <NICHE>
```

### Testing
- **Indexing & Search**: `python scripts/test_asset_management.py`
- **Selection & Processing**: `python scripts/test_background_video_system.py`
- **Scene Mapping**: `python scripts/test_scene_mapping.py`

## Data Models

### VideoAsset
- `asset_name`: Original filename.
- `category`: gameplay, cinematic, etc.
- `resolution`: e.g., "1080x1920".
- `fps`: Frames per second.
- `duration_seconds`: Total length.
- `local_path`: Absolute path to source file.

### VideoClip
- `asset_id`: ID of the source asset.
- `clip_start`: Start timestamp in source.
- `clip_end`: End timestamp in source.
- `output_path`: Path to the processed .mp4 file.
