import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional
from .models import VoicePreset

class ConfigLoader:
    """
    Handles loading and parsing of voice preset configuration files.
    """
    
    @staticmethod
    def load_from_yaml(file_path: Path) -> Dict[str, Any]:
        with open(file_path, "r") as f:
            return yaml.safe_load(f)

    @staticmethod
    def load_from_json(file_path: Path) -> Dict[str, Any]:
        with open(file_path, "r") as f:
            return json.load(f)

    @classmethod
    def load_preset(cls, file_path: Path) -> VoicePreset:
        if file_path.suffix in [".yaml", ".yml"]:
            data = cls.load_from_yaml(file_path)
        elif file_path.suffix == ".json":
            data = cls.load_from_json(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        return VoicePreset(**data)
