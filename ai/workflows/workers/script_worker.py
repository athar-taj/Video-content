import logging
from typing import Dict, Any

from ai.workflows.workers.base_worker import run_async, execute_job_wrapper
from ai.workflows.queue.models import JobType

logger = logging.getLogger(__name__)

async def _process_script_async(job_id: str, workflow_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Asynchronous business logic for generating a script."""
    from ai.generation.script_generator.generator import ScriptGenerator
    from ai.workflows.pipeline.provider_router import ProviderRouter
    from db.repositories.manager import db_manager
    from db.models.script import GeneratedScript

    # Extract parameters from payload
    topic_id = payload.get("topic_id", "1")
    title = payload.get("title", "")
    body = payload.get("body", "")
    subreddit = payload.get("subreddit", "gaming")
    workflow_type = payload.get("workflow_type", "cheap")
    
    router = ProviderRouter()
    generator = ScriptGenerator()
    
    providers_to_try = await router.get_llm_chain(workflow_type)
    last_error = None
    selected_provider = None
    script_data = None
    
    for provider_name in providers_to_try:
        logger.info(f"Attempting script generation with provider: {provider_name}")
        try:
            t_id = int(topic_id) if str(topic_id).isdigit() else 1
            result = await generator.generate_full_script(
                topic_id=t_id,
                title=title,
                raw_body=body,
                subreddit=subreddit,
                target_duration=60,
                provider=provider_name
            )
            logger.info(f"Successfully generated script with {provider_name}")
            router.report_success(provider_name)
            
            selected_provider = provider_name
            script_data = {
                "hook": result.hook,
                "story": result.full_script,
                "full_script": result.full_script,
                "duration": result.metadata.get("estimated_duration", 60)
            }
            break
        except Exception as e:
            logger.error(f"Provider '{provider_name}' failed script generation: {e}")
            router.report_failure(provider_name)
            last_error = e
            
    if not selected_provider:
        fallback_provider = "Ollama"
        from shared.config.settings import settings
        if settings.ENV == "development":
            from ai.workflows.pipeline.provider_capability_registry import provider_capability_registry
            if not await provider_capability_registry.is_provider_available("ollama"):
                fallback_provider = "Mock"
                
        logger.critical(f"All LLM providers failed script generation! Trying {fallback_provider} fallback.")
        try:
            t_id = int(topic_id) if str(topic_id).isdigit() else 1
            result = await generator.generate_full_script(
                topic_id=t_id,
                title=title,
                raw_body=body,
                subreddit=subreddit,
                target_duration=60,
                provider=fallback_provider
            )
            selected_provider = fallback_provider
            script_data = {
                "hook": result.hook,
                "story": result.full_script,
                "full_script": result.full_script,
                "duration": result.metadata.get("estimated_duration", 60)
            }
        except Exception as e:
            logger.exception(f"Ultimate fallback LLM {fallback_provider} failed as well!")
            raise RuntimeError(f"All script generation providers failed: {last_error or e}")

    # Persist in Database
    script_db_id = None
    try:
        async for session in db_manager.get_session():
            t_id = int(topic_id) if str(topic_id).isdigit() else 1
            script_obj = GeneratedScript(
                topic_id=t_id,
                hook=script_data["hook"],
                full_script=script_data["full_script"],
                duration_target=60.0,
                estimated_duration=float(script_data["duration"]),
                provider_used=selected_provider,
                metadata_json={}
            )
            session.add(script_obj)
            await session.commit()
            script_db_id = script_obj.id
            logger.info(f"Saved generated script to database with ID: {script_db_id}")
    except Exception as e:
        logger.error(f"Failed to persist script to database: {e}")
        raise e

    # Update metadata
    metadata = payload.get("execution_metadata", {})
    metadata["script_id"] = script_db_id

    return {
        "generated_script": script_data,
        "selected_llm_provider": selected_provider,
        "execution_metadata": metadata
    }

def process_job(job_id: str, workflow_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """RQ target function for Script Worker."""
    return run_async(
        execute_job_wrapper(
            job_id=job_id,
            workflow_id=workflow_id,
            payload=payload,
            job_type=JobType.SCRIPT,
            processor_func=_process_script_async
        )
    )
