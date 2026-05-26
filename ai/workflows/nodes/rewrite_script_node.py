import logging
import re
from typing import Dict, Any
from ai.providers.factory import ProviderFactory

logger = logging.getLogger(__name__)

async def rewrite_script_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Executing Rewrite Script Node...")
    
    script_data = state.get("generated_script", {})
    script_text = script_data.get("full_script", "")
    errors = state.get("errors", [])
    retry_count = state.get("retry_count", 0) + 1
    llm_provider = state.get("selected_llm_provider", "Ollama")
    
    error_summary = "\n".join([f"- {err}" for err in errors[-3:]]) # Take last few errors
    
    logger.info(f"Script rewrite cycle: {retry_count}. Fixing errors:\n{error_summary}")
    
    prompt = f"""
You are an expert editor. Rewrite the following short-form script to fix the validation errors.
Ensure you maintain a hook at the start, a conversational story, and a clear call-to-action (CTA) at the end.

Previous Script:
\"\"\"
{script_text}
\"\"\"

Validation Errors to Fix:
{error_summary}

Return ONLY the rewritten script. Do not include editing notes, markdown wrappers, or intro/outro text.
"""
    
    rewritten_text = script_text
    try:
        provider = ProviderFactory.get_provider(llm_provider)
        response = await provider.generate(prompt=prompt, max_tokens=1000)
        content = response.content if hasattr(response, "content") else str(response)
        rewritten_text = content.strip()
        logger.info("Successfully obtained rewritten script from LLM.")
    except Exception as e:
        logger.error(f"Failed to rewrite script via LLM: {e}. Keeping previous script.")
        
    # Split rewritten_text into hook and story for consistency if possible
    lines = rewritten_text.split("\n\n")
    hook = lines[0] if lines else "Listen up!"
    story = rewritten_text
    
    updated_script_data = {
        "hook": hook,
        "story": story,
        "full_script": rewritten_text,
        "duration": script_data.get("duration", 60) # Preserve duration
    }
    
    # Update script in DB if script_id is known
    script_id = state.get("execution_metadata", {}).get("script_id")
    if script_id:
        try:
            from db.repositories.manager import db_manager
            from db.models.script import GeneratedScript
            from sqlalchemy import update
            async with db_manager.get_session() as session:
                stmt = update(GeneratedScript).where(GeneratedScript.id == script_id).values(
                    hook=hook,
                    full_script=rewritten_text,
                    provider=llm_provider
                )
                await session.execute(stmt)
                await session.commit()
                logger.info(f"Updated script ID {script_id} in the database.")
        except Exception as e:
            logger.error(f"Failed to update script in database: {e}")

    return {
        "generated_script": updated_script_data,
        "retry_count": retry_count,
        # Clear errors so validation node starts fresh
        "errors": []
    }
