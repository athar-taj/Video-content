import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shared.config.settings import settings
from ai.providers.local_model_manager import local_model_manager
from ai.workflows.pipeline.provider_capability_registry import provider_capability_registry
from ai.workflows.pipeline.provider_router import ProviderRouter
from ai.workflows.nodes.workflow_router_node import workflow_router_node
from ai.generation.prompt_engine import PromptEngine

async def run_tests():
    print("==================================================")
    print("[TEST] STARTING LOCAL-FIRST ROUTING UNIT TESTS")
    print("==================================================")
    
    # Mock Ollama status to be True for routing tests to avoid live dependency on local daemon
    orig_is_provider_available = provider_capability_registry.is_provider_available
    async def mock_is_provider_available(provider_name: str) -> bool:
        if provider_name.lower() == "ollama":
            return getattr(settings, "ENABLE_OLLAMA", True)
        return await orig_is_provider_available(provider_name)
    provider_capability_registry.is_provider_available = mock_is_provider_available
    
    passed_tests = 0
    failed_tests = 0

    def assert_equal(actual, expected, test_name):
        nonlocal passed_tests, failed_tests
        if actual == expected:
            print(f"[PASS] {test_name}")
            passed_tests += 1
        else:
            print(f"[FAIL] {test_name} (Expected: {expected}, Got: {actual})")
            failed_tests += 1

    # --------------------------------------------------
    # 1. Test LocalModelManager
    # --------------------------------------------------
    print("\n--- Testing LocalModelManager ---")
    
    # Backup settings
    orig_vram = settings.MAX_VRAM_GB
    orig_size = settings.LOCAL_MODEL_SIZE
    
    try:
        settings.LOCAL_MODEL_SIZE = "auto"
        
        settings.MAX_VRAM_GB = 2.0
        assert_equal(local_model_manager.recommend_local_model(), "qwen2.5:1.5b", "VRAM 2GB -> Small Model")
        
        settings.MAX_VRAM_GB = 8.0
        assert_equal(local_model_manager.recommend_local_model(), "qwen2.5:7b", "VRAM 8GB -> Medium Model")
        
        settings.MAX_VRAM_GB = 16.0
        assert_equal(local_model_manager.recommend_local_model(), "qwen2.5:14b", "VRAM 16GB -> Large Model")
        
        settings.LOCAL_MODEL_SIZE = "small"
        assert_equal(local_model_manager.recommend_local_model(), "qwen2.5:1.5b", "Forced Small Size")
        
        settings.LOCAL_MODEL_SIZE = "large"
        assert_equal(local_model_manager.recommend_local_model(), "qwen2.5:14b", "Forced Large Size")
    finally:
        settings.MAX_VRAM_GB = orig_vram
        settings.LOCAL_MODEL_SIZE = orig_size

    # --------------------------------------------------
    # 2. Test ProviderCapabilityRegistry
    # --------------------------------------------------
    print("\n--- Testing ProviderCapabilityRegistry ---")
    
    orig_enable_openai = settings.ENABLE_OPENAI
    orig_openai_key = settings.OPENAI_API_KEY
    
    try:
        # Mock OpenAI unavailable
        settings.ENABLE_OPENAI = False
        settings.OPENAI_API_KEY = "sk-test-key"
        val = await provider_capability_registry.is_provider_available("openai")
        assert_equal(val, False, "OpenAI disabled by flag")
        
        settings.ENABLE_OPENAI = True
        settings.OPENAI_API_KEY = ""
        val = await provider_capability_registry.is_provider_available("openai")
        assert_equal(val, False, "OpenAI missing API key")
        
        # Mock OpenAI available
        settings.ENABLE_OPENAI = True
        settings.OPENAI_API_KEY = "sk-test-key"
        val = await provider_capability_registry.is_provider_available("openai")
        assert_equal(val, True, "OpenAI fully available")
        
        # Mock provider should always be available
        val = await provider_capability_registry.is_provider_available("mock")
        assert_equal(val, True, "Mock provider available")
    finally:
        settings.ENABLE_OPENAI = orig_enable_openai
        settings.OPENAI_API_KEY = orig_openai_key

    # --------------------------------------------------
    # 3. Test ProviderRouter
    # --------------------------------------------------
    print("\n--- Testing ProviderRouter Chains ---")
    
    orig_enable_openai = settings.ENABLE_OPENAI
    orig_openai_key = settings.OPENAI_API_KEY
    orig_enable_claude = settings.ENABLE_CLAUDE
    orig_enable_sarvam = settings.ENABLE_SARVAM
    orig_sarvam_key = settings.SARVAM_API_KEY
    orig_enable_hf = settings.ENABLE_HF
    orig_hf_token = settings.HF_API_TOKEN
    orig_enable_ollama = settings.ENABLE_OLLAMA
    
    try:
        router = ProviderRouter()
        
        # Test case A: All cloud keys/flags active
        settings.ENABLE_OPENAI = True
        settings.OPENAI_API_KEY = "sk-test"
        settings.ENABLE_CLAUDE = False # Claude doesn't have a key anyway
        settings.ENABLE_SARVAM = True
        settings.SARVAM_API_KEY = "sarvam-test"
        settings.ENABLE_HF = True
        settings.HF_API_TOKEN = "hf-test"
        settings.ENABLE_OLLAMA = True
        
        llm_chain = await router.get_llm_chain("premium_optional_workflow")
        assert_equal("OpenAI" in llm_chain, True, "OpenAI is routed when active")
        
        tts_chain = await router.get_tts_chain("premium_optional_workflow")
        assert_equal("Sarvam" in tts_chain, True, "Sarvam is routed when active")
        
        # Test case B: Disable OpenAI/Sarvam keys -> verify fallback
        settings.OPENAI_API_KEY = ""
        settings.SARVAM_API_KEY = ""
        
        llm_chain = await router.get_llm_chain("premium_optional_workflow")
        assert_equal("OpenAI" in llm_chain, False, "OpenAI filtered out when key missing")
        assert_equal(llm_chain[0], "Ollama", "Fallback to local Ollama")
        
        tts_chain = await router.get_tts_chain("premium_optional_workflow")
        assert_equal("Sarvam" in tts_chain, False, "Sarvam filtered out when key missing")
        assert_equal(tts_chain[0], "Kokoro", "Fallback to local Kokoro")
    finally:
        settings.ENABLE_OPENAI = orig_enable_openai
        settings.OPENAI_API_KEY = orig_openai_key
        settings.ENABLE_CLAUDE = orig_enable_claude
        settings.ENABLE_SARVAM = orig_enable_sarvam
        settings.SARVAM_API_KEY = orig_sarvam_key
        settings.ENABLE_HF = orig_enable_hf
        settings.HF_API_TOKEN = orig_hf_token
        settings.ENABLE_OLLAMA = orig_enable_ollama

    # --------------------------------------------------
    # 4. Test Workflow Router Node Decisions
    # --------------------------------------------------
    print("\n--- Testing Workflow Router Node Decisions ---")
    
    orig_enable_openai = settings.ENABLE_OPENAI
    orig_openai_key = settings.OPENAI_API_KEY
    orig_enable_claude = settings.ENABLE_CLAUDE
    orig_enable_sarvam = settings.ENABLE_SARVAM
    orig_sarvam_key = settings.SARVAM_API_KEY
    orig_enable_hf = settings.ENABLE_HF
    orig_enable_murf = settings.ENABLE_MURF
    
    try:
        # Test Case A: Rejected due to low score
        decision = await workflow_router_node({"viral_score": 25})
        assert_equal(decision["workflow_type"], "rejected", "Low viral score rejected")
        
        # Test Case B: Premium score, cloud available -> premium workflow
        settings.ENABLE_OPENAI = True
        settings.OPENAI_API_KEY = "sk-test"
        decision = await workflow_router_node({"viral_score": 95})
        assert_equal(decision["workflow_type"], "premium_optional_workflow", "High score with keys -> premium_optional_workflow")
        
        # Test Case C: Premium score, cloud unavailable, Sarvam available -> hybrid workflow
        settings.OPENAI_API_KEY = ""
        settings.ENABLE_SARVAM = True
        settings.SARVAM_API_KEY = "sarvam-test"
        decision = await workflow_router_node({"viral_score": 95})
        assert_equal(decision["workflow_type"], "hybrid_workflow", "Missing LLM keys -> hybrid_workflow")
        
        # Test Case D: Offline Mode requested via env
        os.environ["OFFLINE_MODE"] = "true"
        decision = await workflow_router_node({"viral_score": 95})
        assert_equal(decision["workflow_type"], "local_only_workflow", "Offline mode forces local_only_workflow")
        os.environ.pop("OFFLINE_MODE", None)
        
        # Test Case E: All cloud flags disabled -> local only
        settings.ENABLE_OPENAI = False
        settings.ENABLE_CLAUDE = False
        settings.ENABLE_SARVAM = False
        settings.ENABLE_HF = False
        settings.ENABLE_MURF = False
        decision = await workflow_router_node({"viral_score": 95})
        assert_equal(decision["workflow_type"], "local_only_workflow", "All cloud flags disabled -> local_only_workflow")
    finally:
        settings.ENABLE_OPENAI = orig_enable_openai
        settings.OPENAI_API_KEY = orig_openai_key
        settings.ENABLE_CLAUDE = orig_enable_claude
        settings.ENABLE_SARVAM = orig_enable_sarvam
        settings.SARVAM_API_KEY = orig_sarvam_key
        settings.ENABLE_HF = orig_enable_hf
        settings.ENABLE_MURF = orig_enable_murf

    # --------------------------------------------------
    # 5. Test Prompt Optimization
    # --------------------------------------------------
    print("\n--- Testing Prompt Engine Optimization ---")
    
    prompt = "Rewrite the story of the fox."
    opt_script = PromptEngine.optimize_for_local_model(prompt, "script_generation")
    assert_equal("Do NOT include stage directions" in opt_script, True, "Script prompt optimized")
    
    prompt = "Create a hook about gaming."
    opt_hook = PromptEngine.optimize_for_local_model(prompt, "hook_generation")
    assert_equal("Do NOT write any conversational intro" in opt_hook, True, "Hook prompt optimized")

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------
    print("\n==================================================")
    print(f"SUMMARY: Passed {passed_tests} tests, Failed {failed_tests} tests.")
    print("==================================================")
    
    if failed_tests > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(run_tests())
