import os
import sys
import time
import uuid
import asyncio
import argparse
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# Ensure project root is in the Python search path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Configure basic logging to avoid duplicates and suppress verbose logs
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("Zem.MainGateway")

# Try importing required packages
try:
    import psutil
except ImportError:
    psutil = None

try:
    import colorama
    from colorama import Fore, Style
    colorama.init(autoreset=True)
except ImportError:
    # Minimal fallback class if colorama is missing
    class Fore:
        GREEN = ""
        RED = ""
        YELLOW = ""
        BLUE = ""
        CYAN = ""
        MAGENTA = ""
        WHITE = ""
    class Style:
        BRIGHT = ""
        RESET = ""

# Import Zem Modules
from shared.config.settings import settings
from shared.validation.environment_validator import EnvironmentValidator
from ai.workflows.pipeline.langgraph_orchestrator import LangGraphOrchestrator
from ai.workflows.pipeline.workflow_registry import WorkflowRegistry
from db.repositories.manager import db_manager
from db.models.database import WorkflowJob
from ai.workflows.queue.worker_manager import worker_manager

# Mapping of LangGraph nodes to console display stages
NODE_TO_STAGE = {
    "fetch_topic": ("Fetching raw trending topic source data...", "Trend Discovery"),
    "evaluate_topic": ("Calculating virality velocity and scoring content...", "Trend Evaluation"),
    "route_workflow": ("Routing script generation to appropriate pipeline...", "Pipeline Routing"),
    "generate_script": ("Authoring engaging short-form script layout...", "Script Generation"),
    "validate_script": ("Running monetization safety and hook validation checks...", "Script Validation"),
    "rewrite_script": ("Script failed validation checks. Triggering rewrite loop...", "Script Rewrite"),
    "generate_voice": ("Synthesizing voice narration track...", "Voice Generation"),
    "generate_subtitles": ("Aligning word-level subtitles using faster-whisper...", "Subtitle Alignment"),
    "generate_scene_mapping": ("Slicing gameplay loops and stock background videos...", "Scene Mapping"),
    "render_video": ("Executing FFmpeg timeline composition and styling...", "Video Rendering"),
    "validate_render": ("Validating final video export bounds and file health...", "Render Validation"),
    "upload_video": ("Staging completed video artifact for export/upload...", "Export Staging"),
    "analytics_feedback": ("Updating local workflow performance metrics...", "Analytics Feed")
}

def print_banner():
    banner = f"""
{Fore.CYAN}{Style.BRIGHT}███████╗███████╗███╗   ███╗
╚══███╔╝██╔════╝████╗ ████║
  ███╔╝ █████╗  ██╔████╔██║
 ███╔╝  ██╔══╝  ██║╚██╔╝██║
███████╗███████╗██║ ╚═╝ ██║
╚══════╝╚══════╝╚═╝     ╚═╝{Fore.BLUE}
==================================================
  AUTONOMOUS AI MEDIA OPERATING SYSTEM GATEWAY
=================================================={Style.RESET_ALL}"""
    print(banner)

async def check_provider_latencies():
    """Test connection latencies of enabled providers and infrastructure services."""
    print(f"\n{Style.BRIGHT}{Fore.WHITE}--- Infrastructure & Provider Latency Checks ---")
    
    # 1. PostgreSQL Check
    start = time.time()
    try:
        async with db_manager.session_factory() as session:
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))
        latency = (time.time() - start) * 1000
        print(f"  {Fore.GREEN}[OK] PostgreSQL: Connected ({latency:.1f}ms){Style.RESET_ALL}")
    except Exception as e:
        print(f"  {Fore.RED}[ERR] PostgreSQL: Connection failed - {e}{Style.RESET_ALL}")

    # 2. Redis Check
    start = time.time()
    try:
        import redis
        r = redis.Redis.from_url(settings.REDIS_URL, socket_connect_timeout=1.0)
        r.ping()
        r.close()
        latency = (time.time() - start) * 1000
        print(f"  {Fore.GREEN}[OK] Redis: Connected ({latency:.1f}ms){Style.RESET_ALL}")
    except Exception as e:
        print(f"  {Fore.YELLOW}[WARN] Redis: Offline - Using memory checkpointing ({e}){Style.RESET_ALL}")

    # 3. Ollama Check
    if settings.ENABLE_OLLAMA:
        start = time.time()
        try:
            import httpx
            async with httpx.AsyncClient(timeout=1.5) as client:
                resp = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
                latency = (time.time() - start) * 1000
                if resp.status_code == 200:
                    print(f"  {Fore.GREEN}[OK] Ollama Local LLM: Available ({latency:.1f}ms){Style.RESET_ALL}")
                else:
                    print(f"  {Fore.RED}[ERR] Ollama Local LLM: Status {resp.status_code}{Style.RESET_ALL}")
        except Exception as e:
            print(f"  {Fore.RED}[ERR] Ollama Local LLM: Offline - {e}{Style.RESET_ALL}")
    else:
        print(f"  {Fore.YELLOW}[-] Ollama Local LLM: Disabled by settings{Style.RESET_ALL}")

    # 4. Kokoro Local Check
    if settings.ENABLE_KOKORO:
        model_path = getattr(settings, "KOKORO_MODEL_PATH", None)
        if model_path:
            print(f"  {Fore.GREEN}[OK] Kokoro Local TTS: Model mounted from path ({model_path}){Style.RESET_ALL}")
        else:
            print(f"  {Fore.GREEN}[OK] Kokoro Local TTS: Auto-download cached mode{Style.RESET_ALL}")
    else:
        print(f"  {Fore.YELLOW}[-] Kokoro Local TTS: Disabled by settings{Style.RESET_ALL}")

    # 5. FFmpeg Check
    ffmpeg_path = shutil.which(settings.FFMPEG_BINARY)
    if ffmpeg_path:
        print(f"  {Fore.GREEN}[OK] FFmpeg: Configured ({ffmpeg_path}){Style.RESET_ALL}")
    else:
        print(f"  {Fore.RED}[ERR] FFmpeg: Binary '{settings.FFMPEG_BINARY}' not found in PATH!{Style.RESET_ALL}")

    # 6. Hardware Load Metrics
    if psutil:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        print(f"  {Fore.BLUE}[INFO] System Load: CPU {cpu}% | RAM {ram}%{Style.RESET_ALL}")

async def run_pipeline_orchestration(topic_id: str, force_score: Optional[int] = None):
    """Executes the LangGraph orchestrator, streaming the state machine step by step."""
    job_id = f"job_cli_{uuid.uuid4().hex[:8]}"
    print(f"\n{Style.BRIGHT}{Fore.WHITE}--- Pipeline Execution: {job_id} ---")
    
    registry = WorkflowRegistry()
    orchestrator = LangGraphOrchestrator(registry)
    graph = orchestrator.graph

    # Initialize state snapshot
    initial_state = {
        "job_id": job_id,
        "topic_id": topic_id,
        "workflow_type": "cheap",
        "viral_score": 0,
        "emotional_score": 0,
        "retention_score": 0,
        "selected_llm_provider": None,
        "selected_tts_provider": None,
        "generated_script": None,
        "narration_path": None,
        "subtitle_path": None,
        "scene_timeline_path": None,
        "render_output_path": None,
        "retry_count": 0,
        "workflow_status": "pending",
        "execution_metadata": {"forced_score": force_score} if force_score else {},
        "errors": [],
        "created_at": datetime.utcnow().isoformat(),
        "script_valid": False
    }

    # Record initial job state in PostgreSQL (if connected)
    db_job_id = None
    try:
        async with db_manager.session_factory() as session:
            job_obj = WorkflowJob(
                workflow_type="cheap",
                status="pending",
                state_snapshot=initial_state
            )
            session.add(job_obj)
            await session.commit()
            db_job_id = job_obj.id
            print(f"  {Fore.BLUE}[DB] Initialized database job schema (Job ID: {db_job_id}){Style.RESET_ALL}")
    except Exception as db_err:
        print(f"  {Fore.YELLOW}[WARN] Database staging skipped: {db_err}{Style.RESET_ALL}")

    config = {"configurable": {"thread_id": job_id}}
    completed_stages = []
    failed_stages = []
    output_files = {}
    final_state = initial_state
    start_time = time.time()

    # Update database status to running
    if db_job_id:
        try:
            async with db_manager.session_factory() as session:
                job_obj = await session.get(WorkflowJob, db_job_id)
                if job_obj:
                    job_obj.status = "running"
                    await session.commit()
        except Exception:
            pass

    # Start auto-managed workers dynamically in background processes
    worker_manager.start_workers()

    print(f"\n{Style.BRIGHT}{Fore.CYAN}🚀 Launching state machine orchestration...\n")
    
    # Executing the LangGraph using dynamic stream events
    current_stage_idx = 1
    total_stages = 7
    
    try:
        async for event in graph.astream(initial_state, config=config):
            for node_name, state_update in event.items():
                if state_update:
                    final_state.update(state_update)
                
                # Check if this node maps to a user-facing stage
                if node_name in NODE_TO_STAGE:
                    status_msg, stage_name = NODE_TO_STAGE[node_name]
                    
                    # Estimate progress steps based on stage categories
                    if stage_name not in completed_stages:
                        completed_stages.append(stage_name)
                        progress = f"[{current_stage_idx}/{total_stages}]"
                        current_stage_idx = min(current_stage_idx + 1, total_stages)
                        print(f"{Fore.GREEN}✔ {progress} {stage_name:<20} | {status_msg}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}↺ {stage_name:<20} | {status_msg}{Style.RESET_ALL}")

                # Harvest files as they get generated
                if state_update:
                    if state_update.get("generated_script"):
                        output_files["script"] = "Staged in database/memory"
                    if state_update.get("narration_path"):
                        output_files["audio"] = state_update["narration_path"]
                    if state_update.get("subtitle_path"):
                        output_files["subtitles"] = state_update["subtitle_path"]
                    if state_update.get("render_output_path"):
                        output_files["video"] = state_update["render_output_path"]

        # Finalize success
        status = final_state.get("workflow_status", "completed")
        if status == "rejected":
            print(f"\n{Fore.YELLOW}⚠ Pipeline ended early: Workflow rejected (low virality score).{Style.RESET_ALL}")
        elif final_state.get("render_output_path"):
            print(f"\n{Fore.GREEN}✔ [{total_stages}/{total_stages}] Export Complete | Final composition completed successfully!{Style.RESET_ALL}")
        else:
            status = "failed"
            print(f"\n{Fore.RED}✖ Pipeline failed: Video failed to render.{Style.RESET_ALL}")
            
    except Exception as e:
        status = "failed"
        failed_stages.append("LangGraph Execution")
        final_state["errors"].append(str(e))
        print(f"\n{Fore.RED}✖ Critical state graph crash: {e}{Style.RESET_ALL}")
        print(f"\n{Style.BRIGHT}{Fore.RED}Suggested Fix:")
        print(f"  * Check pipeline worker logs for internal tracebacks.")
        print(f"  * Verify system package compatibility (e.g. ffmpeg ASS subtitle filters).")
        print(f"  * Review environment configuration using 'python main.py --check'.")
    finally:
        worker_manager.terminate_workers()

    execution_duration = time.time() - start_time

    # Record final results to DB
    if db_job_id:
        try:
            async with db_manager.session_factory() as session:
                job_obj = await session.get(WorkflowJob, db_job_id)
                if job_obj:
                    job_obj.workflow_type = final_state.get("workflow_type", "cheap")
                    job_obj.status = status
                    job_obj.errors = "; ".join(final_state.get("errors", [])) if final_state.get("errors") else None
                    job_obj.completed_at = datetime.utcnow()
                    job_obj.state_snapshot = final_state
                    await session.commit()
        except Exception as db_save_err:
            print(f"  {Fore.YELLOW}[WARN] Database status update failed: {db_save_err}{Style.RESET_ALL}")

    # Generate Final Report
    print_execution_summary(status, completed_stages, failed_stages, final_state.get("errors", []), output_files, execution_duration)

def print_execution_summary(status: str, completed: list, failed: list, errors: list, outputs: dict, duration: float):
    print(f"\n{Fore.BLUE}==================================================")
    print(f"{Style.BRIGHT}{Fore.WHITE}                EXECUTION SUMMARY")
    print(f"{Fore.BLUE}==================================================")
    
    if status.lower() in ("completed", "success") or (status.lower() == "running" and outputs.get("video")):
        print(f"Status:          {Fore.GREEN}{Style.BRIGHT}SUCCESS{Style.RESET_ALL}")
    elif status.lower() == "rejected":
        print(f"Status:          {Fore.YELLOW}{Style.BRIGHT}REJECTED (Low Score){Style.RESET_ALL}")
    else:
        print(f"Status:          {Fore.RED}{Style.BRIGHT}FAILED{Style.RESET_ALL}")
        
    print(f"Execution Time:  {duration:.1f} seconds")
    
    print(f"\nCompleted Stages:")
    for stage in completed:
        print(f"  {Fore.GREEN}✔ {stage}{Style.RESET_ALL}")
        
    if failed or errors:
        print(f"\nFailed Stages / Errors:")
        for stage in failed:
            print(f"  {Fore.RED}✖ {stage}{Style.RESET_ALL}")
        for err in errors:
            print(f"  {Fore.RED}  * Error: {err}{Style.RESET_ALL}")
            
    print(f"\nOutput Files:")
    if outputs:
        for name, path in outputs.items():
            print(f"  * {name:<10}: {Fore.CYAN}{path}{Style.RESET_ALL}")
    else:
        print(f"  {Fore.YELLOW}No output files generated.{Style.RESET_ALL}")
        
    print(f"{Fore.BLUE}==================================================\n")

async def main():
    parser = argparse.ArgumentParser(description="Zem Autonomous AI Media Operating System Gateway Command Line Interface.")
    parser.add_argument("--check", action="store_true", help="Run comprehensive pre-flight verification checks and exit.")
    parser.add_argument("--topic", type=str, default="topic_reddit_gaming_001", help="Target topic ID to run the pipeline against.")
    parser.add_argument("--force-score", type=int, help="Force a content virality evaluation score (e.g. 85 for premium routing).")
    
    args = parser.parse_args()
    print_banner()

    if args.check:
        print(f"\n{Style.BRIGHT}{Fore.WHITE}--- Running Pre-Flight Diagnostics Check ---")
        validator = EnvironmentValidator()
        passed = await validator.generate_health_report()
        await check_provider_latencies()
        if not passed:
            sys.exit(1)
        sys.exit(0)

    # Standard run: Execute pre-flight check, verify latencies, and execute the orchestrator
    validator = EnvironmentValidator()
    passed = await validator.generate_health_report()
    await check_provider_latencies()
    
    if not passed:
        print(f"\n{Fore.RED}{Style.BRIGHT}✖ Pre-flight health validation failed. Pipeline blocked.{Style.RESET_ALL}")
        print(f"Please resolve the critical issues listed above and try again.")
        sys.exit(1)
        
    # Run the pipeline
    await run_pipeline_orchestration(args.topic, args.force_score)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}⚠ Operation cancelled by user. Terminating.{Style.RESET_ALL}")
        sys.exit(1)
