import asyncio
import logging
from typing import List, Optional, Dict, Any
from ai.subtitles.timestamps.models import WordTimestamp, SubtitleSegment
from ai.subtitles.timestamps.audio_segmenter import AudioSegmenter
from ai.subtitles.timestamps.word_aligner import WordAligner
from ai.subtitles.timestamps.transcript_matcher import TranscriptMatcher
from ai.subtitles.timestamps.timing_optimizer import TimingOptimizer
from ai.subtitles.timestamps.validators import TimestampValidator

logger = logging.getLogger(__name__)

class TimestampGenerator:
    """
    Orchestrates the subtitle generation pipeline.
    """
    def __init__(self, model_size: str = "base", device: str = "cpu", compute_type: str = "int8"):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = None # Lazy load
        
        self.segmenter = AudioSegmenter()
        self.aligner = WordAligner()
        self.matcher = TranscriptMatcher()
        self.optimizer = TimingOptimizer()
        self.validator = TimestampValidator()

    def _load_model(self):
        from shared.config.settings import settings
        if settings.ENV == "development":
            return
        if self.model is None:
            from faster_whisper import WhisperModel
            logger.info(f"Loading Whisper model: {self.model_size} on {self.device}")
            self.model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)

    async def generate_word_timestamps(self, audio_path: str, original_script: Optional[str] = None) -> List[WordTimestamp]:
        """
        Transcribes audio and generates word-level timestamps.
        """
        from shared.config.settings import settings
        self._load_model()
        
        if settings.ENV == "development":
            logger.info("Development mode detected: Generating mock word timestamps.")
            text = original_script or "This is a mock transcription of the narration audio for development."
            words = [w.strip(".,!?\"'") for w in text.split() if w.strip()]
            refined_words = []
            current_time = 0.0
            for pos, w in enumerate(words):
                start = current_time
                end = current_time + 0.35
                refined_words.append(WordTimestamp(
                    word=w,
                    start_time=start,
                    end_time=end,
                    confidence=0.99,
                    position=pos
                ))
                current_time = end + 0.05
            return refined_words
        
        # Preprocess audio
        normalized_audio = self.segmenter.preprocess_audio(audio_path)
        
        # Run transcription in a thread to avoid blocking asyncio loop
        loop = asyncio.get_event_loop()
        segments, info = await loop.run_in_executor(
            None, 
            lambda: self.model.transcribe(normalized_audio, word_timestamps=True)
        )
        
        raw_words = []
        pos = 0
        for segment in segments:
            if segment.words:
                for word in segment.words:
                    raw_words.append(WordTimestamp(
                        word=word.word.strip(),
                        start_time=word.start,
                        end_time=word.end,
                        confidence=word.probability,
                        position=pos
                    ))
                    pos += 1
                    
        # Refine alignments
        refined_words = self.aligner.refine_alignments(raw_words)
        
        # Align with original script if provided
        if original_script:
            refined_words = self.matcher.align_transcript(original_script, refined_words)
            
        return refined_words

    async def generate_segments(self, words: List[WordTimestamp]) -> List[SubtitleSegment]:
        """
        Groups words into readable segments.
        """
        return self.optimizer.optimize_segments(words)

    async def process_pipeline(self, audio_path: str, script: Optional[str] = None) -> Dict[str, Any]:
        """
        Full pipeline: Transcribe -> Align -> Optimize -> Validate.
        """
        import time
        start_time = time.time()
        
        try:
            # Transcription with retry
            max_retries = 2
            for attempt in range(max_retries + 1):
                try:
                    t0 = time.time()
                    words = await self.generate_word_timestamps(audio_path, script)
                    transcription_time = time.time() - t0
                    logger.info(f"Transcription and alignment took {transcription_time:.2f}s")
                    break
                except Exception as e:
                    if attempt == max_retries:
                        raise
                    logger.warning(f"Transcription attempt {attempt + 1} failed, retrying... Error: {e}")
                    await asyncio.sleep(1)

            t1 = time.time()
            segments = await self.generate_segments(words)
            segmentation_time = time.time() - t1
            logger.info(f"Segmentation and optimization took {segmentation_time:.2f}s")
            
            # Validation
            t2 = time.time()
            is_valid = self.validator.validate_word_timestamps(words)
            validation_time = time.time() - t2
            
            total_time = time.time() - start_time
            logger.info(f"Full subtitle pipeline completed in {total_time:.2f}s")
            
            return {
                "words": [w.model_dump() for w in words],
                "segments": [s.model_dump() for s in segments],
                "is_valid": is_valid,
                "language": "en",
                "metrics": {
                    "transcription_time": transcription_time,
                    "segmentation_time": segmentation_time,
                    "total_time": total_time
                }
            }
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}", extra={"audio_path": audio_path})
            raise
