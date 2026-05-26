# Zem AI Media Engine - Documentation

## Project Progress Overview

This document tracks the implemented features of the Zem AI Media Engine, structured by phases.

### Phase 1 — Content Discovery (Completed)
- **Reddit API/Scraper Integration**: Scrapes posts from `AskReddit`, `confessions`, `relationship_advice`, and `talesfromtechsupport`. Extracts title, body, and comments while filtering NSFW content.
- **Trend Ranking Logic**: Computes a viral score based on upvotes, comments, and recency, applying quality filters and detecting duplicates.
- **Topic Storage System**: Persists fetched Reddit posts to a PostgreSQL database with a normalized schema, ensuring duplicate prevention and processing status tracking.

### Phase 2 — Script Engine (Completed)
- **OpenAI Integration**: Implements LLM-based content generation with configurable prompts and token logging.
- **Prompt Template Engine**: Uses dynamic placeholders for structured generation (e.g., HOOK, STORY, CLIFFHANGER, CTA).
- **Script Generator**: Converts raw Reddit content into viral short scripts with configurable target durations.
- **Script Quality Validation**: Validates script length, ensures uniqueness, and filters profanity.

### Phase 3 — Voice Generation
- **TTS Provider Integration**: Base structures integrated for Sarvam AI, Murf AI, and Kokoro.
- **Voice Preset System**: A comprehensive preset system managing multiple voice personalities, emotional tone mapping, narration pacing, and context-driven routing. Stores configurations in YAML and PostgreSQL, with Redis caching.

#### Task 3.3 — Audio Storage System (Completed)
Builds a scalable Audio Storage & Lifecycle Management System serving as the central audio asset layer.

**Key Features:**
- **Storage Strategy**: Separates files into `raw`, `processed`, `temp`, and `archived` states under `assets/audio/`. Uses deterministic file naming (`{script_id}_{provider}_{voice}_{version}.mp3`).
- **Database Tracking**: Uses PostgreSQL to track metadata via `AudioGenerationModel`, managing data like duration, sample rate, checksum, size, and current status (`pending`, `completed`, `failed`, `archived`).
- **Data Integrity**: Implements SHA256 checksums to detect corruption and verify processing pipelines. Validates empty files, durations, and missing assets.
- **Automated Cleanup**: A robust `CleanupService` automating deletion of expired temp files, old failed attempts, and the archival of successfully processed audio.
- **Archival Flow**: Migrates old generated audio to long-term storage, keeping active directories clean and performant while preparing for future cloud (AWS S3, R2) transitions.
- **Scripts Available**:
  - `python scripts/test_audio_storage.py` - Runs the end-to-end storage, metadata, and validation flow.
  - `python scripts/run_audio_cleanup.py` - Cleans old temp files and archives stale data.

### Phase 4 — Subtitles & Word Timestamps (Completed)
Builds a scalable Word-Level Timestamp Generation and Formatting System for the AI media engine.

**Key Features:**
- **Word-Level Generation**: Uses `faster-whisper` for accurate transcription and word-level timing data.
- **Transcript Alignment**: Implements a `TranscriptMatcher` using fuzzy matching (`rapidfuzz`) to align transcribed words with original scripts.
- **Modular Formatting Engine**:
  - `SRTFormatter`: Standard-compliant SRT generation.
  - `JSONFormatter`: Structured data for frontend/rendering.
  - `ASS/KaraokeFormatter`: Advanced styling and animated highlighting support.
- **Visual Caption Styling System**:
  - `CaptionStyleManager`: Orchestrates fonts, styles, and animations.
  - `AnimationEngine`: Supports fade, pop, bounce, and shake effects via ASS tags.
  - `HighlightEngine`: Word-level emphasis and karaoke highlighting.
  - `StyleTemplates`: Reusable presets like `tiktok_bold`, `reels_clean`, and `horror_red`.
  - `FontManager`: Manages custom and system font registration.
- **Deterministic Exporting**: `SubtitleExporter` manages directory structures and consistent naming conventions.
- **Storage & Metadata**: Detailed tracking of formatted outputs and styling profiles via `CaptionStyleModel`.
- **Scripts Available**:
  - `python scripts/run_word_timestamp_generation.py` - Main CLI for subtitle generation.
  - `python scripts/run_subtitle_formatter.py` - Formats existing subtitle data.
  - `python scripts/run_caption_styling.py` - Applies visual styles to subtitle JSON.
  - `python scripts/test_caption_styles.py` - Validates the styling and animation pipeline.

### Phase 5 — Background Video System (Completed)
Builds a scalable Background Video Asset System for automated visual selection and processing.

**Key Features:**
- **Asset Lifecycle Management**: Centralized `AssetManager` and `AssetIndexer` for recursive indexing, registration, and validation.
- **Technical Metadata Extraction**: Automated extraction of resolution, FPS, bitrate, codecs, orientation, and durations using FFmpeg.
- **Searchable Media Library**: `AssetSearchEngine` enables fast retrieval via tags, niche, category, duration, and orientation.
- **Niche-Aware Routing & Tagging**: `GameplayRouter` and `TagManager` map content themes to relevant visual assets and metadata.
- **Scene Mapping & Visual Sync**: `SceneMapper` and `NarrationAligner` split scripts into narrative segments and synchronize them with audio timings.
- **Timeline Orchestration**: `SceneTimelineBuilder` creates render-ready visual timelines with dynamic transitions (fade, zoom, flash) and pacing styles.
- **Automated Processing**: `DurationTrimmer` handles frame-accurate cutting and seamless looping.
- **Storage & Metadata**: Comprehensive database tracking via `VideoAssetModel` and `SceneTimelineModel` in PostgreSQL.
- **Scripts Available**:
  - `python scripts/run_asset_indexing.py` - Scans and indexes local media assets.
  - `python scripts/run_scene_mapping.py` - Generates a visual timeline from script and narration.
  - `python scripts/run_background_video_selection.py` - Automates video selection for production.
  - `python scripts/test_scene_mapping.py` - Validates the narrative-to-scene alignment pipeline.

### Phase 6 — Video Rendering Engine (Completed)
Builds the final orchestration layers to combine audio, video, overlays, and stylized captions via FFmpeg.

**Key Features:**
- **Caption Burner**: Uses `ffmpeg-python` to inject hardcoded `.ass` subtitle files dynamically into vertical videos while enforcing mobile safe zones.
- **Dynamic Render Pipeline**: `FinalVideoComposer` synchronizes the background scenes, narration audio, branding overlays, and karaoke subtitles using complex FFmpeg filter graphs (`-filter_complex`).
- **Validation**: Strict pre-render (missing assets) and post-render (zero-byte checking) guards.
- **Exporting**: Auto-archives final renders out of temp directories safely.
- **Scripts Available**:
  - `python scripts/run_caption_burn.py` - standalone ASS burning test.
  - `python scripts/run_final_video_composer.py` - full composition of all assets.

### Phase 7 — Pipeline Orchestration (Completed)
Builds a robust, multi-stage, stateful pipeline engine to drive the AI automation from script generation to final render.

**Key Features:**
- **Stateful Execution Context**: Passes data between disjointed workflows efficiently.
- **Resiliency & Retries**: `RetryManager` handles exponential backoffs for failing external APIs.
- **Dependency Guardrails**: Prevents execution if prerequisite assets (e.g., narration missing before rendering) are not met.
- **Cost-Aware Multi-Provider Architecture**: Implemented foundational support allowing runtime swapping between Local (Ollama, Kokoro) and Premium (OpenAI, Sarvam) providers based on content quality and cost efficiency, documented in `docs/architecture_principles.md`.
- **Scripts Available**:
  - `python scripts/run_pipeline.py` - Orchestrates the full pipeline workflow.
  - `python scripts/test_pipeline.py` - Verifies state updates across all stages.

### Phase 8 — Autonomous AI Operating System (LangGraph) (Completed)
Transitions the orchestration layer from a static linear pipeline to a dynamic, decision-driven autonomous engine using **LangGraph**.

**Key Features:**
- **Dynamic Decision Routing**: Evaluates topic viral potential (e.g., via `viral_score`) to route execution through `cheap`, `balanced`, or `premium` pipelines.
- **Self-Healing Workflows**: Natively supports conditional edges for retry loops, such as automatically rewriting scripts if quality validation fails.
- **Parallel Processing**: Executes independent stages like `generate_subtitles` and `map_scenes` concurrently, syncing their outputs before final rendering.
- **Provider Switching**: Automatically adjusts LLM and TTS providers based on the selected pipeline route (e.g., Local Ollama/Kokoro for cheap, Claude/Sarvam for premium).
- **Stateful Memory Graph**: Graph state tracking ensures complete observability of the pipeline across disjointed nodes, preparing for future analytical feedback loops.
- **Scripts Available**:
  - `python scripts/test_langgraph_pipeline.py` - Verifies the dynamic graph routing and execution.

### Phase 9 — Job Queue & Distributed Execution System (Completed)
Builds a scalable asynchronous Job Queue & Distributed Execution System (RQ) to run background task workflows, separate rendering computations, stage/track executions inside PostgreSQL, and enable recovery/retries.

**Key Features:**
- **Asynchronous Execution**: Decouples LangGraph node transitions from direct execution via `JobDispatcher` and Redis Queue (RQ).
- **PostgreSQL Job Staging**: Persists all job statuses, parameters, and results in `pipeline_jobs` and `job_failures` tables before enqueuing.
- **Worker Isolation**: General worker handles light tasks (scripts, TTS, subtitles, uploads, analytics), while a dedicated render worker executes resource-heavy FFmpeg video comps on the `render_queue`.
- **Worker Registry & Heartbeats**: Background thread logs active worker health metrics, states, and heartbeats to `worker_states` database table.
- **Thread-Safe DB Pool Access**: Isolated thread-local engines and session factories prevent connection pool conflicts between heartbeat loops and active workers.
- **Scripts Available**:
  - `python scripts/run_worker.py` - Launches standard queues worker.
  - `python scripts/run_render_worker.py` - Launches dedicated rendering worker.
  - `python scripts/monitor_queues.py` - Visualizes queue/worker status on console dashboard in real-time.
  - `python scripts/retry_failed_jobs.py` - Inspects failed jobs and replays dead letter records.
  - `python scripts/purge_dead_jobs.py` - Cleans up failure histories and dead logs.

### Phase 10 — Local-First AI Migration & Master Environment Validation (Completed)
Builds a cost-efficient, offline-first operating system that validates the environment and fallback routes prior to running the pipelines.

**Key Features:**
- **Local-First & Free-First Routing**: Configured provider router prioritizing Ollama and HuggingFace for LLMs, and Kokoro and Sarvam for TTS to avoid premium API key billing blocks.
- **Master Environment Validator**: Implemented `EnvironmentValidator` that validates imports, config files, required Ollama models, external binaries (FFmpeg/FFprobe), custom fonts, ASS subtitles templates, visual overlays, gameplay videos, and database/Redis/Twitter/Sarvam connectivity checks with warning status downgrades for optional keys.
- **Dynamic Connection & URL Assembly**: Enabled Pydantic `model_validator` in `settings.py` to automatically assemble `DATABASE_URL` and `REDIS_URL` from individual postgres and redis host/port/db parameters.
- **One-Command Bootstrap script**: Created `scripts/bootstrap_environment.py` to build the required directory tree, deploy configurations, run DB migrations, and verify system dependencies.
- **Scripts Available**:
  - `python scripts/bootstrap_environment.py` - Bootstraps the local project environment, directories, configuration, and migrations.
  - `python scripts/test_local_first_routing.py` - Runs the unit test suite for local routing and model capability validation.

### Phase 11 — Real-Time X/Twitter Discovery Engine (Completed)
Migrates the media engine trend discovery from Reddit-first to Twitter/X-first real-time trend discovery, enabling velocity tracking and lexical deduplication.

**Key Features:**
- **Twitter-First Discovery Ingestion**: Created PostgreSQL database schemas for `TwitterTrend`, `TrendCluster`, and `InfluencerMetrics`.
- **Robust Multi-Provider Twitter Ingestor**: Created Tweepy API client with automatic web-scraping fallbacks (Twikit, snscrape, Playwright) and Mock simulations for full offline and sandbox execution.
- **Lexical Topic Clustering & Virality Analysis**: Groups trending topics dynamically using RapidFuzz string similarity, scoring virality based on retweet velocity, engagement ratios, and creator authority metrics.
- **Dynamic Decision Edge Integration**: Refactored the LangGraph `topic_fetch_node` and router to ingest Twitter trends and choose workflows dynamically matching the trend's virality.
- **Scripts Available**:
  - `python scripts/run_twitter_discovery.py` - CLI to ingest and cluster real-time Twitter/X trends.
  - `python scripts/test_twitter_pipeline.py` - Integration test for Twitter trend fetching and state routing.

---

*This document is actively maintained as new features are integrated into the architecture.*

