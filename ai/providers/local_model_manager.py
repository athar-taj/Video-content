import os
import torch
import gc
import logging
import psutil
from typing import Dict, Any, Optional, List, Tuple
from shared.config.settings import settings

logger = logging.getLogger(__name__)

class LocalModelManager:
    """
    Manages local Hugging Face and GGUF models.
    Handles hardware auto-detection (VRAM, RAM, CPU), VRAM-aware model recommendations,
    quantization config, automatic downloading from Hugging Face Hub, preloading/caching loaded models,
    and memory eviction to prevent CUDA Out-Of-Memory (OOM) errors.
    """
    
    def __init__(self):
        self.device = self._detect_device()
        self.vram_gb = self._detect_vram()
        self.ram_gb = psutil.virtual_memory().total / (1024 ** 3)
        self.cpu_cores = psutil.cpu_count(logical=True)
        self.cache_dir = os.path.abspath(settings.HF_MODEL_CACHE)
        
        # Ensure directories exist
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(os.path.join(self.cache_dir, "gguf"), exist_ok=True)
        
        # In-memory model cache to avoid reloading weights
        # Maps model_id -> (model_instance, tokenizer_instance) or Llama instance
        self._loaded_models: Dict[str, Any] = {}

    def _detect_device(self) -> str:
        if getattr(settings, "HF_DEVICE", "auto") != "auto":
            return settings.HF_DEVICE
        return "cuda" if torch.cuda.is_available() else "cpu"

    def _detect_vram(self) -> float:
        if torch.cuda.is_available():
            try:
                # Retrieve total VRAM of default device in GB
                return torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
            except Exception as e:
                logger.warning(f"Failed to query CUDA VRAM: {e}")
                return 0.0
        return 0.0

    def recommend_hardware_tier(self) -> str:
        """Determines the hardware tier (cheap, balanced, premium) based on VRAM/RAM."""
        if self.device == "cuda":
            if self.vram_gb >= 12.0:
                return "premium"
            elif self.vram_gb >= 6.0:
                return "balanced"
            else:
                return "cheap"
        else:
            # CPU execution
            if self.ram_gb >= 16.0:
                return "balanced"
            return "cheap"

    def recommend_model(self, workflow_type: str = "cheap") -> str:
        """Recommends a model based on workflow type and hardware capabilities."""
        tier = self.recommend_hardware_tier()
        
        # Hardware recommendations table
        # Cheap tier: Qwen2.5-3B (or 1.5B/Gemma-2B/Phi-3 if VRAM is very low)
        # Balanced tier: Qwen2.5-7B-Instruct
        # Premium tier: Qwen2.5-14B-Instruct
        if workflow_type == "cheap" or tier == "cheap":
            if self.device == "cpu" or (self.device == "cuda" and self.vram_gb < 4.0):
                return "Qwen/Qwen2.5-1.5B-Instruct"
            return "Qwen/Qwen2.5-3B-Instruct"
        elif workflow_type == "balanced" or tier == "balanced":
            return "Qwen/Qwen2.5-7B-Instruct"
        else:
            # Premium
            return "Qwen/Qwen2.5-14B-Instruct"

    def download_model(self, model_id: str) -> str:
        """Downloads model files from HuggingFace Hub to local cache directory."""
        from huggingface_hub import snapshot_download
        
        is_gguf = "gguf" in model_id.lower() or model_id.endswith(".gguf")
        target_dir = os.path.join(self.cache_dir, "gguf") if is_gguf else self.cache_dir
        
        logger.info(f"[MODEL] Verifying/Downloading model '{model_id}'...")
        
        try:
            if is_gguf:
                # For GGUF repositories, download Q4_K_M GGUF format by default
                repo_id = model_id
                filename = "*.gguf"
                
                # Check if specific model was requested (e.g. Qwen/Qwen2.5-3B-Instruct-GGUF)
                allow_patterns = ["*q4_k_m.gguf", "*Q4_K_M.gguf"]
                if "1.5b" in repo_id.lower():
                    allow_patterns = ["*q4_k_m.gguf", "*Q4_K_M.gguf", "*q8_0.gguf"]
                
                logger.info(f"[MODEL] Downloading GGUF format {allow_patterns} from '{repo_id}'...")
                path = snapshot_download(
                    repo_id=repo_id,
                    allow_patterns=allow_patterns,
                    cache_dir=target_dir,
                    local_files_only=False
                )
                logger.info(f"[MODEL] GGUF model files downloaded successfully at: {path}")
                return path
            else:
                # Standard HF model
                path = snapshot_download(
                    repo_id=model_id,
                    cache_dir=target_dir,
                    local_files_only=False,
                    ignore_patterns=["*.msgpack", "*.h5", "*.ot"]  # Save bandwidth by avoiding non-PyTorch binaries
                )
                logger.info(f"[MODEL] Model '{model_id}' is ready at: {path}")
                return path
        except Exception as e:
            logger.error(f"[MODEL] Failed to download model '{model_id}': {e}")
            raise

    def unload_all_models(self):
        """Clears all loaded models from memory and empties CUDA cache to prevent OOM."""
        if not self._loaded_models:
            return
            
        logger.info("[MODEL] Unloading all cached models from memory...")
        self._loaded_models.clear()
        
        # Explicit garbage collection and CUDA cache empty
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        logger.info("[MODEL] Memory cleared successfully.")

    def load_model(self, model_id: str) -> Tuple[Any, Any]:
        """
        Loads the model and tokenizer from local cache.
        Evicts other models if needed to prevent memory pressure.
        """
        # If already cached in memory, reuse it
        if model_id in self._loaded_models:
            logger.debug(f"[MODEL] Reusing warm model instance for '{model_id}' from memory cache.")
            return self._loaded_models[model_id]
            
        # Ensure only one model remains loaded at a time to prevent OOM
        self.unload_all_models()
        
        # Download model first
        model_path = self.download_model(model_id)
        
        # Check if we should load GGUF or standard Transformers
        is_gguf = "gguf" in model_id.lower() or any(
            f.endswith(".gguf") for root, _, files in os.walk(model_path) for f in files
        )
        
        if is_gguf:
            # Load as GGUF
            instance = self._load_gguf_instance(model_path)
            self._loaded_models[model_id] = (instance, None)
            return instance, None
        else:
            # Load as standard Transformers
            model, tokenizer = self._load_transformers_instance(model_path, model_id)
            self._loaded_models[model_id] = (model, tokenizer)
            return model, tokenizer

    def _load_gguf_instance(self, model_path: str) -> Any:
        """Loads GGUF model using llama-cpp-python."""
        try:
            from llama_cpp import Llama
        except ImportError:
            logger.error("[MODEL] llama-cpp-python is not installed. Falling back to CPU transformers!")
            raise ImportError(
                "llama-cpp-python is required to run GGUF models. "
                "Please run pip install llama-cpp-python or switch to a standard Transformers model."
            )
            
        # Find the actual .gguf file
        gguf_file = None
        for root, _, files in os.walk(model_path):
            for file in files:
                if file.endswith(".gguf"):
                    gguf_file = os.path.join(root, file)
                    break
            if gguf_file:
                break
                
        if not gguf_file:
            raise FileNotFoundError(f"Could not find any GGUF file inside {model_path}")
            
        logger.info(f"[MODEL] Initializing GGUF runtime from: {gguf_file}")
        
        # Configure GPU offloading (offload all layers if CUDA is available, otherwise 0)
        n_gpu_layers = -1 if self.device == "cuda" else 0
        
        llm = Llama(
            model_path=gguf_file,
            n_ctx=2048,
            n_gpu_layers=n_gpu_layers,
            verbose=False
        )
        logger.info(f"[MODEL] GGUF Runtime initialized successfully (GPU layers: {n_gpu_layers}).")
        return llm

    def _load_transformers_instance(self, model_path: str, model_id: str) -> Tuple[Any, Any]:
        """Loads transformers model and tokenizer."""
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        
        logger.info(f"[MODEL] Loading tokenizer for '{model_id}'...")
        tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=True)
        # Fix tokenizer default padding token if missing
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        logger.info(f"[MODEL] Loading PyTorch model for '{model_id}' on '{self.device}'...")
        
        load_kwargs = {
            "pretrained_model_name_or_path": model_path,
            "device_map": self.device if self.device == "cpu" else "auto"
        }
        
        # VRAM-aware quantization config
        if settings.HF_ENABLE_QUANTIZATION and self.device == "cuda":
            try:
                import bitsandbytes
                logger.info("[MODEL] bitsandbytes detected! Activating 4-bit VRAM optimization...")
                quant_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
                load_kwargs["quantization_config"] = quant_config
            except ImportError:
                logger.warning("[MODEL] bitsandbytes package is not installed. Loading model in FP16/BF16 without quantization.")
                load_kwargs["torch_dtype"] = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
        else:
            if self.device == "cuda":
                load_kwargs["torch_dtype"] = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
            else:
                load_kwargs["torch_dtype"] = torch.float32

        model = AutoModelForCausalLM.from_pretrained(**load_kwargs)
        logger.info(f"[MODEL] Model '{model_id}' loaded successfully into memory.")
        return model, tokenizer

# Global instance
local_model_manager = LocalModelManager()
