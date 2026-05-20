import asyncio
from ai.voice.generation.tts_service import TTSService
from db.repositories.manager import db_manager
from sqlalchemy import select
from db.models.script import GeneratedScript
from db.models.audio import GeneratedAudio
from shared.logging.logger import log

async def main():
    log.info("🚀 Launching TTS Generation Pipeline")
    
    tts_service = TTSService()
    
    async for session in db_manager.get_session():
        # 1. Fetch scripts that are ready for voice generation
        # (This usually follows validation, but we'll fetch recently generated ones)
        stmt = select(GeneratedScript).limit(1)
        result = await session.execute(stmt)
        scripts = result.scalars().all()
        
        if not scripts:
            log.warning("No scripts found for voice generation.")
            return

        for script in scripts:
            try:
                # 2. Generate Narration
                log.info(f"Generating voice for Script {script.id}...")
                res = await tts_service.generate_narration(script.full_script)
                
                # 3. Store Metadata
                audio_obj = GeneratedAudio(
                    script_id=script.id,
                    provider=res.provider,
                    voice_name=res.voice,
                    audio_path=res.audio_path,
                    duration_seconds=res.duration_sec,
                    file_size_bytes=res.file_size_bytes
                )
                session.add(audio_obj)
                
                log.info(f"✅ Audio generated: {res.audio_path}")
                
            except Exception as e:
                log.error(f"TTS generation failed for script {script.id}: {e}")
                
        await session.commit()

if __name__ == "__main__":
    asyncio.run(main())
