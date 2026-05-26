import aio_pika
import logging
from shared.config.settings import settings

logger = logging.getLogger(__name__)

class RabbitMQManager:
    """Manages robust async connections, channels, and exchange/queue topology declarations for RabbitMQ using aio-pika."""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RabbitMQManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.connection = None
        self.channel = None
        self.exchange = None
        self.dlx = None
        self.dlq = None
        self.general_queue = None
        self.render_queue = None
        self.analytics_queue = None
        self._initialized = True

    async def connect(self):
        """Establishes robust connection and channel to RabbitMQ."""
        if self.connection and not self.connection.is_closed:
            return

        logger.info(f"Connecting to RabbitMQ at {settings.RABBITMQ_URL}...")
        try:
            self.connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            self.channel = await self.connection.channel()
            logger.info("Connected to RabbitMQ successfully.")
            await self.declare_topology()
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise e

    async def declare_topology(self):
        """Declares direct exchanges, queues, and Dead Letter Exchange bindings."""
        if not self.channel:
            raise RuntimeError("Cannot declare topology without an open channel. Call connect() first.")

        # 1. Declare Main Exchange
        self.exchange = await self.channel.declare_exchange(
            "zem_exchange", aio_pika.ExchangeType.DIRECT, durable=True
        )

        # 2. Declare Dead Letter Exchange (DLX) & Dead Letter Queue (DLQ)
        self.dlx = await self.channel.declare_exchange(
            "zem_dlx", aio_pika.ExchangeType.DIRECT, durable=True
        )
        self.dlq = await self.channel.declare_queue(
            "dead_letter_queue", durable=True
        )
        await self.dlq.bind(self.dlx, routing_key="dead_letter")

        # 3. Declare capability-driven standard queues bound to DLX parameters
        # x-dead-letter-exchange routes rejected or failed messages to DLX
        queue_args = {
            "x-dead-letter-exchange": "zem_dlx",
            "x-dead-letter-routing-key": "dead_letter"
        }

        self.general_queue = await self.channel.declare_queue(
            "general_queue", durable=True, arguments=queue_args
        )
        await self.general_queue.bind(self.exchange, routing_key="general")

        self.render_queue = await self.channel.declare_queue(
            "render_queue", durable=True, arguments=queue_args
        )
        await self.render_queue.bind(self.exchange, routing_key="render")

        self.analytics_queue = await self.channel.declare_queue(
            "analytics_queue", durable=True, arguments=queue_args
        )
        await self.analytics_queue.bind(self.exchange, routing_key="analytics")

        logger.info("RabbitMQ topology declared successfully (queues, bindings, and DLX configured).")

    async def close(self):
        """Closes the connection and channel."""
        if self.channel:
            await self.channel.close()
            self.channel = None
        if self.connection:
            await self.connection.close()
            self.connection = None
        logger.info("Closed RabbitMQ connection.")

# Singleton instance
rabbitmq_manager = RabbitMQManager()
