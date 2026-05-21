import os
from typing import Dict, Any
from shared.config.settings import settings
from shared.logging.logger import log

class PromptEngine:
    """Engine for managing and loading prompt templates, and optimizing them for local models."""
    
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

    @classmethod
    def optimize_for_local_model(cls, prompt: str, task_name: str) -> str:
        """
        Enhances the prompt to optimize response quality for local, quantized models (like Qwen 7B/1.5B).
        Appends strict format constraints to minimize context noise and prevent conversational filler or stage directions.
        """
        system_constraint = (
            "\n\n--- STRICT SYSTEM CONSTRAINTS FOR LOCAL LLM ---\n"
            "You are a precise, production-grade text generation engine. "
            "Please follow these instructions with absolute strictness:\n"
        )
        
        task_lower = task_name.lower()
        if "hook" in task_lower:
            system_constraint += (
                "- Do NOT write any conversational intro or outro (e.g. do not write 'Here is your hook:' or 'Sure!').\n"
                "- Output ONLY the raw hook text itself.\n"
                "- Do NOT wrap the hook in quotation marks.\n"
                "- Output exactly one single line containing only the hook."
            )
        elif "script" in task_lower or "rewrite" in task_lower:
            system_constraint += (
                "- Output ONLY the spoken narration script. Do NOT write any intros, outros, or explanations.\n"
                "- Do NOT include stage directions, bracketed instructions (like '[music pauses]' or '[Narrator]'), or scene descriptions.\n"
                "- Ensure the output contains only the actual words to be read aloud.\n"
                "- Strip out any conversational preamble."
            )
        elif "evaluate" in task_lower or "eval" in task_lower:
            system_constraint += (
                "- Output ONLY a valid, parseable JSON object.\n"
                "- Do NOT wrap the response in markdown blocks like ```json ... ```.\n"
                "- Do NOT include any explanations or commentary outside the JSON."
            )
        else:
            system_constraint += (
                "- Output only the exact text requested. No chat preamble or conversational fluff."
            )
            
        return prompt.strip() + system_constraint

