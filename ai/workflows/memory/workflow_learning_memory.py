import logging
from typing import Dict, List, Any
import os
import json

logger = logging.getLogger(__name__)

class WorkflowLearningMemory:
    """Remembers successful generation strategies (best hooks, prompts, etc.) for optimization."""
    
    def __init__(self, memory_file: str = "assets/memory/workflow_learning.json"):
        self.memory_file = memory_file
        self.memory_data: Dict[str, Any] = {
            "best_hooks": [],
            "best_prompts": {},
            "best_narration_styles": {},
            "best_providers": {},
            "successful_runs": 0
        }
        self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r") as f:
                    self.memory_data = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load workflow learning memory: {e}")

    def save_memory(self):
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        try:
            with open(self.memory_file, "w") as f:
                json.dump(self.memory_data, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save workflow learning memory: {e}")

    def record_successful_run(self, hook: str, provider: str, narration_style: str):
        self.memory_data["successful_runs"] += 1
        # Track successful hooks
        if hook not in self.memory_data["best_hooks"]:
            self.memory_data["best_hooks"].append(hook)
            # Keep top 50 hooks
            if len(self.memory_data["best_hooks"]) > 50:
                self.memory_data["best_hooks"].pop(0)
        
        # Increment provider and style stats
        self.memory_data["best_providers"][provider] = self.memory_data["best_providers"].get(provider, 0) + 1
        self.memory_data["best_narration_styles"][narration_style] = self.memory_data["best_narration_styles"].get(narration_style, 0) + 1
        
        self.save_memory()

    def get_recommendations(self) -> Dict[str, Any]:
        """Return recommended styles and providers based on learning history."""
        best_provider = max(self.memory_data["best_providers"], key=self.memory_data["best_providers"].get) if self.memory_data["best_providers"] else None
        best_style = max(self.memory_data["best_narration_styles"], key=self.memory_data["best_narration_styles"].get) if self.memory_data["best_narration_styles"] else None
        
        return {
            "recommended_provider": best_provider,
            "recommended_style": best_style,
            "top_hooks": self.memory_data["best_hooks"][-5:]
        }

workflow_learning_memory = WorkflowLearningMemory()
