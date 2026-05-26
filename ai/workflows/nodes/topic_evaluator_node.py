import logging
import json
import re
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def topic_evaluator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Executing Topic Evaluator Node...")
    metadata = state.get("execution_metadata", {})
    title = metadata.get("title", "")
    body = metadata.get("body", "")
    
    # Check if forced_score is provided in execution_metadata or state
    forced_score = metadata.get("forced_score") or state.get("execution_metadata", {}).get("forced_score")
    if forced_score:
        logger.info(f"Using forced viral score: {forced_score}")
        return {
            "viral_score": forced_score,
            "emotional_score": forced_score,
            "retention_score": forced_score
        }

    prompt = f"""
Evaluate the viral potential of the following topic for a short-form video (TikTok/Reels/Shorts).
Title: {title}
Body: {body}

Provide a JSON object containing:
1. "viral_score" (integer 0-100)
2. "emotional_score" (integer 0-100)
3. "retention_score" (integer 0-100)

Return ONLY the raw JSON object. Do not include markdown formatting or wrapper text.
"""
    viral_score = 50
    emotional_score = 50
    retention_score = 50
    
    try:
        from ai.providers.factory import ProviderRouter
        provider = await ProviderRouter.get_provider_for_task("validation")
        response = await provider.generate(prompt=prompt, max_tokens=150)
        
        # GenerationResponse wraps output in .content
        content = response.content if hasattr(response, "content") else str(response)
        
        # Parse JSON
        match = re.search(r"\{.*?\}", content, re.DOTALL)
        if match:
            data = json.loads(match.group(0))
            viral_score = int(data.get("viral_score", 50))
            emotional_score = int(data.get("emotional_score", 50))
            retention_score = int(data.get("retention_score", 50))
    except Exception as e:
        logger.error(f"Failed to evaluate topic via local LLM: {e}. Using baseline scores of 50.")
        
    logger.info(f"Evaluated Scores - Viral: {viral_score}, Emotional: {emotional_score}, Retention: {retention_score}")
    return {
        "viral_score": viral_score,
        "emotional_score": emotional_score,
        "retention_score": retention_score
    }
