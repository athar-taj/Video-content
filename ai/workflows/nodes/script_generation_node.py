import logging
from typing import Dict, Any
from ai.generation.script_generator.generator import ScriptGenerator
from ai.workflows.pipeline.provider_router import ProviderRouter

logger = logging.getLogger(__name__)

async def script_generation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Executing Script Generation Node...")
    
    metadata = state.get("execution_metadata", {})
    title = metadata.get("title", "")
    body = metadata.get("body", "")
    subreddit = metadata.get("subreddit", "gaming")
    topic_id = state.get("topic_id", "1")
    workflow_type = state.get("workflow_type", "cheap")
    
    router = ProviderRouter()
    generator = ScriptGenerator()
    
    # Get preference list
    providers_to_try = list(router.llm_chains.get(workflow_type, ["Ollama"]))
    
    last_error = None
    selected_provider = None
    
    for provider_name in providers_to_try:
        logger.info(f"Attempting script generation with provider: {provider_name}")
        try:
            # Generate the script
            # Ensure topic_id is integer for database constraints
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
        logger.critical("All LLM providers failed script generation! Trying Ollama as ultimate fallback.")
        try:
            t_id = int(topic_id) if str(topic_id).isdigit() else 1
            result = await generator.generate_full_script(
                topic_id=t_id,
                title=title,
                raw_body=body,
                subreddit=subreddit,
                target_duration=60,
                provider="Ollama"
            )
            selected_provider = "Ollama"
            script_data = {
                "hook": result.hook,
                "story": result.full_script,
                "full_script": result.full_script,
                "duration": result.metadata.get("estimated_duration", 60)
            }
        except Exception as e:
            logger.exception("Ultimate fallback LLM Ollama failed as well!")
            return {
                "errors": state.get("errors", []) + [f"LLM Generation failed: {str(last_error or e)}"],
                "workflow_status": "failed"
            }
            
    # Persist in Database (like run_script_generation does)
    try:
        from db.repositories.manager import db_manager
        from db.models.script import GeneratedScript
        async for session in db_manager.get_session():
            t_id = int(topic_id) if str(topic_id).isdigit() else 1
            script_obj = GeneratedScript(
                topic_id=t_id,
                hook=script_data["hook"],
                full_script=script_data["full_script"],
                duration_target=60,
                provider=selected_provider,
                model="orchestrated",
                metadata_json={"estimated_duration": script_data["duration"]}
            )
            session.add(script_obj)
            await session.commit()
            # Cache the script ID in metadata
            state_metadata = state.get("execution_metadata", {})
            state_metadata["script_id"] = script_obj.id
            logger.info(f"Saved generated script to database with ID: {script_obj.id}")
    except Exception as e:
        logger.error(f"Failed to persist script to database: {e}")

    return {
        "generated_script": script_data,
        "selected_llm_provider": selected_provider,
        "execution_metadata": state.get("execution_metadata", {})
    }
