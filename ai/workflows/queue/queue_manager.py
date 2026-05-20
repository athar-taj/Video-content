import redis
from rq import Queue
from shared.config.settings import settings
from ai.workflows.queue.models import JobPriority

class QueueManager:
    """Manages Redis connection and exposes Redis Queue (RQ) queues."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(QueueManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        # Parse connection options or use directly
        self.redis_conn = redis.from_url(settings.REDIS_URL)
        self._queues = {}
        self._initialized = True
        
    def get_queue(self, queue_name: str) -> Queue:
        """Retrieves or creates a named RQ queue."""
        if queue_name not in self._queues:
            # We map queue names to Redis Queues
            self._queues[queue_name] = Queue(
                name=queue_name,
                connection=self.redis_conn,
                default_timeout=3600  # Default timeout 1 hour
            )
        return self._queues[queue_name]

    def get_redis_connection(self) -> redis.Redis:
        return self.redis_conn

# Singleton instance
queue_manager = QueueManager()
