import redis
import logging
import importlib
import os
from rq import Queue
from shared.config.settings import settings

logger = logging.getLogger(__name__)

class MockQueue:
    """Mock RQ Queue that runs jobs synchronously when Redis is unavailable or offline mode is active."""
    
    def __init__(self, name: str):
        self.name = name

    def enqueue_call(self, func, args=(), kwargs=None, job_id=None, timeout=None, result_ttl=None, **other_kwargs):
        logger.info(f"[MockQueue] Synchronously executing {func} in a separate thread with args={args} kwargs={kwargs}")
        if kwargs is None:
            kwargs = {}
            
        import threading
        result_holder = {}
        
        def run_in_thread():
            try:
                # Dynamically import and execute the target function
                module_path, func_name = func.rsplit(".", 1)
                module = importlib.import_module(module_path)
                target_func = getattr(module, func_name)
                
                # Execute target function (which handles its own run_async)
                result_holder['result'] = target_func(*args, **kwargs)
            except Exception as e:
                logger.exception(f"[MockQueue Thread] Failed to execute job {job_id}: {e}")
                result_holder['error'] = e

        t = threading.Thread(target=run_in_thread)
        t.start()
        t.join()
        
        if 'error' in result_holder:
            raise result_holder['error']
            
        # Return a mock job object containing the result
        class MockJob:
            def __init__(self, j_id, res):
                self.id = j_id
                self.result = res
        return MockJob(job_id, result_holder.get('result'))

    def enqueue_in(self, delay, func, args=(), kwargs=None, job_id=None, timeout=None, result_ttl=None, **other_kwargs):
        # Synchronously run immediately
        return self.enqueue_call(func, args=args, kwargs=kwargs, job_id=job_id, timeout=timeout, result_ttl=result_ttl, **other_kwargs)


class QueueManager:
    """Manages Redis connection and exposes Redis Queue (RQ) queues with sync fallback."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(QueueManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self._queues = {}
        self.redis_available = False
        
        # Check if offline mode is requested
        offline_requested = os.environ.get("OFFLINE_MODE", "false").lower() == "true"
        
        if offline_requested:
            logger.info("Offline mode requested via env. QueueManager will run in synchronous/mock mode.")
            self.redis_conn = None
        else:
            try:
                # Test connection to Redis
                self.redis_conn = redis.from_url(settings.REDIS_URL, socket_connect_timeout=1.0)
                self.redis_conn.ping()
                self.redis_available = True
                logger.info("Successfully connected to Redis.")
            except Exception as e:
                logger.warning(f"Redis connection failed ({e}). Falling back to synchronous/mock mode.")
                self.redis_conn = None
                
        self._initialized = True
        
    def get_queue(self, queue_name: str):
        """Retrieves or creates a named RQ queue or MockQueue."""
        if not self.redis_available:
            if queue_name not in self._queues:
                self._queues[queue_name] = MockQueue(queue_name)
            return self._queues[queue_name]
            
        if queue_name not in self._queues:
            self._queues[queue_name] = Queue(
                name=queue_name,
                connection=self.redis_conn,
                default_timeout=3600
            )
        return self._queues[queue_name]

    def get_redis_connection(self):
        return self.redis_conn

# Singleton instance
queue_manager = QueueManager()
