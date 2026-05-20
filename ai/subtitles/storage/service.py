import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models.subtitles import SubtitleGeneration, WordTimestampModel, SubtitleSegmentModel, SubtitleStatus
from ai.subtitles.timestamps.models import WordTimestamp, SubtitleSegment

class SubtitleStorageService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_generation(self, script_id: Optional[int] = None, audio_id: Optional[str] = None) -> str:
        gen_id = str(uuid.uuid4())
        gen = SubtitleGeneration(
            id=gen_id,
            script_id=script_id,
            audio_generation_id=audio_id,
            status=SubtitleStatus.PENDING
        )
        self.session.add(gen)
        await self.session.commit()
        return gen_id

    async def store_timestamps(self, gen_id: str, words: List[WordTimestamp], segments: List[SubtitleSegment]):
        # Update status
        result = await self.session.execute(select(SubtitleGeneration).where(SubtitleGeneration.id == gen_id))
        gen = result.scalar_one_or_none()
        if not gen:
            raise ValueError(f"Generation {gen_id} not found")
        
        gen.status = SubtitleStatus.COMPLETED
        
        # Store words
        for w in words:
            word_model = WordTimestampModel(
                subtitle_generation_id=gen_id,
                word=w.word,
                start_time=w.start_time,
                end_time=w.end_time,
                confidence=w.confidence,
                position=w.position
            )
            self.session.add(word_model)
            
        # Store segments
        for s in segments:
            seg_model = SubtitleSegmentModel(
                subtitle_generation_id=gen_id,
                text=s.text,
                start_time=s.start_time,
                end_time=s.end_time,
                duration=s.duration,
                word_data=[w.model_dump() for w in s.words]
            )
            self.session.add(seg_model)
            
        await self.session.commit()

    async def get_generation_results(self, gen_id: str):
        result = await self.session.execute(
            select(SubtitleGeneration).where(SubtitleGeneration.id == gen_id)
        )
        gen = result.scalar_one_or_none()
        if not gen:
            return None
            
        return {
            "id": gen.id,
            "status": gen.status,
            "segments": [
                {
                    "text": s.text,
                    "start": s.start_time,
                    "end": s.end_time,
                    "words": s.word_data
                } for s in gen.segments
            ]
        }
