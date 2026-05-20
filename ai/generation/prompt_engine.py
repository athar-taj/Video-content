import os
from typing import Dict, Any
from shared.config.settings import settings
from shared.logging.logger import log

class PromptEngine:
    """Engine for managing and loading prompt templates."""
    
    BASE_DIR = "ai/prompts"

    @classmethod
    def load_prompt(cls, template_path: str, variables: Dict[str, Any]) -> str:
        """Loads a template and injects variables."""
        full_path = os.path.join(cls.BASE_DIR, template_path)
        
        if not os.path.exists(full_path):
            log.error(f"Prompt template not found: {full_path}")
            raise FileNotFoundError(f"Template not found: {template_path}")
            
        with open(full_path, "r", encoding="utf-8") as f:
            template = f.read()
            
        # Replace placeholders {{variable}}
        for key, value in variables.items():
            placeholder = "{{" + key + "}}"
            template = template.replace(placeholder, str(value))
            
        return template

    @staticmethod
    def get_template_path(category: str, name: str) -> str:
        return f"{category}/{name}.txt"
