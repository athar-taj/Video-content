import re
from typing import Dict, Any, List
from shared.logging.logger import log

class StructureValidator:
    """Validates the storytelling structure of a script."""
    
    def validate(self, script_text: str) -> Dict[str, Any]:
        """
        Checks for key components: Hook, Setup/Story, and CTA.
        """
        has_hook = bool(re.search(r"HOOK:|\[Hook\]", script_text, re.I)) or len(script_text.splitlines()[0]) < 100
        has_cta = bool(re.search(r"CTA:|FOLLOW|SUBSCRIBE|CLICK", script_text, re.I))
        
        # Heuristic: A good story has at least 3 distinct paragraphs or sections
        lines = [l for l in script_text.split("\n") if l.strip()]
        has_progression = len(lines) >= 3
        
        return {
            "has_hook": has_hook,
            "has_cta": has_cta,
            "has_progression": has_progression,
            "score": sum([has_hook, has_cta, has_progression]) / 3
        }
