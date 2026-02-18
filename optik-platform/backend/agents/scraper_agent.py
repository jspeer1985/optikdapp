import asyncio
import json
import os
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

class ShopifyScraperAgent(BaseScraper):
    """
    Scraper specialized for Shopify stores.
    """
    async def preview_store(self, url: str, limit: int = 5) -> Dict[str, Any]:
        """Preview store data for frontend visualization."""
        async with httpx.AsyncClient(headers=self.headers, follow_redirects=True, timeout=15.0) as client:
            products = await self.scrape_products(url, client)
            return {
                "store_info": {"name": url.split("//")[-1].split(".")[0], "platform": "shopify"},
                "products": products[:limit],
                "total_products": len(products)
            }

    async def scrape_products(self, url: str, client: httpx.AsyncClient) -> List[Dict[str, Any]]:
        products_url = f"{url.rstrip('/')}/products.json"
        response = await client.get(products_url)
        if response.status_code != 200:
            raise RuntimeError(f"Shopify scrape failed: {response.status_code}")
        data = response.json()
        products = data.get('products', [])
        if not products:
            raise RuntimeError("Shopify scrape returned no products")
        return [{
            "id": p.get('id'),
            "title": p.get('title'),
            "description": p.get('body_html'),
            "price": p.get('variants', [{}])[0].get('price'),
            "images": [img.get('src') for img in p.get('images', [])]
        } for p in products]

class WooCommerceScraperAgent(BaseScraper):
    """
    Scraper specialized for WooCommerce stores.
    """
    async def preview_store(self, url: str, limit: int = 5) -> Dict[str, Any]:
        async with httpx.AsyncClient(headers=self.headers, follow_redirects=True, timeout=15.0) as client:
            products = await self.scrape_products(url, client)
            return {
                "store_info": {"name": url.split("//")[-1].split(".")[0], "platform": "woocommerce"},
                "products": products[:limit],
                "total_products": len(products)
            }

    async def scrape_products(self, url: str, client: httpx.AsyncClient, api_key: Optional[str] = None, api_secret: Optional[str] = None) -> List[Dict[str, Any]]:
        api_key = api_key or os.getenv("WOOCOMMERCE_CONSUMER_KEY")
        api_secret = api_secret or os.getenv("WOOCOMMERCE_CONSUMER_SECRET")
        if not api_key or not api_secret:
            raise RuntimeError("WooCommerce API credentials are required")

        products = []
        page = 1
        while True:
            response = await client.get(
                f"{url.rstrip('/')}/wp-json/wc/v3/products",
                params={"consumer_key": api_key, "consumer_secret": api_secret, "per_page": 100, "page": page},
            )
            if response.status_code != 200:
                raise RuntimeError(f"WooCommerce scrape failed: {response.status_code}")
            data = response.json()
            if not data:
                break
            for p in data:
                products.append({
                    "id": p.get("id"),
                    "title": p.get("name"),
                    "description": p.get("description"),
                    "price": p.get("price"),
                    "images": [img.get("src") for img in p.get("images", [])],
                })
            page += 1

        if not products:
            raise RuntimeError("WooCommerce scrape returned no products")
        return products
