import logging
import os
import sys

logger = logging.getLogger(__name__)

class WorkerHealthMonitor:
    """Monitors system resource utilization (CPU, memory) and logs metrics."""

    def get_resource_metrics(self) -> dict:
        """Retrieves current CPU and Memory usage.
        Gracefully falls back if psutil is not installed.
        """
        metrics = {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "gpu_usage": "N/A"
        }
        
        try:
            import psutil
            metrics["cpu_percent"] = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()
            metrics["memory_percent"] = mem.percent
        except ImportError:
            # Fallback when psutil is not available
            pass
        except Exception as e:
            logger.warning(f"Error reading resource metrics: {e}")
            
        # GPU detection placeholder (e.g. check nvidia-smi if on Windows/Linux)
        # In a real environment, we'd execute nvidia-smi or use gpustat
        return metrics

    def log_health_status(self) -> None:
        metrics = self.get_resource_metrics()
        logger.info(f"System Health: CPU: {metrics['cpu_percent']}% | Memory: {metrics['memory_percent']}% | GPU: {metrics['gpu_usage']}")
        
        # Log warnings if resources are exhausted
        if metrics["cpu_percent"] > 90.0:
            logger.warning("⚠️ High CPU usage detected!")
        if metrics["memory_percent"] > 90.0:
            logger.warning("⚠️ High memory usage detected!")

# Singleton instance
worker_health_monitor = WorkerHealthMonitor()
