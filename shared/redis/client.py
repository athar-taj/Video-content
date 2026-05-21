import redis.asyncio as redis
from shared.config.settings import settings
from shared.logging.logger import log

class RedisManager:
    def __init__(self):
        self.client: redis.Redis = None
        self.enabled = True

    async def connect(self):
        if not self.enabled:
            return
        if not self.client:
            log.info(f"Connecting to Redis at {settings.REDIS_URL}")
            try:
                self.client = redis.from_url(
                    settings.REDIS_URL, 
                    encoding="utf-8", 
                    decode_responses=True,
                    socket_timeout=1.0,
                    socket_connect_timeout=1.0
                )
                await self.client.ping()
            except Exception as e:
                log.warning(f"Failed to connect to Redis: {e}. Redis caching will be bypassed.")
                self.client = None
                self.enabled = False

    async def disconnect(self):
        if self.client:
            try:
                await self.client.close()
            except Exception:
                pass
            self.client = None
            log.info("Disconnected from Redis")

    async def set_cache(self, key: str, value: str, expire: int = 3600):
        if not self.client or not self.enabled:
            return
        try:
            await self.client.set(key, value, ex=expire)
        except Exception as e:
            log.warning(f"Redis set_cache failed: {e}")

    async def get_cache(self, key: str) -> str:
        if not self.client or not self.enabled:
            return None
        try:
            return await self.client.get(key)
        except Exception as e:
            log.warning(f"Redis get_cache failed: {e}")
            return None

redis_manager = RedisManager()
