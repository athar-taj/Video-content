from ai.generation.prompt_renderer import PromptRenderer
from shared.logging.logger import log

def test_prompt_engine():
    log.info("🚀 Testing Advanced Prompt Template Engine")
    
    renderer = PromptRenderer()
    
    # 1. Test basic rendering with logic
    log.info("--- Testing Conditional Rendering ---")
    vars_suspense = {
        "topic": "The hidden room in my basement",
        "subreddit": "confessions",
        "tone": "suspense"
    }
    
    output = renderer.render("hooks/viral_hook_v1.txt", vars_suspense)
    print(f"Suspense Output:\n{output}\n")
    
    vars_shock = {
        "topic": "I found out my boss is my biological father",
        "subreddit": "offmychest",
        "tone": "shock"
    }
    output = renderer.render("hooks/viral_hook_v1.txt", vars_shock)
    print(f"Shock Output:\n{output}\n")

    # 2. Test validation failure
    log.info("--- Testing Validation Failure ---")
    try:
        renderer.render("hooks/viral_hook_v1.txt", {"topic": "Missing Tone"})
    except ValueError as e:
        log.info(f"✅ Successfully caught missing variable: {e}")

    log.info("--- Prompt Engine Test Complete ---")

if __name__ == "__main__":
    test_prompt_engine()
