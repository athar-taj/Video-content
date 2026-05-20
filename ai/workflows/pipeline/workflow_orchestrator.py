import logging
from typing import Dict, Any
from .pipeline_engine import PipelineEngine
from .workflow_registry import WorkflowRegistry
from .models import PipelineJob

logger = logging.getLogger(__name__)

class WorkflowOrchestrator:
    """Coordinates workflow modules and executes them via the PipelineEngine."""
    
    def __init__(self):
        self.registry = WorkflowRegistry()
        self._register_default_stages()
        self.engine = PipelineEngine(self.registry)
        
    def _register_default_stages(self):
        """Register the default stage handlers."""
        # In a real implementation, these handlers would import and call the 
        # actual AI modules (e.g., ai.generation.script_engine.generate_script)
        # Here we mock them for testing the pipeline orchestration itself.
        
        async def mock_script_node(context):
            logger.info("Executing Script Generation Node")
            context.script_payload = {
                "sections": [{"type": "hook", "text": "Mock script hook"}]
            }
            
        async def mock_voice_node(context):
            logger.info("Executing Voice Generation Node")
            context.narration_path = "assets/input/audio/narration_test.mp3"
            
        async def mock_subtitle_node(context):
            logger.info("Executing Subtitle Generation Node")
            context.subtitle_path = "assets/ass/test_captions.ass"
            
        async def mock_scene_mapping_node(context):
            logger.info("Executing Scene Mapping Node")
            context.scene_timeline = {"timeline": [{"scene_id": "1", "asset": "test.mp4"}]}
            
        async def mock_render_node(context):
            logger.info("Executing Final Render Node")
            # Create a dummy output file for validation
            import os
            os.makedirs("assets/renders", exist_ok=True)
            output = "assets/renders/orchestrated_output.mp4"
            with open(output, "w") as f:
                f.write("dummy render content")
            context.final_video_path = output
            
        self.registry.register_stage("script", mock_script_node)
        self.registry.register_stage("voice", mock_voice_node)
        self.registry.register_stage("subtitle", mock_subtitle_node)
        self.registry.register_stage("scene_mapping", mock_scene_mapping_node)
        self.registry.register_stage("render", mock_render_node)

    async def run_default_workflow(self, topic_id: str, topic_data: Dict[str, Any]) -> PipelineJob:
        """Run the standard Shorts generation workflow."""
        
        # Define the deterministic stage execution order (could be a LangGraph flow)
        stages = [
            "script",
            "voice",
            "subtitle",
            "scene_mapping",
            "render"
        ]
        
        return await self.engine.execute_pipeline(topic_id, topic_data, stages)
