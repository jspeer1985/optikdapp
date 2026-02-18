from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Dict
from pydantic import BaseModel
from datetime import datetime
from utils.auth import get_current_user, User
from utils.database import db

router = APIRouter(prefix="/api/v1/products", tags=["products"])

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    supply: str
    price: str
    status: str = "Live"

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    supply: Optional[str] = None
    price: Optional[str] = None
    status: Optional[str] = None

class Product(ProductBase):
    id: str
    user_id: str
    sold: int
    created_at: datetime
    updated_at: datetime

@router.get("/")
async def list_products(user: User = Depends(get_current_user)):
    products = await db.get_products(user.id)
    return products

@router.post("/")
async def create_product(product: ProductCreate, user: User = Depends(get_current_user)):
    data = product.dict()
    data["user_id"] = user.id
    product_id = await db.create_product(data)
    return {**data, "id": product_id, "sold": 0, "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()}

@router.put("/{product_id}")
async def update_product(product_id: str, updates: ProductUpdate, user: User = Depends(get_current_user)):
    data = {k: v for k, v in updates.dict().items() if v is not None}
    if not data:
        raise HTTPException(status_code=400, detail="No updates provided")
    await db.update_product(product_id, user.id, data)
    return {"message": "Product updated"}

@router.delete("/{product_id}")
async def delete_product(product_id: str, user: User = Depends(get_current_user)):
    await db.delete_product(product_id, user.id)
    return {"message": "Product deleted"}
