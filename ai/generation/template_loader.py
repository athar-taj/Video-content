import os
from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateNotFound
from shared.logging.logger import log

class TemplateLoader:
    """Handles loading and caching Jinja2 templates for prompts."""
    
    def __init__(self, base_path: str = "ai/prompts"):
        self.base_path = base_path
        self.env = Environment(
            loader=FileSystemLoader(self.base_path),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def get_template(self, template_name: str):
        """Loads a template by its relative path."""
        try:
            return self.env.get_template(template_name)
        except TemplateNotFound:
            log.error(f"Prompt template not found: {template_name} in {self.base_path}")
            raise
        except Exception as e:
            log.error(f"Error loading template {template_name}: {e}")
            raise

    def list_templates(self):
        """Lists all available templates."""
        return self.env.list_templates()
