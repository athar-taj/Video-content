from sqlalchemy.ext.asyncio import AsyncSession
from db.models.database import Topic, Script, WorkflowJob
from datetime import datetime

class ContentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_topic(self, title: str, content: str = "") -> Topic:
        topic = Topic(title=title, content=content)
        self.session.add(topic)
        await self.session.flush()
        return topic

    async def save_script(self, topic_id: int, hook: str, script: str, provider: str) -> Script:
        new_script = Script(
            topic_id=topic_id,
            hook=hook,
            script=script,
            provider_used=provider
        )
        self.session.add(new_script)
        await self.session.flush()
        return new_script

    async def log_job(self, workflow_type: str, status: str, errors: str = None) -> WorkflowJob:
        job = WorkflowJob(
            workflow_type=workflow_type,
            status=status,
            errors=errors,
            completed_at=datetime.utcnow() if status in ["completed", "failed"] else None
        )
        self.session.add(job)
        await self.session.flush()
        return job
