import logging
import os
from typing import Dict, Any
from ai.voice.generation.tts_service import TTSService
from ai.workflows.pipeline.provider_router import ProviderRouter
from db.repositories.manager import db_manager
from db.models import GeneratedAudio

logger = logging.getLogger(__name__)

async def tts_generation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Executing TTS Generation Node...")
    
    script_data = state.get("generated_script")
    if not script_data:
        logger.error("No generated script in state for TTS.")
        return {
            "errors": state.get("errors", []) + ["No script found for TTS generation"],
            "workflow_status": "failed"
        }
        
    script_text = script_data.get("full_script", "")
    workflow_type = state.get("workflow_type", "cheap")
    script_id = state.get("execution_metadata", {}).get("script_id", 1)
    
    router = ProviderRouter()
    tts_service = TTSService(output_dir="assets/audio/generated")
    
    # Get preference list
    providers_to_try = list(router.tts_chains.get(workflow_type, ["Kokoro"]))
    
    selected_provider = None
    audio_path = None
    duration = 0.0
    
    for provider_name in providers_to_try:
        logger.info(f"Attempting TTS generation with provider: {provider_name}")
        try:
            # Map standard voice ids
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
            return {
                "errors": state.get("errors", []) + [f"TTS Generation failed: {str(e)}"],
                "workflow_status": "failed"
            }
            
    # Persist in DB
    try:
        async for session in db_manager.get_session():
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
            logger.info(f"Saved generated audio metadata to DB with ID: {audio_obj.id}")
            
            state_metadata = state.get("execution_metadata", {})
            state_metadata["audio_id"] = audio_obj.id
            state_metadata["audio_duration"] = duration
    except Exception as e:
        logger.error(f"Failed to persist audio metadata to DB: {e}")
        
    return {
        "narration_path": audio_path,
        "selected_tts_provider": selected_provider,
        "execution_metadata": state.get("execution_metadata", {})
    }
