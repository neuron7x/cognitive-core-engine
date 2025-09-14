import asyncio
from sqlalchemy.orm import Session
from cognitive_core.storage.models import Episode

async def run_replay(db: Session, topk: int = 200):
    episodes = db.query(Episode).order_by(Episode.surprise.desc()).limit(topk).all()
    for ep in episodes:
        _ = ep.payload_json
        await asyncio.sleep(0)
