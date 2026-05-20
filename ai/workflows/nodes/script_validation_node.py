import logging
from typing import Dict, Any
from ai.validators.script_validator import ScriptValidator
from db.repositories.manager import db_manager
from db.models.validation import ScriptValidation

logger = logging.getLogger(__name__)

async def script_validation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Executing Script Validation Node...")
    
    generated_script = state.get("generated_script")
    if not generated_script:
        logger.error("No generated script found in state for validation.")
        return {"script_valid": False, "errors": state.get("errors", []) + ["No script to validate"]}
        
    script_text = generated_script.get("full_script", "")
    script_id = state.get("execution_metadata", {}).get("script_id", 1)
    
    validator = ScriptValidator()
    
    try:
        # Run validation
        result = await validator.validate(script_id=script_id, script_text=script_text)
        
        logger.info(f"Validation completed. Passed: {result.passed}, Quality Score: {result.quality_score:.2f}")
        
        # Persist validation result to DB (like Phase 2 does)
        try:
            async for session in db_manager.get_session():
                val_obj = ScriptValidation(
                    script_id=script_id,
                    is_valid=result.passed,
                    quality_score=result.quality_score,
                    profanity_score=result.profanity_score,
                    duplicate_score=result.duplicate_score,
                    readability_score=result.readability_score,
                    duration_estimate=result.duration_estimate,
                    failures_json=[{"type": f.type, "message": f.message} for f in result.failures]
                )
                session.add(val_obj)
                await session.commit()
                logger.info(f"Persisted validation results to DB.")
        except Exception as e:
            logger.error(f"Failed to persist validation result to DB: {e}")

        errors = []
        if not result.passed:
            for f in result.failures:
                errors.append(f"Script validation failure [{f.type}]: {f.message}")
            logger.warning(f"Script validation failed. Errors: {errors}")
            
        return {
            "script_valid": result.passed,
            "errors": state.get("errors", []) + errors
        }
    except Exception as e:
        logger.exception(f"Critical error during script validation: {e}")
        return {
            "script_valid": False,
            "errors": state.get("errors", []) + [f"Script validation crashed: {str(e)}"]
        }
