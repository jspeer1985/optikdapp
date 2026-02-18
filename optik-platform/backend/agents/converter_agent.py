import os
import logging
import json
from typing import Dict, Any, List
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)

class Web3ConverterAgent:
    """
    Converts Web2 product data into Web3-ready formats.
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = ChatAnthropic(
            model="claude-3-sonnet-20240229",
            anthropic_api_key=self.api_key,
            temperature=0.2
        ) if self.api_key else None

    async def convert(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Web2 product data to Web3 format.
        """
        title = product_data.get('title')
        desc = product_data.get('description') or ''
        if not title:
            raise ValueError("Product title is required")

        images = product_data.get('images', [])
        if not images:
            raise ValueError(f"Product {title} is missing images")

        try:
            price_usd = float(product_data.get('price') or 0)
        except (ValueError, TypeError):
            raise ValueError(f"Product {title} has invalid price")

        sol_usd = float(os.getenv("SOL_USD_PRICE", "0") or 0)
        if not sol_usd:
            raise ValueError("SOL_USD_PRICE is required to compute SOL pricing")

        price_sol = round(price_usd / sol_usd, 6)
        web3_title = title
        web3_desc = desc.strip()

        logger.info(f"Converted product: {title}")

        return {
            "title": web3_title,
            "description": web3_desc,
            "price_sol": price_sol,
            "price": price_usd,
            "currency": "USD",
            "image": images[0],
            "metadata": {
                "origin": "Optik Converter",
                "original_platform": product_data.get("platform", "unknown")
            }
        }
