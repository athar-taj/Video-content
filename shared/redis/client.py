import redis.asyncio as redis
from shared.config.settings import settings
from shared.logging.logger import log

class RedisManager:
    def __init__(self):
        self.client: redis.Redis = None

    async def connect(self):
        if not self.client:
            log.info(f"Connecting to Redis at {settings.REDIS_URL}")
            self.client = redis.from_url(
                settings.REDIS_URL, 
                encoding="utf-8", 
                decode_responses=True
            )

    async def disconnect(self):
        if self.client:
            await self.client.close()
            log.info("Disconnected from Redis")

    async def set_cache(self, key: str, value: str, expire: int = 3600):
        await self.client.set(key, value, ex=expire)

    async def get_cache(self, key: str) -> str:
        return await self.client.get(key)

redis_manager = RedisManager()
