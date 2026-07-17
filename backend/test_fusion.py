import asyncio
from app.orchestrator.participant_fusion import ParticipantFusionEngine
from app.database import AsyncSessionLocal

async def run():
    async with AsyncSessionLocal() as db:
        engine = ParticipantFusionEngine(db)
        res = await engine.fuse_participants(1)
        print('RESULT:', res)

asyncio.run(run())
