import logging
from typing import Dict, Any, Optional
from datetime import datetime
from langgraph.checkpoint.memory import MemorySaver

from ai.workflows.graph.langgraph_builder import LangGraphBuilder
from ai.workflows.memory.redis_checkpoint_saver import RedisCheckpointSaver
from ai.workflows.pipeline.workflow_registry import WorkflowRegistry
from db.repositories.manager import db_manager
from db.models.database import WorkflowJob

logger = logging.getLogger(__name__)

class LangGraphOrchestrator:
    """The master orchestrator using LangGraph to run autonomous video generation."""
    
    def __init__(self, registry: Optional[WorkflowRegistry] = None):
        self.registry = registry or WorkflowRegistry()
        self.builder = LangGraphBuilder()
        self.graph = self._compile_graph()

    def _compile_graph(self):
        """Compile the state graph with persistent Redis checkpointing."""
        workflow = self.builder.build_graph()
        
        # Try to use Redis checkpointer, fallback to MemorySaver
        try:
            checkpointer = RedisCheckpointSaver()
            logger.info("Compiled LangGraph with RedisCheckpointSaver.")
        except Exception as e:
            logger.warning(f"Failed to initialize Redis checkpointer: {e}. Falling back to MemorySaver.")
            checkpointer = MemorySaver()
            
        return workflow.compile(checkpointer=checkpointer)

    async def execute_workflow(self, job_id: str, topic_id: str, forced_score: Optional[int] = None) -> Dict[str, Any]:
        """Runs the autonomous video production pipeline for a given job and topic."""
        logger.info(f"🚀 Triggering LangGraph Autonomous Pipeline for Job: {job_id}, Topic: {topic_id}")
        
        # 1. Initialize state variables
        initial_state = {
            "job_id": job_id,
            "topic_id": topic_id,
            "workflow_type": "cheap",
            "viral_score": 0,
            "emotional_score": 0,
            "retention_score": 0,
            "selected_llm_provider": None,
            "selected_tts_provider": None,
            "generated_script": None,
            "narration_path": None,
            "subtitle_path": None,
            "scene_timeline_path": None,
            "render_output_path": None,
            "retry_count": 0,
            "workflow_status": "pending",
            "execution_metadata": {"forced_score": forced_score} if forced_score else {},
            "errors": [],
            "created_at": datetime.utcnow().isoformat(),
            "script_valid": False
        }
        
        # 2. Record initial job state in PostgreSQL
        async with db_manager.session_factory() as session:
            job_obj = WorkflowJob(
                workflow_type="cheap",
                status="pending",
                state_snapshot=initial_state
            )
            session.add(job_obj)
            await session.commit()
            db_job_id = job_obj.id
            logger.info(f"Recorded initial workflow job in database with ID: {db_job_id}")

        # Config for checkpoints (thread-based isolation)
        config = {
            "configurable": {
                "thread_id": job_id
            }
        }
        
        try:
            # Update DB to running status
            async with db_manager.session_factory() as session:
                job_obj = await session.get(WorkflowJob, db_job_id)
                if job_obj:
                    job_obj.status = "running"
                    await session.commit()

            # 3. Invoke StateGraph
            final_state = await self.graph.ainvoke(initial_state, config=config)
            
            # 4. Save success / final state back to DB
            status = final_state.get("workflow_status", "completed")
            errors_str = "; ".join(final_state.get("errors", [])) if final_state.get("errors") else None
            
            async with db_manager.session_factory() as session:
                job_obj = await session.get(WorkflowJob, db_job_id)
                if job_obj:
                    job_obj.workflow_type = final_state.get("workflow_type", "cheap")
                    job_obj.status = status
                    job_obj.errors = errors_str
                    job_obj.completed_at = datetime.utcnow()
                    job_obj.state_snapshot = final_state
                    await session.commit()
            
            logger.info(f"🏁 Workflow completed. Status: {status}. Output: {final_state.get('render_output_path')}")
            return final_state
            
        except Exception as e:
            logger.exception(f"Critical workflow failure in LangGraph orchestrator: {e}")
            
            # Save failure snapshot to DB
            async with db_manager.session_factory() as session:
                job_obj = await session.get(WorkflowJob, db_job_id)
                if job_obj:
                    job_obj.status = "failed"
                    job_obj.errors = str(e)
                    job_obj.completed_at = datetime.utcnow()
                    job_obj.state_snapshot = {"error": str(e)}
                    await session.commit()
                    
            raise e
