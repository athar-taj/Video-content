import time
from typing import Dict, Any, Type
from shared.logging.logger import log
from db.repositories.manager import db_manager
from db.repositories.repository import ContentRepository
from langgraph.graph.state import CompiledStateGraph

class WorkflowRunner:
    """Utility class to execute AI workflows and persist results."""
    
    def __init__(self, workflow: CompiledStateGraph):
        self.workflow = workflow

    async def run(self, initial_state: Dict[str, Any], workflow_type: str = "default") -> Dict[str, Any]:
        log.info(f"🚀 Starting workflow: {workflow_type}")
        start_time = time.time()
        
        # Get DB session
        async for session in db_manager.get_session():
            repo = ContentRepository(session)
            
            try:
                # Execute LangGraph workflow
                final_state = await self.workflow.ainvoke(initial_state)
                
                execution_time = time.time() - start_time
                log.info(f"✅ Workflow {workflow_type} completed in {execution_time:.2f}s")
                
                # If generation workflow, persist specific results
                if workflow_type == "script_generation" and final_state.get("status") == "completed":
                    topic_obj = await repo.create_topic(title=final_state["topic"])
                    await repo.save_script(
                        topic_id=topic_obj.id,
                        hook=final_state["hook"],
                        script=final_state["script"],
                        provider=final_state["provider_used"]
                    )
                
                # Log job status
                status = final_state.get("status", "completed")
                errors = "; ".join(final_state.get("errors", [])) if final_state.get("errors") else None
                await repo.log_job(workflow_type=workflow_type, status=status, errors=errors)
                
                return final_state
                
            except Exception as e:
                log.exception(f"❌ Critical failure in workflow {workflow_type}: {e}")
                await repo.log_job(workflow_type=workflow_type, status="failed", errors=str(e))
                raise
