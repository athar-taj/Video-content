# Zem: Cost-Aware Multi-Provider AI Architecture

## Core Philosophy
Zem is a capability-driven autonomous AI media infrastructure platform.
The architecture thinks in terms of **CAPABILITIES** (`generate_script`, `generate_voice`, `render_video`), NOT specific tools (`use_openai`, `use_kokoro`).

**Providers are implementation details.**

## Primary System Philosophy
ALWAYS FOLLOW:
1. LOCAL-FIRST
2. PREMIUM-WHEN-NEEDED
3. FALLBACK-ALWAYS

The engine intelligently decides when to use local models, premium APIs, downgrade costs, fallback, cache, or retry.

## Multi-Provider Requirement
Every subsystem must support:
1. Primary Provider
2. Secondary Provider
3. Fallback Provider
4. Offline/Local Provider
5. Future Provider Expansion

### LLM Architecture
- **Local/Free Providers**: Ollama, HuggingFace, Qwen, Mistral, Gemma, GGUF models.
- **Premium Providers**: OpenAI, Claude, Gemini, Mistral API.
- **Local Usage**: Metadata generation, cleaning, validation, experimentation, batch generation.
- **Premium Usage**: Viral hook generation, emotional storytelling, high-retention scripts, premium final outputs.
- **Requirements**: BaseLLMProvider abstraction, dynamic routing, fallback, cost-aware routing.

### TTS Architecture
- **Local/Free**: Kokoro, Piper TTS (future), Coqui TTS (future).
  - *Offline Execution*: Fully supports air-gapped environments by configuring `KOKORO_MODEL_PATH` to point to a directory containing the `.pth` model weights and its matching `config.json`.
- **Premium**: Murf AI, Sarvam AI, ElevenLabs, OpenAI TTS, Azure TTS.
- **Local Usage**: Testing, drafts, experimentation, bulk generation.
- **Premium Usage**: High-performing content, final premium exports, emotionally optimized narration.
- **Requirements**: BaseTTSProvider abstraction, runtime switching, emotional routing, fallback.

### Subtitle Architecture
- **Local/Free**: faster-whisper, Whisper.cpp, Vosk.
- **Premium/Advanced**: WhisperX, Deepgram (future).
- **Requirements**: Interchangeable engines, offline generation, fallback systems.

### Video Rendering Architecture
- **Primary**: FFmpeg (free, scalable, production-proven).
- **Future**: GPU rendering, OpenCV, Blender automation, distributed rendering.
- **Requirements**: Renderer abstraction, fallback pipeline, GPU-ready architecture.

### Asset System Architecture
- **Free/Local**: Local gameplay libraries, reusable loops, stock footage.
- **Future**: Stock APIs, AI-generated visuals, cloud systems.
- **Requirements**: Asset abstraction, source-independent retrieval.

## Pipeline Orchestration & Failure Tolerance
- Support provider switching, fallback chains, retries, health tracking, and quality/cost-aware routing.
- Survive API outages, rate limits, network failures via graceful degradation and automatic rerouting.

## Cost-Aware & Quality Gating
- Intelligently choose providers based on quality, speed, cost, and importance.
- NEVER waste premium resources unnecessarily.
- **Quality Gating**: Premium providers activate ONLY if hook quality, retention prediction, and emotional scores pass thresholds.
- **Cost Optimization**: Track token usage, API costs, cost per video, and optimize for profitability.

## Mandatory Engineering Rules
- ALWAYS use abstractions and support multiple providers.
- ALWAYS support local/offline workflows.
- ALWAYS cache aggressively.
- NEVER hardcode providers or assume cloud availability.
- NEVER build single-provider workflows.

## MVP Execution Strategy
The FIRST working MVP uses minimal cost:
- Ollama / Qwen / Mistral local
- Kokoro
- faster-whisper
- FFmpeg
- PostgreSQL
- Redis

ONLY AFTER THE MVP WORKS do we add premium providers and expensive generation.
