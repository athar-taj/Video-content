# Zem: AI Media Engine

Zem is a lightweight, Python-first AI orchestration pipeline designed for rapid experimentation with short-form content generation.

## 🚀 Core Features

- **Content Discovery & X/Twitter Trend Engine (Phases 1 & 11)**: Autonomous X/Twitter and Reddit trend ingestion. Leverages official APIs and robust scraping fallbacks with lexical similarity topic clustering and virality velocity tracking.
- **Trend Intelligence**: Intelligent multi-dimensional ranking algorithm using engagement velocity, hashtags, user authority, and emotional triggers.
- **Storytelling & Script Generation (Phase 2)**: Multi-stage AI engine for converting raw topics into conversational, high-retention short-form scripts.
- **Voice Generation & TTS (Phase 3)**: Narration engine supporting local (**Kokoro**) and premium (**Sarvam AI**) providers with automated local-first routing.
- **Dynamic Captions (Phase 4)**: Generates exact word-level timestamps (`faster-whisper`), styles them with ASS animations (karaoke fills, bounce, pop), and matches them to scripts.
- **Background Visuals & Scene Mapping (Phase 5)**: Automatically slices scripts into emotional narrative beats, aligns durations, and splices niche-specific background gameplay/stock video.
- **Final Video Compositor (Phase 6)**: Advanced `FFmpeg` rendering engine that orchestrates background scaling, audio syncing, branding overlays, and hardcodes styled `.ass` subtitles safely within mobile boundaries.
- **Static Orchestration (Phase 7)**: A stateful, retry-safe pipeline engine that automates the end-to-end process with dependency guardrails.
- **Autonomous AI Operating System (Phase 8)**: A true LangGraph-driven decision engine that dynamically evaluates content potential, routing execution through cheap/balanced/premium pipelines, handling conditional retries, and managing parallel sub-tasks.
- **Job Queue & Distributed Execution (Phase 9)**: Scalable asynchronous background execution using Redis Queue (RQ) and staging PostgreSQL tracking tables, providing thread-safe worker execution and rendering workload isolation.
- **Free-First & Local-First self-validating OS (Phase 10)**: Dynamic provider capability detection and fail-fast environment check before pipeline runs. Uses local models by default (Ollama, HuggingFace, Kokoro), only routing to premium APIs optionally when configured and available.

## 📂 Directory Structure

```
zem/
├── ai/
│   ├── discovery/      # Reddit ingestion, trend ranking, storage services
│   ├── generation/     # Script generator, prompt engine, rendering logic
│   ├── voice/          # TTS providers, voice routing, audio generation
│   ├── video_assets/   # Scene mapping, transitions, pacing orchestration
│   ├── rendering/      # Subtitle ASS generation, FFmpeg compositor, overlays
│   └── workflows/      # Stateful pipeline engine, retry management, dependency resolvers
│       ├── queue/      # RQ queue manager, job dispatcher, staging DB validation
│       └── workers/    # General and render worker entry points
├── db/
│   ├── models/         # Modular SQLAlchemy models (Topic, Script, Audio)
│   ├── repositories/   # Async Repository Pattern implementations
├── shared/             # Config, structured logging, utilities
├── assets/             # Generated media assets (audio, temporary files)
└── scripts/            # CLI entry points for pipelines
```

## 🧠 Technical Deep Dive

### 1. Voice Generation & TTS Layer
Our scalable narration system is built for performance and flexibility:
- **Provider Routing**: Automatically selects between high-speed local models and premium studio-quality APIs.
- **Asset Management**: Full lifecycle tracking of generated MP3 narration with duration and file size metadata.
- **Local-First Foundation**: Uses **Kokoro** for high-quality, cost-free local narration, ensuring offline capability.

### 2. Script Quality & Safety Validation
- **Monetization Safety**: Automated detection of profanity and platform-risk topics.
- **Storytelling Standards**: Validates the presence of hooks, narrative arcs, and CTAs.

### 3. Storytelling & Script Generation
- **Hook Optimization**: Dedicated logic for creating suspenseful or shocking opening lines.
- **Duration Control**: Estimates script timing based on word counts to fit 30s/60s/90s constraints.

## 🛠️ Getting Started

> [!NOTE]
> For a detailed step-by-step setup walkthrough, hardware requirements, and background worker orchestration details, see the [Setup & Execution Guide](file:///z:/Zem/docs/setup_and_execution_guide.md).

Zem comes with an automated one-command bootstrapping tool that initializes directories, config files, database schemas, migrations, and checks system dependencies.

1. **Bootstrap Environment**:
   ```bash
   python scripts/bootstrap_environment.py
   ```
   *This copies `.env.example` to `.env` (if not existing), runs database migrations to the latest Alembic head, and verifies FFmpeg/FFprobe availability.*

2. **Configure Credentials**:
   Open `.env` and fill in any optional provider keys (e.g. OpenAI, Twitter, Sarvam) if you plan to use them.

3. **Launch Optional Infrastructure Services**:
   If using Redis for distributed queues or persistent LangGraph checkpointing:
   ```bash
   docker-compose -f infra/docker/docker-compose.yml up -d
   ```

## 🏃 Execution Pipelines

### 1. Real-Time Twitter Discovery
Ingest and cluster real-time viral trends from X/Twitter:
```bash
python scripts/run_twitter_discovery.py
```

### 2. Reddit Ingestion (Fallback/Legacy)
Fetch, filter, and ingest topics from subreddits:
```bash
python scripts/run_content_discovery.py
```

### 3. End-to-End Autonomous Pipeline
Run the fully autonomous pre-validated orchestrator that runs pre-flight diagnostics, evaluates topics, routes, and renders the final video:
```bash
python scripts/run_pipeline.py
```
*This validates dependencies, models, and assets automatically before executing LangGraph orchestration.*

### 4. Integration & Routing Verification Tests
Validate local-first capability routing decisions:
```bash
python scripts/test_local_first_routing.py
```
Validate real-time Twitter ingestion, scoring, clustering, and routing workflows:
```bash
python scripts/test_twitter_pipeline.py
```

### 5. Background Workers & Queue System
Start general workers (listening to script, tts, subtitle, upload, and analytics queues):
```bash
python scripts/run_worker.py
```
Start dedicated render workers (handles CPU-intensive FFmpeg compositions in isolation):
```bash
python scripts/run_render_worker.py
```
Monitor queue depths, active jobs, and worker heartbeats in real-time:
```bash
python scripts/monitor_queues.py --watch
```
Detailed instructions on queue structures, retries, and staging schemas are in [`docs/job_queue.md`](docs/job_queue.md).

## 📐 Architecture Principles
Zem strictly follows a **Cost-Aware Multi-Provider Philosophy**. 
It is a capability-driven engine that enforces:
1. **Local-First Execution** (Ollama, Kokoro, FFmpeg)
2. **Premium-When-Needed** (OpenAI, Sarvam)
3. **Fallback-Always** (Retry managers and stateful dependency guardrails)

Read the full architecture spec in [`docs/architecture_principles.md`](docs/architecture_principles.md), routing system in [`docs/langgraph_decision_engine.md`](docs/langgraph_decision_engine.md), and repository/environment guidelines in [`docs/repository_hygiene.md`](docs/repository_hygiene.md).

## 📊 Observability
Logs are stored in `logs/error.log` and printed to stdout via **Loguru**. Voice assets and generation metrics are tracked in the `generated_audio` table.
