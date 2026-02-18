import os
import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class ImageProcessor:
    """
    Handles image processing and IPFS uploads via Pinata.
    """
    
    def __init__(self, api_key: Optional[str] = None, secret_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("PINATA_API_KEY")
        self.secret_key = secret_key or os.getenv("PINATA_SECRET_KEY")
        self.base_url = "https://api.pinata.cloud"

    async def upload_to_ipfs(self, image_url: str) -> Optional[str]:
        """
        Downloads an image from a URL and uploads it to Pinata IPFS.
        Returns the IPFS gateway URL.
        """
        if not self.api_key or not self.secret_key:
            raise RuntimeError("Pinata credentials are required for IPFS uploads")

        try:
            async with httpx.AsyncClient() as client:
                # 1. Download image
                img_response = await client.get(image_url)
                if img_response.status_code != 200:
                    raise RuntimeError(f"Failed to download image: {img_response.status_code}")
                
                # 2. Upload to Pinata
                headers = {
                    "pinata_api_key": self.api_key,
                    "pinata_secret_api_key": self.secret_key
                }
                
                files = {
                    'file': ('image.jpg', img_response.content, 'image/jpeg')
                }
                
                pin_response = await client.post(
                    f"{self.base_url}/pinning/pinFileToIPFS",
                    headers=headers,
                    files=files
                )
                
                if pin_response.status_code == 200:
                    cid = pin_response.json().get("IpfsHash")
                    return f"https://gateway.pinata.cloud/ipfs/{cid}"
                else:
                    raise RuntimeError(f"Pinata upload failed: {pin_response.text}")

        except Exception as e:
            logger.error(f"Image processing error for {image_url}: {e}")
            raise

    async def upload_file_bytes(self, filename: str, content: bytes, content_type: str) -> str:
        if not self.api_key or not self.secret_key:
            raise RuntimeError("Pinata credentials are required for IPFS uploads")

        headers = {
            "pinata_api_key": self.api_key,
            "pinata_secret_api_key": self.secret_key,
        }
        files = {
            "file": (filename, content, content_type)
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/pinning/pinFileToIPFS",
                headers=headers,
                files=files,
            )
            if response.status_code != 200:
                raise RuntimeError(f"Pinata upload failed: {response.text}")
            cid = response.json().get("IpfsHash")
            return f"https://gateway.pinata.cloud/ipfs/{cid}"

    async def upload_json(self, payload: dict, name: str) -> str:
        if not self.api_key or not self.secret_key:
            raise RuntimeError("Pinata credentials are required for IPFS uploads")

        headers = {
            "pinata_api_key": self.api_key,
            "pinata_secret_api_key": self.secret_key,
        }
        json_payload = {
            "pinataMetadata": {"name": name},
            "pinataContent": payload,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/pinning/pinJSONToIPFS",
                headers=headers,
                json=json_payload,
            )
            if response.status_code != 200:
                raise RuntimeError(f"Pinata JSON upload failed: {response.text}")
            cid = response.json().get("IpfsHash")
            return f"https://gateway.pinata.cloud/ipfs/{cid}"
