from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Optional, Dict
from pydantic import BaseModel
from datetime import datetime
from utils.auth import get_current_user, User
from utils.database import db

router = APIRouter(prefix="/api/v1/integrations", tags=["integrations"])

class IntegrationBase(BaseModel):
    name: str
    detail: str
    status: str = "Available"
    icon: str

class IntegrationCreate(IntegrationBase):
    pass

class IntegrationUpdate(BaseModel):
    status: str

@router.get("/")
async def list_integrations(user: User = Depends(get_current_user)):
    integrations = await db.get_integrations(user.id)
    return integrations

@router.post("/", include_in_schema=False)
async def create_integration(integration: IntegrationCreate, user: User = Depends(get_current_user)):
    # This might be for future expansion, currently seeded
    pass

@router.post("/{integration_id}/connect")
async def connect_integration(integration_id: str, user: User = Depends(get_current_user)):
    # In real app: Redirect to OAuth
    await db.update_integration(integration_id, user.id, {"status": "Connected"})
    return {"message": "Integration connected", "status": "Connected"}

@router.post("/{integration_id}/disconnect")
async def disconnect_integration(integration_id: str, user: User = Depends(get_current_user)):
    await db.update_integration(integration_id, user.id, {"status": "Available"})
    return {"message": "Integration disconnected", "status": "Available"}
