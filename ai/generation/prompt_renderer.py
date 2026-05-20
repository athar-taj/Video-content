from typing import Dict, Any
from ai.generation.template_loader import TemplateLoader
from ai.generation.placeholder_validator import PlaceholderValidator
from shared.logging.logger import log

class PromptRenderer:
    """Master class for rendering final prompts with validation."""
    
    def __init__(self):
        self.loader = TemplateLoader()
        self.validator = PlaceholderValidator()

    def render(self, template_name: str, variables: Dict[str, Any], provider_override: str = None) -> str:
        """
        Renders a template with provided variables.
        Supports provider-specific overrides by looking in providers/{provider}/{template_name}.
        """
        # 1. Check for provider-specific override
        actual_template = template_name
        if provider_override:
            override_path = f"providers/{provider_override}/{template_name}"
            try:
                # Test if override exists
                self.loader.get_template(override_path)
                actual_template = override_path
                log.debug(f"Using provider override for {provider_override}: {actual_template}")
            except Exception:
                pass # Fallback to default

        # 2. Validate variables
        self.validator.validate(self.loader.env, actual_template, variables)
        
        # 3. Render
        template = self.loader.get_template(actual_template)
        rendered = template.render(**variables)
        
        return rendered.strip()
