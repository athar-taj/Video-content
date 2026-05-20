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
            if isinstance(w, dict):
                w_word = w.get("word")
                w_start = w.get("start_time")
                w_end = w.get("end_time")
                w_conf = w.get("confidence")
                w_pos = w.get("position")
            else:
                w_word = w.word
                w_start = w.start_time
                w_end = w.end_time
                w_conf = w.confidence
                w_pos = w.position

            word_model = WordTimestampModel(
                subtitle_generation_id=gen_id,
                word=w_word,
                start_time=w_start,
                end_time=w_end,
                confidence=w_conf,
                position=w_pos
            )
            self.session.add(word_model)
            
        # Store segments
        for s in segments:
            if isinstance(s, dict):
                s_text = s.get("text")
                s_start = s.get("start_time")
                s_end = s.get("end_time")
                s_dur = s.get("duration")
                s_words = s.get("words", [])
            else:
                s_text = s.text
                s_start = s.start_time
                s_end = s.end_time
                s_dur = s.duration
                s_words = s.words

            word_data_dicts = []
            for item in s_words:
                if isinstance(item, dict):
                    word_data_dicts.append(item)
                else:
                    word_data_dicts.append(item.model_dump())

            seg_model = SubtitleSegmentModel(
                subtitle_generation_id=gen_id,
                text=s_text,
                start_time=s_start,
                end_time=s_end,
                duration=s_dur,
                word_data=word_data_dicts
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
