import time
from typing import List, Dict, Any
from ai.validators.profanity_filter import ProfanityFilter
from ai.validators.duplicate_detector import DuplicateScriptDetector
from ai.validators.structure_validator import StructureValidator
from ai.validators.models import ValidationResult, ValidationFailure
from ai.generation.script_generator.duration_controller import DurationController
from shared.logging.logger import log

class ScriptValidator:
    """Master orchestrator for AI script quality control."""
    
    def __init__(self):
        self.profanity = ProfanityFilter()
        self.duplicate = DuplicateScriptDetector()
        self.structure = StructureValidator()

    async def validate(self, script_id: int, script_text: str, historical_scripts: List[str] = None) -> ValidationResult:
        log.info(f"🛡️ Validating script {script_id}...")
        start_time = time.time()
        
        failures = []
        
        # 1. Profanity & Safety
        p_score, p_matches = self.profanity.analyze(script_text)
        if p_score > 0.1: # Threshold
            failures.append(ValidationFailure(type="profanity", message=f"Found: {', '.join(p_matches)}"))

        # 2. Length & Duration
        duration = DurationController.estimate_duration(script_text)
        if duration < 15:
            failures.append(ValidationFailure(type="duration", message=f"Too short ({int(duration)}s)"))
        elif duration > 120:
            failures.append(ValidationFailure(type="duration", message=f"Too long ({int(duration)}s)"))

        # 3. Structure
        s_result = self.structure.validate(script_text)
        if not s_result["has_hook"]:
            failures.append(ValidationFailure(type="structure", message="Missing clear hook"))
        if not s_result["has_cta"]:
            log.warning(f"Script {script_id} missing CTA - continuing as warning")

        # 4. Duplicate Check
        is_dup = False
        if historical_scripts:
            is_dup = self.duplicate.is_too_similar(script_text, historical_scripts)
            if is_dup:
                failures.append(ValidationFailure(type="duplicate", message="Near-duplicate content detected"))

        # 5. Aggregate Results
        passed = len([f for f in failures if f.type != "warning"]) == 0
        
        # Simple quality heuristic
        quality_score = (1.0 - p_score) * 0.4 + s_result["score"] * 0.4 + (0.0 if is_dup else 0.2)

        return ValidationResult(
            script_id=script_id,
            passed=passed,
            quality_score=quality_score,
            profanity_score=p_score,
            duplicate_score=1.0 if is_dup else 0.0,
            readability_score=0.8, # Placeholder
            duration_estimate=duration,
            failures=failures,
            metadata={"validation_time": time.time() - start_time}
        )
