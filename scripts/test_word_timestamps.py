import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.subtitles.timestamps.timestamp_generator import TimestampGenerator
from shared.logging.logger import log

async def test_pipeline():
    log.info("Testing Word Timestamp Generation Pipeline")
    
    # We need a test audio file. Since we don't have one, we'll log that.
    # In a real scenario, you'd provide a path to a small mp3/wav file.
    test_audio = "assets/subtitles/temp/test_audio.mp3"
    
    if not os.path.exists(test_audio):
        log.warning(f"Test audio not found at {test_audio}. Please provide a valid audio file to run the full test.")
        log.info("You can run: python scripts/run_word_timestamp_generation.py --audio <path_to_audio>")
        return

    generator = TimestampGenerator(model_size="tiny") # Use tiny for fast testing
    
    try:
        log.info(f"Processing {test_audio}...")
        results = await generator.process_pipeline(test_audio)
        
        print("\n--- TIMING OUTPUT ---")
        for seg in results["segments"][:5]: # Show first 5 segments
            print(f"[{seg['start_time']:.2f} - {seg['end_time']:.2f}] {seg['text']}")
            
        print("\n--- WORD LEVEL (First 10) ---")
        for word in results["words"][:10]:
            print(f"  {word['word']} ({word['start_time']:.2f} - {word['end_time']:.2f})")
            
        print(f"\nValidation Result: {'PASSED' if results['is_valid'] else 'FAILED'}")
        
    except Exception as e:
        log.error(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_pipeline())
