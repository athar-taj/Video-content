from typing import Dict, Any, Tuple
from ai.workflows.queue.models import JobType

def validate_job_payload(job_type: JobType, payload: Dict[str, Any]) -> Tuple[bool, str]:
    """Validates the payload structure for a specific job type.
    Returns (is_valid, error_message).
    """
    if job_type == JobType.SCRIPT:
        if not payload.get("topic_id"):
            return False, "Missing 'topic_id' in SCRIPT job payload."
        if not payload.get("workflow_type"):
            return False, "Missing 'workflow_type' in SCRIPT job payload."
            
    elif job_type == JobType.TTS:
        script_data = payload.get("generated_script")
        if not script_data or not script_data.get("full_script"):
            # Also support direct script_text
            if not payload.get("script_text"):
                return False, "Missing 'generated_script' or 'script_text' in TTS job payload."
        if not payload.get("script_id"):
            return False, "Missing 'script_id' in TTS job payload."
            
    elif job_type == JobType.SUBTITLE:
        if not payload.get("narration_path"):
            return False, "Missing 'narration_path' in SUBTITLE job payload."
        if not payload.get("script_id"):
            return False, "Missing 'script_id' in SUBTITLE job payload."
            
    elif job_type == JobType.RENDER:
        if not payload.get("scene_timeline_path") and not payload.get("scene_timeline"):
            return False, "Missing 'scene_timeline_path' or 'scene_timeline' in RENDER job payload."
        if not payload.get("narration_path"):
            return False, "Missing 'narration_path' in RENDER job payload."
        if not payload.get("subtitle_path"):
            return False, "Missing 'subtitle_path' in RENDER job payload."
            
    elif job_type == JobType.UPLOAD:
        if not payload.get("final_video_path"):
            return False, "Missing 'final_video_path' in UPLOAD job payload."
        if not payload.get("platform"):
            return False, "Missing target 'platform' in UPLOAD job payload."
            
    elif job_type == JobType.ANALYTICS:
        if not payload.get("video_id"):
            return False, "Missing 'video_id' in ANALYTICS job payload."
        if not payload.get("platform"):
            return False, "Missing 'platform' in ANALYTICS job payload."
            
    return True, ""
