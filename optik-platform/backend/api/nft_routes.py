from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional
import os

from utils.auth import get_current_user
from utils.database import db
from utils.image_processor import ImageProcessor
from utils.nft_generator import NFTGenerator

router = APIRouter(prefix="/api/v1/nft", tags=["nft"])


@router.post("/prepare")
async def prepare_nft(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    symbol: Optional[str] = Form(None),
    seller_fee_basis_points: int = Form(500),
    image: UploadFile = File(...),
    user=Depends(get_current_user),
):
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")
    if not image:
        raise HTTPException(status_code=400, detail="Image is required")

    pairing_token = os.getenv("OPTIK_PAIRING_TOKEN", "OPTIK")
    symbol = symbol or os.getenv("OPTIK_COLLECTION_SYMBOL", pairing_token)

    content = await image.read()
    if not content:
        raise HTTPException(status_code=400, detail="Image upload failed")

    image_processor = ImageProcessor()
    image_url = await image_processor.upload_file_bytes(
        filename=image.filename or "asset.png",
        content=content,
        content_type=image.content_type or "application/octet-stream",
    )

    attributes = [{"trait_type": "Pairing Token", "value": pairing_token}]
    metadata = NFTGenerator.generate_metadata(
        name=name,
        symbol=symbol,
        description=description or "",
        image_url=image_url,
        attributes=attributes,
        seller_fee_basis_points=seller_fee_basis_points,
        external_url=os.getenv("FRONTEND_URL", ""),
    )
    metadata_url = await image_processor.upload_json(metadata, name)

    asset_id = await db.create_nft_asset(user.id, {
        "name": name,
        "symbol": symbol,
        "description": description,
        "image_url": image_url,
        "metadata_url": metadata_url,
        "seller_fee_basis_points": seller_fee_basis_points,
        "backing_amount": float(os.getenv("OPTIK_BACKING_AMOUNT", "0")),
        "status": "prepared",
    })

    return {
        "asset_id": asset_id,
        "image_url": image_url,
        "metadata_url": metadata_url,
        "pairing_token": pairing_token,
    }
