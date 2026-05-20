# Zem: LangGraph Decision Engine Architecture

## Core Philosophy
Zem must evolve from **Static Pipeline Automation** to an **Autonomous AI Media Operating System**.

LangGraph acts as the **AI Production Director**, NOT just a task runner. It evaluates, decides, routes, retries, learns, and optimizes workflows dynamically based on content potential and cost-efficiency.

## Target Execution Flow (Dynamic)
The workflow is no longer a linear `Fetch -> Script -> Voice -> Render`. It is a branching decision tree:

1. **Fetch Topic**
2. **Evaluate Topic** (Calculate Viral Score, Emotional Score, Retention Score)
3. **Decision Router (LangGraph)**
   - **Low Potential** -> `Cheap Pipeline`
   - **Medium Potential** -> `Balanced Pipeline`
   - **High Potential** -> `Premium Pipeline`

## Workflow Routing Strategies

### 1. Cheap Pipeline
- **Goal**: Bulk, cheap generation and experimentation.
- **Tools**: Local LLMs (Qwen/Mistral), Kokoro TTS, basic captions, simple gameplay render.

### 2. Balanced Pipeline
- **Goal**: Better retention with controlled costs.
- **Tools**: Mixed Local/Cloud LLMs, Sarvam TTS, animated captions, enhanced rendering.

### 3. Premium Pipeline
- **Goal**: Maximum retention and viral potential.
- **Tools**: Claude/OpenAI, Murf/ElevenLabs, cinematic subtitles, premium rendering.

## Conditional Decision Examples
LangGraph natively manages conditional edges for execution:
- **IF `viral_score < 40`**: Reject content, skip generation.
- **IF `viral_score > 80`**: Activate premium storytelling.
- **IF `script_quality < threshold`**: Trigger script rewrite loop.
- **IF `narration_quality fails`**: Switch TTS provider dynamically.
- **IF `caption sync fails`**: Retry subtitle engine.
- **IF `render fails`**: Fallback to safe render pipeline.

## Self-Improving Learning Layer
Over time, the LangGraph memory state should track and learn from analytics:
- Watch time, retention, CTR, hook success rates.
- Successful narration styles and visual pacing.
- The workflow should route future generations based on past successful patterns and failed pipelines.

## Mandatory Engineering Requirements
The orchestration brain must implement:
- Conditional edges and dynamic routing.
- Quality-aware and cost-aware scoring systems.
- Fallback and retry branches.
- Workflow memory and state transitions.

*Zem workflows do not just execute. They evaluate, decide, route, and optimize.*
