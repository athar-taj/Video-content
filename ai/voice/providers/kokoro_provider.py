import os
import asyncio
from typing import List, Dict, Any
from pathlib import Path
from ai.voice.providers.base_tts_provider import BaseTTSProvider, TTSResponse
from shared.logging.logger import log

try:
    from kokoro import KPipeline, KModel
    import torch
    import soundfile as sf
    KOKORO_AVAILABLE = True
except ImportError:
    KOKORO_AVAILABLE = False


class KokoroProvider(BaseTTSProvider):
    """Local TTS provider supporting custom weights path via KOKORO_MODEL_PATH and automatic fallbacks."""

    def __init__(self):
        self._pipeline = None
        self._device = None

    def _get_pipeline(self):
        if self._pipeline is not None:
            return self._pipeline

        if not KOKORO_AVAILABLE:
            raise ImportError(
                "The 'kokoro' package or dependencies are not available. "
                "Install them using: pip install kokoro soundfile"
            )

        from shared.config.settings import settings
        
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        model_path = getattr(settings, "KOKORO_MODEL_PATH", None)

        if model_path:
            path = Path(model_path)
            if not path.exists():
                raise FileNotFoundError(f"KOKORO_MODEL_PATH specified but does not exist: {model_path}")

            if path.is_dir():
                pth_files = list(path.glob("*.pth"))
                if not pth_files:
                    raise FileNotFoundError(f"No .pth files found in model directory: {model_path}")
                pth_path = str(pth_files[0])
                config_path = str(path / "config.json")
            else:
                pth_path = str(path)
                config_path = str(path.parent / "config.json")

            if not os.path.exists(config_path):
                raise FileNotFoundError(f"config.json not found for model: {config_path}")

            log.info(f"Loading local Kokoro model from {pth_path} (device: {self._device})")
            model = KModel(model=pth_path, config=config_path, repo_id=None).to(self._device).eval()
            self._pipeline = KPipeline(lang_code="a", model=model, device=self._device)
        else:
            log.info(f"Initializing Kokoro KPipeline with auto-download (device: {self._device})")
            self._pipeline = KPipeline(lang_code="a", device=self._device)

        return self._pipeline

    async def generate_audio(self, text: str, voice_id: str, output_path: str, **kwargs) -> TTSResponse:
        log.info(f"Kokoro (Local) generating audio for: {text[:30]}...")

        try:
            # Try to get the real Kokoro pipeline
            pipeline = self._get_pipeline()
            
            # Since pipeline runs inference, run in thread executor to keep event loop unblocked
            loop = asyncio.get_event_loop()
            
            def _inference():
                clean_voice = voice_id
                if clean_voice == "default" or not clean_voice:
                    clean_voice = "af_bella"
                
                # Generate audio using the real Kokoro model
                generator = pipeline(text, voice=clean_voice, speed=kwargs.get("speed", 1.0))
                
                import numpy as np
                audio_pieces = []
                for _, _, audio in generator:
                    if audio is not None and len(audio) > 0:
                        audio_pieces.append(audio)
                        
                if not audio_pieces:
                    raise ValueError("Kokoro TTS returned no audio segments.")
                    
                full_audio = np.concatenate(audio_pieces)
                
                # Ensure parent dir exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # Save to disk as 24kHz mono WAV
                sf.write(output_path, full_audio, 24000)
                
                duration = len(full_audio) / 24000.0
                return duration

            duration = await loop.run_in_executor(None, _inference)

            return TTSResponse(
                audio_path=output_path,
                provider="kokoro",
                voice=voice_id,
                duration_sec=duration,
                file_size_bytes=os.path.getsize(output_path),
                metadata={"type": "local_inference", "device": self._device or "cpu"}
            )

        except Exception as e:
            log.warning(f"Failed to generate audio using real Kokoro pipeline: {e}. Falling back to mock synthesis.")
            return await self._generate_mock_audio(text, voice_id, output_path, **kwargs)

    async def _generate_mock_audio(self, text: str, voice_id: str, output_path: str, **kwargs) -> TTSResponse:
        await asyncio.sleep(0.5)
        
        duration = len(text.split()) / 2.5  # Heuristic
        if duration < 1.0:
            duration = 1.0

        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
        import wave
        import struct
        
        sample_rate = 24000
        num_samples = int(duration * sample_rate)
        with wave.open(output_path, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            silence_frame = struct.pack("<h", 0)
            chunk_size = 10000
            for i in range(0, num_samples, chunk_size):
                current_chunk = min(chunk_size, num_samples - i)
                wav_file.writeframes(silence_frame * current_chunk)
            
        return TTSResponse(
            audio_path=output_path,
            provider="kokoro",
            voice=voice_id,
            duration_sec=duration,
            file_size_bytes=os.path.getsize(output_path),
            metadata={"type": "mock_inference"}
        )

    async def get_available_voices(self) -> List[Dict[str, str]]:
        return [
            {"id": "af_bella", "name": "Bella (Female)"},
            {"id": "am_adam", "name": "Adam (Male)"},
            {"id": "af_sarah", "name": "Sarah (Female)"},
            {"id": "af_nicole", "name": "Nicole (Female)"},
            {"id": "af_sky", "name": "Sky (Female)"},
            {"id": "am_michael", "name": "Michael (Male)"}
        ]

    async def health_check(self) -> bool:
        try:
            if not KOKORO_AVAILABLE:
                return False
            pipeline = self._get_pipeline()
            return pipeline is not None
        except Exception:
            return False
