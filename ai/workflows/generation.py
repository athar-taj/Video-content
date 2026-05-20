import time
from typing import TypedDict, Optional, List, Dict
from langgraph.graph import StateGraph, END
from ai.providers.factory import ProviderFactory
from ai.prompts.engine import PromptEngine
from shared.logging.logger import log

class WorkflowState(TypedDict):
    # Inputs
    topic: str
    
    # Intermediate / Outputs
    hook: Optional[str]
    script: Optional[str]
    provider_used: Optional[str]
    
    # Metadata
    start_time: float
    execution_time: float
    status: str
    errors: List[str]
    quality_score: float

async def fetch_topic_node(state: WorkflowState) -> WorkflowState:
    log.info(f"🚀 Starting workflow for topic: {state['topic']}")
    state["start_time"] = time.time()
    state["status"] = "processing"
    return state

async def generate_hook_node(state: WorkflowState) -> WorkflowState:
    try:
        provider = await ProviderFactory.get_provider_for_task("hook_generation")
        model = ProviderFactory.get_model_for_provider(state.get("provider_used") or "mistral", "hook_generation")
        
        prompt = PromptEngine.load_prompt("hook_v1.txt", {"topic": state["topic"]})
        
        hook = await provider.generate(prompt, model=model)
        state["hook"] = hook.strip()
        state["provider_used"] = f"{provider.__class__.__name__} ({model})"
        return state
    except Exception as e:
        state["errors"].append(f"Hook Error: {str(e)}")
        return state

async def generate_script_node(state: WorkflowState) -> WorkflowState:
    if not state["hook"] or len(state["hook"]) < 5:
        state["errors"].append("Hook generation failed or too short")
        return state

    try:
        provider = await ProviderFactory.get_provider_for_task("script_generation")
        model = ProviderFactory.get_model_for_provider("mistral", "script_generation")
        
        prompt = PromptEngine.load_prompt("script_v1.txt", {
            "topic": state["topic"],
            "hook": state["hook"]
        })
        
        script = await provider.generate(prompt, model=model)
        state["script"] = script.strip()
        return state
    except Exception as e:
        state["errors"].append(f"Script Error: {str(e)}")
        return state

async def validate_script_node(state: WorkflowState) -> WorkflowState:
    log.info("🔍 Validating script content...")
    script = state.get("script", "")
    
    if not script:
        state["errors"].append("Validation: Script is empty")
        state["status"] = "failed"
        return state
        
    if len(script) < 50:
        state["errors"].append("Validation: Script too short")
        state["status"] = "failed"
        return state

    state["status"] = "validated"
    state["quality_score"] = 0.9
    return state

async def save_result_node(state: WorkflowState) -> WorkflowState:
    state["execution_time"] = time.time() - state["start_time"]
    log.info(f"✅ Workflow completed in {state['execution_time']:.2f}s")
    state["status"] = "completed"
    return state

def create_generation_workflow():
    workflow = StateGraph(WorkflowState)
    
    workflow.add_node("fetch_topic", fetch_topic_node)
    workflow.add_node("generate_hook", generate_hook_node)
    workflow.add_node("generate_script", generate_script_node)
    workflow.add_node("validate", validate_script_node)
    workflow.add_node("save_result", save_result_node)
    
    workflow.set_entry_point("fetch_topic")
    workflow.add_edge("fetch_topic", "generate_hook")
    workflow.add_edge("generate_hook", "generate_script")
    workflow.add_edge("generate_script", "validate")
    
    workflow.add_conditional_edges(
        "validate",
        lambda x: "save_result" if x["status"] == "validated" else END,
        {"save_result": "save_result", END: END}
    )
    
    workflow.add_edge("save_result", END)
    return workflow.compile()

script_gen_workflow = create_generation_workflow()
