from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ValidationFailure(BaseModel):
    type: str
    message: str

class ValidationResult(BaseModel):
    script_id: int
    passed: bool
    quality_score: float
    profanity_score: float
    duplicate_score: float
    readability_score: float
    duration_estimate: float
    failures: List[ValidationFailure] = []
    metadata: Dict[str, Any] = {}
