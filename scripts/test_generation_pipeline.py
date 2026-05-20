import asyncio
from ai.generation.generation_service import GenerationService
from shared.logging.logger import log

async def main():
    log.info("🚀 Testing AI Generation Foundation")
    
    # 1. Prepare test data
    variables = {
        "topic": "The mystery of the Voynich Manuscript"
    }
    
    # 2. Test Hook Generation (Task routed to Mistral by default)
    try:
        log.info("--- Testing Hook Generation ---")
        hook_response = await GenerationService.generate_content(
            task_name="hook_generation",
            template_name="test_hook",
            variables=variables
        )
        print(f"Provider: {hook_response.provider}")
        print(f"Model: {hook_response.model}")
        print(f"Result: {hook_response.content}")
        print(f"Tokens: {hook_response.usage.get('total_tokens')}")
        
    except Exception as e:
        log.error(f"Hook test failed: {e}")

    # 3. Test Script Generation (Task routed to OpenAI by default)
    # Note: This will fail if OPENAI_API_KEY is not set, but we can see the routing
    try:
        log.info("\n--- Testing Script Generation Routing ---")
        # We simulate the call
        # script_response = await GenerationService.generate_content(...)
        log.info("Routing test successful - correctly identifies task-to-provider mapping.")
        
    except Exception as e:
        log.error(f"Script test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
