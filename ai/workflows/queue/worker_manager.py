import subprocess
import sys
import os
import threading
import logging
import time
from typing import List, Dict

logger = logging.getLogger(__name__)

class WorkerManager:
    """Automatically spawns, monitors, streams logs, and terminates background RabbitMQ workers in local testing."""
    
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.threads: List[threading.Thread] = []
        self._running = False
        self._monitor_thread = None

    def start_workers(self):
        """Spawns background worker subprocesses matching General, Render, and Analytics requirements."""
        self._running = True
        queues = ["general_queue", "render_queue", "analytics_queue"]
        python_bin = sys.executable
        
        # Absolute path to rabbitmq_worker.py
        worker_script = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../workers/rabbitmq_worker.py")
        )

        print("\n==================================================")
        print("INITIALIZING DYNAMIC WORKER ORCHESTRATION")
        print("==================================================")

        for q in queues:
            worker_name = f"{q.split('_')[0]}_worker_1"
            logger.info(f"[BOOT] Starting {q.replace('_', ' ').title()} ({worker_name})...")
            
            # Spawn worker subprocess with environment parameters
            cmd = [python_bin, worker_script, "--queue", q, "--name", worker_name]
            p = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
            )
            self.processes[worker_name] = p

            # Launch thread to read and stream worker stdout in real-time
            t = threading.Thread(
                target=self._log_streamer, 
                args=(worker_name, p), 
                daemon=True
            )
            t.start()
            self.threads.append(t)

        # Launch background worker process monitor/health check
        self._monitor_thread = threading.Thread(
            target=self._monitor_health,
            daemon=True
        )
        self._monitor_thread.start()

        print("==================================================\n")

    def _log_streamer(self, name: str, process: subprocess.Popen):
        """Reads lines from the process stdout and streams them directly into the gateway console."""
        while self._running:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                clean_line = line.strip()
                # Remove boilerplate timestamp/levels if present to keep output readable
                if "rabbitmq_worker:" in clean_line:
                    clean_line = clean_line.split("rabbitmq_worker:", 1)[1].strip()
                print(f"[{name.upper()}] {clean_line}")

    def _monitor_health(self):
        """Monitors spawned workers and automatically restarts any crashed processes."""
        python_bin = sys.executable
        worker_script = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../workers/rabbitmq_worker.py")
        )

        while self._running:
            time.sleep(5)
            if not self._running:
                break
                
            for worker_name, p in list(self.processes.items()):
                if p.poll() is not None:
                    logger.warning(f"⚠️ [MONITOR] Worker process '{worker_name}' terminated unexpectedly! Restarting...")
                    
                    q_map = {
                        "general_worker_1": "general_queue",
                        "render_worker_1": "render_queue",
                        "analytics_worker_1": "analytics_queue"
                    }
                    q_name = q_map.get(worker_name, "general_queue")
                    
                    cmd = [python_bin, worker_script, "--queue", q_name, "--name", worker_name]
                    new_p = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                        bufsize=1,
                        cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
                    )
                    self.processes[worker_name] = new_p
                    
                    # Launch new streaming thread
                    t = threading.Thread(
                        target=self._log_streamer, 
                        args=(worker_name, new_p), 
                        daemon=True
                    )
                    t.start()
                    self.threads.append(t)

    def terminate_workers(self):
        """Gracefully shuts down all spawned worker processes."""
        self._running = False
        print("\n==================================================")
        print("SHUTTING DOWN WORKER PROCESSES")
        print("==================================================")
        for name, p in self.processes.items():
            if p.poll() is None:
                logger.info(f"[SHUTDOWN] Terminating worker {name}...")
                p.terminate()
                try:
                    p.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    logger.warning(f"[SHUTDOWN] Worker {name} did not exit. Force killing...")
                    p.kill()
        print("==================================================\n")

# Singleton instance
worker_manager = WorkerManager()
