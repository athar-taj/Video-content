import os
from typing import Dict
from shared.logging.logger import log

class PromptEngine:
    _base_path = os.path.join("ai", "prompts")

    @classmethod
    def load_prompt(cls, filename: str, variables: Dict[str, str]) -> str:
        """Load a prompt template and replace variables."""
        try:
            path = os.path.join(cls._base_path, filename)
            if not os.path.exists(path):
                log.error(f"Prompt file not found: {path}")
                return ""
                
            with open(path, "r", encoding="utf-8") as f:
                template = f.read()
            
            return template.format(**variables)
        except Exception as e:
            log.error(f"Error loading prompt {filename}: {e}")
            return ""

# Example prompts (already created in previous turn, but ensuring they are there)
