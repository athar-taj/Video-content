import logging
import pickle
from typing import Any, AsyncIterator, Optional, Sequence, Iterator
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
    ChannelVersions
)
from shared.redis.client import redis_manager

logger = logging.getLogger(__name__)

class RedisCheckpointSaver(BaseCheckpointSaver):
    """A custom LangGraph checkpoint saver backed by Redis."""
    
    def put(self, config: RunnableConfig, checkpoint: Checkpoint, metadata: CheckpointMetadata, new_versions: ChannelVersions) -> RunnableConfig:
        logger.warning("Synchronous put called on RedisCheckpointSaver. Prefer async version.")
        return config

    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        logger.warning("Synchronous get_tuple called on RedisCheckpointSaver. Prefer async version.")
        return None

    def list(self, config: Optional[RunnableConfig], *, filter: Optional[dict] = None, before: Optional[RunnableConfig] = None, limit: Optional[int] = None) -> Iterator[CheckpointTuple]:
        return iter([])

    async def aget_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = config["configurable"].get("checkpoint_id")
        
        # Connect to Redis
        await redis_manager.connect()
        
        if checkpoint_id:
            key = f"checkpoint:{thread_id}:{checkpoint_ns}:{checkpoint_id}"
        else:
            # Retrieve latest checkpoint ID
            latest_id = await redis_manager.client.get(f"checkpoint:latest:{thread_id}:{checkpoint_ns}")
            if not latest_id:
                return None
            key = f"checkpoint:{thread_id}:{checkpoint_ns}:{latest_id.decode()}"
            
        data = await redis_manager.client.get(key)
        if not data:
            return None
            
        checkpoint_dict = pickle.loads(data)
        
        # Format parent config
        parent_config = checkpoint_dict.get("parent_config")
        
        return CheckpointTuple(
            config=config,
            checkpoint=checkpoint_dict["checkpoint"],
            metadata=checkpoint_dict["metadata"],
            parent_config=parent_config
        )

    async def aput(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = checkpoint["id"]
        
        await redis_manager.connect()
        
        key = f"checkpoint:{thread_id}:{checkpoint_ns}:{checkpoint_id}"
        
        parent_checkpoint_id = checkpoint.get("parent_checkpoint_id")
        parent_config = None
        if parent_checkpoint_id:
            parent_config = config.copy()
            parent_config["configurable"] = config["configurable"].copy()
            parent_config["configurable"]["checkpoint_id"] = parent_checkpoint_id
            
        checkpoint_dict = {
            "checkpoint": checkpoint,
            "metadata": metadata,
            "parent_config": parent_config
        }
        
        # Save in Redis with 1 day expiration to save memory
        serialized_data = pickle.dumps(checkpoint_dict)
        await redis_manager.client.setex(key, 86400, serialized_data)
        
        # Save latest pointer
        await redis_manager.client.setex(f"checkpoint:latest:{thread_id}:{checkpoint_ns}", 86400, checkpoint_id)
        
        logger.info(f"Saved LangGraph checkpoint in Redis: {key}")
        
        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": checkpoint_id
            }
        }

    async def aput_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = config["configurable"]["checkpoint_id"]
        
        await redis_manager.connect()
        key = f"writes:{thread_id}:{checkpoint_ns}:{checkpoint_id}:{task_id}"
        
        # Save write operations
        serialized_writes = pickle.dumps(writes)
        await redis_manager.client.setex(key, 86400, serialized_writes)
