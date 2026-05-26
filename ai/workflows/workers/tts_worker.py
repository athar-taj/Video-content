import logging
import os
from typing import Dict, Any

from ai.workflows.workers.base_worker import run_async, execute_job_wrapper
from ai.workflows.queue.models import JobType

logger = logging.getLogger(__name__)

async def _process_tts_async(job_id: str, workflow_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Asynchronous business logic for generating TTS audio."""
    from ai.voice.generation.tts_service import TTSService
    from ai.workflows.pipeline.provider_router import ProviderRouter
    from db.repositories.manager import db_manager
    from db.models import GeneratedAudio

    script_data = payload.get("generated_script")
    script_text = ""
    if script_data:
        script_text = script_data.get("full_script", "")
    else:
        script_text = payload.get("script_text", "")
        
    if not script_text:
        raise ValueError("Missing script text for TTS generation.")
        
    workflow_type = payload.get("workflow_type", "cheap")
    script_id = payload.get("script_id") or payload.get("execution_metadata", {}).get("script_id", 1)
    
    router = ProviderRouter()
    tts_service = TTSService(output_dir="assets/audio/generated")
    
    providers_to_try = await router.get_tts_chain(workflow_type)
    
    selected_provider = None
    audio_path = None
    duration = 0.0
    
    for provider_name in providers_to_try:
        logger.info(f"Attempting TTS generation with provider: {provider_name}")
        try:
            voice_id = "af_bella" if provider_name.lower() == "kokoro" else "default"
            res = await tts_service.generate_narration(
                script_text=script_text,
                provider=provider_name,
                voice_id=voice_id
            )
            logger.info(f"Successfully generated narration with {provider_name}")
            router.report_success(provider_name)
            
            selected_provider = provider_name
            audio_path = res.audio_path
            duration = res.duration_sec
            break
        except Exception as e:
            logger.error(f"Provider '{provider_name}' failed TTS generation: {e}")
            router.report_failure(provider_name)
            
    if not selected_provider:
        logger.critical("All TTS providers failed voice generation! Trying Kokoro as ultimate fallback.")
        try:
            res = await tts_service.generate_narration(
                script_text=script_text,
                provider="Kokoro",
                voice_id="af_bella"
            )
            selected_provider = "Kokoro"
            audio_path = res.audio_path
            duration = res.duration_sec
        except Exception as e:
            logger.exception("Ultimate fallback TTS Kokoro failed as well!")
            raise RuntimeError(f"All TTS providers failed: {e}")
            
    # Persist in DB
    audio_db_id = None
    try:
        async with db_manager.get_session() as session:
            s_id = int(script_id) if str(script_id).isdigit() else 1
            audio_obj = GeneratedAudio(
                script_id=s_id,
                provider=selected_provider,
                voice_name="af_bella",
                audio_path=audio_path,
                duration_seconds=duration,
                file_size_bytes=os.path.getsize(audio_path) if os.path.exists(audio_path) else 0
            )
            session.add(audio_obj)
            await session.commit()
            audio_db_id = audio_obj.id
            logger.info(f"Saved generated audio metadata to DB with ID: {audio_db_id}")
    except Exception as e:
        logger.error(f"Failed to persist audio metadata to DB: {e}")
        # Not a fatal execution failure, we can continue as long as audio file exists

    metadata = payload.get("execution_metadata", {})
    metadata["audio_id"] = audio_db_id
    metadata["audio_duration"] = duration

    return {
        "narration_path": audio_path,
        "selected_tts_provider": selected_provider,
        "execution_metadata": metadata
    }

def process_job(job_id: str, workflow_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """RQ target function for TTS Worker."""
    return run_async(
        execute_job_wrapper(
            job_id=job_id,
            workflow_id=workflow_id,
            payload=payload,
            job_type=JobType.TTS,
            processor_func=_process_tts_async
        )
    )
