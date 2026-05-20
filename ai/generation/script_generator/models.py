from pydantic import BaseModel
from typing import Dict, Any, Optional, List

class ScriptStage(BaseModel):
    hook: str
    story: str
    cta: str = "Subscribe for more stories."
    estimated_duration_sec: float = 0.0

class ScriptGenerationResult(BaseModel):
    id: Optional[int] = None
    topic_id: int
    hook: str
    full_script: str
    metadata: Dict[str, Any] = {}
    provider: str
    model: str
    duration_target: int
    quality_score: float = 0.0
