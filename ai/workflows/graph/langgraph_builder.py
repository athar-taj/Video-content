import logging
from typing import Dict, Any, List, Optional
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Import Nodes
from ai.workflows.nodes.topic_fetch_node import topic_fetch_node
from ai.workflows.nodes.topic_evaluator_node import topic_evaluator_node
from ai.workflows.nodes.workflow_router_node import workflow_router_node
from ai.workflows.nodes.script_generation_node import script_generation_node
from ai.workflows.nodes.script_validation_node import script_validation_node
from ai.workflows.nodes.rewrite_script_node import rewrite_script_node
from ai.workflows.nodes.tts_generation_node import tts_generation_node
from ai.workflows.nodes.subtitle_generation_node import subtitle_generation_node
from ai.workflows.nodes.scene_mapping_node import scene_mapping_node
from ai.workflows.nodes.render_node import render_node
from ai.workflows.nodes.render_validation_node import render_validation_node
from ai.workflows.nodes.upload_node import upload_node
from ai.workflows.nodes.analytics_feedback_node import analytics_feedback_node

logger = logging.getLogger(__name__)

# Define state representation for LangGraph
class GraphState(TypedDict):
    job_id: str
    topic_id: Optional[str]
    workflow_type: str  # cheap, balanced, premium, rejected
    viral_score: int
    emotional_score: int
    retention_score: int
    selected_llm_provider: Optional[str]
    selected_tts_provider: Optional[str]
    generated_script: Optional[Dict[str, Any]]
    narration_path: Optional[str]
    subtitle_path: Optional[str]
    scene_timeline_path: Optional[str]
    render_output_path: Optional[str]
    retry_count: int
    workflow_status: str
    execution_metadata: Dict[str, Any]
    errors: List[str]
    created_at: Any
    script_valid: bool

class LangGraphBuilder:
    """Builds and compiles the autonomous video production StateGraph."""
    
    @staticmethod
    def route_by_score(state: GraphState) -> str:
        """Route to script generation or reject the workflow."""
        if state.get("workflow_type") == "rejected":
            logger.warning(f"Workflow rejected due to low viral score: {state.get('viral_score')}")
            return "reject"
        return "proceed"

    @staticmethod
    def route_script_validation(state: GraphState) -> str:
        """Decide whether to proceed, rewrite, or fail script stage."""
        if state.get("script_valid"):
            return "valid"
        if state.get("retry_count", 0) < 3:
            return "rewrite"
        logger.error("Script validation failed and retry limit exceeded.")
        return "fail"

    @staticmethod
    def route_render_validation(state: GraphState) -> str:
        """Decide whether to upload or fail render stage."""
        if state.get("workflow_status") == "completed":
            return "proceed"
        return "fail"

    def build_graph(self) -> StateGraph:
        """Construct the full LangGraph state graph."""
        logger.info("Initializing LangGraph StateGraph builder...")
        workflow = StateGraph(GraphState)

        # 1. Register Nodes
        workflow.add_node("fetch_topic", topic_fetch_node)
        workflow.add_node("evaluate_topic", topic_evaluator_node)
        workflow.add_node("route_workflow", workflow_router_node)
        workflow.add_node("generate_script", script_generation_node)
        workflow.add_node("validate_script", script_validation_node)
        workflow.add_node("rewrite_script", rewrite_script_node)
        workflow.add_node("generate_voice", tts_generation_node)
        workflow.add_node("generate_subtitles", subtitle_generation_node)
        workflow.add_node("generate_scene_mapping", scene_mapping_node)
        workflow.add_node("render_video", render_node)
        workflow.add_node("validate_render", render_validation_node)
        workflow.add_node("upload_video", upload_node)
        workflow.add_node("analytics_feedback", analytics_feedback_node)

        # 2. Define Connectivity (Edges)
        workflow.set_entry_point("fetch_topic")
        workflow.add_edge("fetch_topic", "evaluate_topic")
        workflow.add_edge("evaluate_topic", "route_workflow")

        # Conditional routing based on viral evaluation score
        workflow.add_conditional_edges(
            "route_workflow",
            self.route_by_score,
            {
                "proceed": "generate_script",
                "reject": END
            }
        )

        workflow.add_edge("generate_script", "validate_script")

        # Conditional routing for script quality loop
        workflow.add_conditional_edges(
            "validate_script",
            self.route_script_validation,
            {
                "valid": "generate_voice",
                "rewrite": "rewrite_script",
                "fail": END
            }
        )

        # Loop back from rewrite to validation
        workflow.add_edge("rewrite_script", "validate_script")

        # Parallel branches split from voice generation
        workflow.add_edge("generate_voice", "generate_subtitles")
        workflow.add_edge("generate_voice", "generate_scene_mapping")

        # Merge branches at render stage
        workflow.add_edge("generate_subtitles", "render_video")
        workflow.add_edge("generate_scene_mapping", "render_video")

        workflow.add_edge("render_video", "validate_render")

        # Conditional routing based on rendering validation
        workflow.add_conditional_edges(
            "validate_render",
            self.route_render_validation,
            {
                "proceed": "upload_video",
                "fail": END
            }
        )

        workflow.add_edge("upload_video", "analytics_feedback")
        workflow.add_edge("analytics_feedback", END)

        return workflow
