import os
from typing import Dict, Any, List, Optional

class NFTGenerator:
    """
    Generates Metaplex-compatible metadata for products.
    """
    
    @staticmethod
    def generate_metadata(
        name: str, 
        symbol: str, 
        description: str, 
        image_url: str, 
        attributes: List[Dict[str, str]],
        seller_fee_basis_points: int = 500,
        creators: Optional[List[Dict[str, Any]]] = None,
        external_url: Optional[str] = None,
        collection: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Creates the JSON structure for a standard SPL-NFT.
        """
        file_type = "image/jpeg"
        ext = os.path.splitext(image_url)[1].lower()
        if ext == ".png":
            file_type = "image/png"
        elif ext == ".gif":
            file_type = "image/gif"
        return {
            "name": name,
            "symbol": symbol,
            "description": description,
            "seller_fee_basis_points": seller_fee_basis_points,
            "image": image_url,
            "attributes": attributes,
            "external_url": external_url,
            "properties": {
                "files": [
                    {
                        "uri": image_url,
                        "type": file_type
                    }
                ],
                "category": "image",
                "creators": creators or [],
            },
            "collection": collection,
        }

    @staticmethod
    def format_attributes(raw_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extracts key features into NFT traits."""
        attributes = []
        if raw_data.get("vendor"):
            attributes.append({"trait_type": "Vendor", "value": raw_data["vendor"]})
        if raw_data.get("type"):
            attributes.append({"trait_type": "Category", "value": raw_data["type"]})
        return attributes
