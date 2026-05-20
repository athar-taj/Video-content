# Zem: AI Media Engine

Zem is a lightweight, Python-first AI orchestration pipeline designed for rapid experimentation with short-form content generation.

## 🚀 Core Features

- **Content Discovery (Phase 1)**: Autonomous Reddit ingestion with viral scoring, quality filtering, and duplicate detection.
- **Trend Intelligence**: Intelligent multi-dimensional ranking algorithm using engagement velocity, time decay, and emotional triggers.
- **Storytelling & Script Generation (Phase 2)**: Multi-stage AI engine for converting raw topics into conversational, high-retention short-form scripts.
- **Voice Generation & TTS (Phase 3)**: Scalable narration engine supporting local (**Kokoro**) and premium (**Sarvam AI**) providers with automated routing.
- **Dynamic Captions (Phase 4)**: Generates exact word-level timestamps (`faster-whisper`), styles them with ASS animations (karaoke fills, bounce, pop), and matches them to scripts.
- **Background Visuals & Scene Mapping (Phase 5)**: Automatically slices scripts into emotional narrative beats, aligns durations, and splices niche-specific background gameplay/stock video.
- **Final Video Compositor (Phase 6)**: Advanced `FFmpeg` rendering engine that orchestrates background scaling, audio syncing, branding overlays, and hardcodes styled `.ass` subtitles safely within mobile boundaries.
- **Static Orchestration (Phase 7)**: A stateful, retry-safe pipeline engine that automates the end-to-end process with dependency guardrails.
- **Autonomous AI Operating System (Phase 8)**: A true LangGraph-driven decision engine that dynamically evaluates content potential, routing execution through cheap/balanced/premium pipelines, handling conditional retries, and managing parallel sub-tasks.
- **Cost-Aware Multi-Provider Foundation**: Unified abstraction for LLMs (**OpenAI**, **Mistral**, **Ollama**), TTS, and logic ensuring Zem falls back dynamically and operates safely offline.

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

1. **Setup Environment**:
   ```bash
   cp .env.example .env
   # Add your OpenAI, Mistral, and Reddit API keys
   ```

2. **Launch Infrastructure**:
   ```bash
   docker-compose -f infra/docker/docker-compose.yml up -d
   ```

3. **Run Migrations**:
   ```bash
   py -m alembic upgrade head
   ```

## 🏃 Execution Pipelines

### 1. Content Discovery
Fetch, filter, and ingest topics from Reddit:
```bash
python scripts/run_content_discovery.py
```

### 2. Script Generation
Generate viral scripts for ranked topics:
```bash
python scripts/run_script_generation.py --limit 5
```

### 3. Voice Generation (TTS)
Convert validated scripts into professional narration:
```bash
python scripts/run_tts_generation.py
```

### 4. End-to-End Autonomous Pipeline
Run the fully autonomous orchestrator that evaluates, routes, and executes the complete flow:
```bash
python scripts/run_pipeline.py
```
To test the LangGraph conditional routing and parallel state graph directly:
```bash
python scripts/test_langgraph_pipeline.py
```

### 5. Final Rendering Pipeline (Standalone)
To test only the FFmpeg subtitle burning and scene composition:
```bash
python scripts/test_final_video_composer.py
```

## 📐 Architecture Principles
Zem strictly follows a **Cost-Aware Multi-Provider Philosophy**. 
It is a capability-driven engine that enforces:
1. **Local-First Execution** (Ollama, Kokoro, FFmpeg)
2. **Premium-When-Needed** (OpenAI, Sarvam)
3. **Fallback-Always** (Retry managers and stateful dependency guardrails)

Read the full architecture spec in [`docs/architecture_principles.md`](docs/architecture_principles.md) and learn about the routing system in [`docs/langgraph_decision_engine.md`](docs/langgraph_decision_engine.md).

## 📊 Observability
Logs are stored in `logs/error.log` and printed to stdout via **Loguru**. Voice assets and generation metrics are tracked in the `generated_audio` table.
