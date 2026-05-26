import asyncio
from ai.validators.script_validator import ScriptValidator
from db.repositories.manager import db_manager
from sqlalchemy import select
from db.models.script import GeneratedScript
from db.models.validation import ScriptValidation
from shared.logging.logger import log

async def main():
    log.info("🚀 Launching Script Validation Pipeline")
    
    validator = ScriptValidator()
    
    async with db_manager.get_session() as session:
        # 1. Fetch scripts that haven't been validated yet
        # (This is a simplified check for the demo)
        stmt = select(GeneratedScript).limit(5)
        result = await session.execute(stmt)
        scripts = result.scalars().all()
        
        if not scripts:
            log.warning("No scripts found for validation.")
            return

        for script in scripts:
            try:
                # 2. Run Validation
                res = await validator.validate(script.id, script.full_script)
                
                # 3. Store Result
                val_obj = ScriptValidation(
                    script_id=script.id,
                    passed=res.passed,
                    quality_score=res.quality_score,
                    profanity_score=res.profanity_score,
                    duplicate_score=res.duplicate_score,
                    readability_score=res.readability_score,
                    duration_estimate=res.duration_estimate,
                    failures_json=[f.dict() for f in res.failures]
                )
                session.add(val_obj)
                
                log.info(f"✅ Script {script.id} validation complete. Pass: {res.passed} | Score: {res.quality_score:.2f}")
                
            except Exception as e:
                log.error(f"Validation failed for script {script.id}: {e}")
                
        await session.commit()

if __name__ == "__main__":
    asyncio.run(main())
