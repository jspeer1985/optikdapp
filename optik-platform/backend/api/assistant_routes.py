import os
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/assistant", tags=["assistant"])


@router.get("/models")
async def list_models():
    provider = os.getenv("OPTIK_ASSISTANT_PROVIDER", "anthropic")
    fast = os.getenv("OPTIK_ASSISTANT_MODEL_FAST", "claude-3-haiku-20240307")
    accurate = os.getenv("OPTIK_ASSISTANT_MODEL_ACCURATE", "claude-3-sonnet-20240229")
    mode = os.getenv("OPTIK_ASSISTANT_MODE", "balanced")

    return {
        "provider": provider,
        "default_mode": mode,
        "modes": [
            {"id": "fast", "label": "Fast", "model": fast},
            {"id": "balanced", "label": "Balanced", "model": accurate},
            {"id": "accurate", "label": "Accurate", "model": accurate},
        ],
    }
