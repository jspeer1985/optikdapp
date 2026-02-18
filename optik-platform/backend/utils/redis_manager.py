import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import redis.asyncio as redis_async
except Exception:
    redis_async = None


class RedisManager:
    """
    Manages job states and real-time progress using Redis.
    """

    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.client = None
        self.redis_enabled = False

    async def connect(self):
        redis_url = os.getenv("REDIS_URL")
        if redis_url and redis_async:
            self.client = redis_async.from_url(redis_url, decode_responses=True)
            self.redis_enabled = True
            logger.info("Redis connection initialized")
        else:
            logger.info("Redis not configured; using in-memory job store")

    async def disconnect(self):
        if self.client:
            await self.client.close()
        logger.info("Redis disconnected")

    async def ping(self) -> bool:
        if self.redis_enabled and self.client:
            try:
                await self.client.ping()
                return True
            except Exception:
                return False
        return True

    async def set_job_status(self, job_id: str, status_data: Dict[str, Any]):
        status_data = dict(status_data)
        if self.redis_enabled and self.client:
            status_data.setdefault("created_at", datetime.utcnow().isoformat())
            status_data["updated_at"] = datetime.utcnow().isoformat()
            status_data["job_id"] = job_id
            await self.client.hset(f"job:{job_id}", mapping=status_data)
            return

        if job_id in self.jobs:
            status_data["created_at"] = self.jobs[job_id].get("created_at", datetime.utcnow())
        else:
            status_data["created_at"] = datetime.utcnow()

        status_data["updated_at"] = datetime.utcnow()
        status_data["job_id"] = job_id
        self.jobs[job_id] = status_data
        logger.info(f"Job {job_id} updated to {status_data.get('status')}")

    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        if self.redis_enabled and self.client:
            data = await self.client.hgetall(f"job:{job_id}")
            return data or None

        job_data = self.jobs.get(job_id)
        if job_data:
            return dict(job_data)
        return None

    async def get_active_job_count(self) -> int:
        if self.redis_enabled and self.client:
            keys = await self.client.keys("job:*")
            count = 0
            for key in keys:
                status = await self.client.hget(key, "status")
                if status not in ["completed", "failed", "deployed"]:
                    count += 1
            return count

        return len([j for j in self.jobs.values() if j.get("status") not in ["completed", "failed", "deployed"]])

    async def cancel_job(self, job_id: str):
        if self.redis_enabled and self.client:
            await self.client.hset(f"job:{job_id}", mapping={"status": "cancelled", "updated_at": datetime.utcnow().isoformat()})
            return

        if job_id in self.jobs:
            self.jobs[job_id]["status"] = "cancelled"


redis = RedisManager()
