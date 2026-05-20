from typing import List, Dict, Any
from ai.providers.base_provider import BaseLLMProvider, GenerationResponse

class MockLLMProvider(BaseLLMProvider):
    """Mock LLM Provider for local development and integration tests."""

    async def generate(self, prompt: str, **kwargs) -> GenerationResponse:
        content = "This is a mock generated content from the Mock LLM Provider because we are in development mode."
        # If the prompt requests a hook or short story, customize it slightly
        if "hook" in prompt.lower():
            content = "[Mock Hook] You won't believe what this Minecraft player discovered in their singleplayer world!"
        elif "story" in prompt.lower() or "rewrite" in prompt.lower() or "body" in prompt.lower():
            content = "[Mock Story] So I was playing Minecraft on my usual survival world, just mining down at Y level -58. I heard standard cave noises, but then I saw a redstone torch placed. I didn't place it. I followed the trail of redstone torches until I found a sign that said 'Stop looking.' I deleted the world and never played singleplayer again."
            
        return GenerationResponse(
            content=content,
            provider="mock",
            model="mock-gpt",
            usage={"prompt_tokens": 10, "completion_tokens": 50, "total_tokens": 60}
        )

    async def health_check(self) -> bool:
        return True
