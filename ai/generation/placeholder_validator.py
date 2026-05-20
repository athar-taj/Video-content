from jinja2 import meta
from typing import Set, Dict, Any
from shared.logging.logger import log

class PlaceholderValidator:
    """Validates that all required placeholders in a template are provided."""
    
    @staticmethod
    def get_undeclared_variables(env, template_source: str) -> Set[str]:
        """Extracts all variable names from a Jinja2 template string."""
        ast = env.parse(template_source)
        return meta.find_undeclared_variables(ast)

    @classmethod
    def validate(cls, env, template_name: str, variables: Dict[str, Any]):
        """Validates that all variables needed by the template are present."""
        template_source = env.loader.get_source(env, template_name)[0]
        required = cls.get_undeclared_variables(env, template_source)
        
        missing = required - set(variables.keys())
        if missing:
            log.error(f"Missing placeholders for template {template_name}: {missing}")
            raise ValueError(f"Missing variables: {missing}")
            
        return True
