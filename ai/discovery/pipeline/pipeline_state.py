from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class PipelineMetrics(BaseModel):
    total_fetched: int = 0
    total_filtered: int = 0
    total_duplicates: int = 0
    total_stored: int = 0
    total_comments: int = 0
    duration_ms: float = 0.0
    start_time: datetime = Field(default_factory=datetime.utcnow)

class DiscoveryState(BaseModel):
    """Immutable-safe state object for the content discovery pipeline."""
    
    # Data Stages
    raw_topics: List[Dict[str, Any]] = []
    processed_topics: List[Dict[str, Any]] = []
    final_topics: List[Dict[str, Any]] = []
    
    # Execution Tracking
    metrics: PipelineMetrics = Field(default_factory=PipelineMetrics)
    errors: List[str] = []
    current_stage: str = "initialized"
    is_complete: bool = False
    
    def update_metrics(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self.metrics, key):
                setattr(self.metrics, key, getattr(self.metrics, key) + value)

    def log_error(self, error: str):
        self.errors.append(f"[{datetime.utcnow().isoformat()}] {error}")
