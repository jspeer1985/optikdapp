import logging
import httpx
import json
from typing import Dict, Any, List, Optional
from agents.scraper_agent import ShopifyScraperAgent, WooCommerceScraperAgent, BaseScraper
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

class MetaScraperAgent(BaseScraper):
    """
    The 'Universal' fallback. Uses HTML parsing and JSON-LD extraction 
    to support non-standard e-commerce platforms (Magento, BigCommerce, Custom).
    """
    async def scrape_products(self, url: str, client: httpx.AsyncClient) -> List[Dict[str, Any]]:
        logger.info(f"Using MetaScraper for {url}")
        try:
            response = await client.get(url)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            products = []
            
            # Strategy 1: Look for JSON-LD (Schema.org Product)
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    # Handle both single objects and lists
                    items = data if isinstance(data, list) else [data]
                    for item in items:
                        if item.get('@type') == 'Product' or 'Product' in item.get('@type', []):
                            products.append(self._normalize_schema_product(item))
                except:
                    continue
            
            # Strategy 2: Heuristic HTML Scraping (Fallback)
            if not products:
                # Look for common product containers
                # This is a simplified version for the demo/agent
                pass
                
            return products
        except Exception as e:
            logger.error(f"MetaScraper failed: {e}")
            return []

    def _normalize_schema_product(self, item: Dict) -> Dict:
        """Normalizes Schema.org Product data to Optik standard."""
        offers = item.get('offers', {})
        if isinstance(offers, list):
            offers = offers[0]
        
        return {
            "external_id": str(item.get('sku', item.get('name'))),
            "title": item.get('name'),
            "description": item.get('description'),
            "price": offers.get('price'),
            "currency": offers.get('priceCurrency', 'USD'),
            "images": [item.get('image')] if isinstance(item.get('image'), str) else item.get('image', []),
            "sku": item.get('sku'),
            "variants": [] # MetaScraper typically gets the primary variant
        }

class UniversalIngestionManager:
    """
    Point 1 Fix: The DApp Conversion Engine's Ingestion Layer.
    Orchestrates data extraction across Shopify, Woo, and Generic platforms.
    """
    def __init__(self):
        self.shopify = ShopifyScraperAgent()
        self.woo = WooCommerceScraperAgent()
        self.meta = MetaScraperAgent()

    async def ingest(self, url: str, platform: Optional[str] = None) -> Dict[str, Any]:
        """
        Main entry point for 'Incorporating All Platforms'.
        Detects platform and routes to the best-fit adapter.
        """
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            # 1. Platform Detection
            detected_platform = platform or await self._detect_platform(url, client)
            logger.info(f"Targeting platform: {detected_platform}")

            # 2. Scrape with Adapter
            if detected_platform == "shopify":
                products = await self.shopify.scrape_products(url, client)
            elif detected_platform == "woocommerce":
                products = await self.woo.scrape_products(url, client)
            else:
                products = await self.meta.scrape_products(url, client)

            # 3. Data Fidelity Check (Point 1 requirement)
            valid_products = [p for p in products if p.get('title') and p.get('price')]
            
            return {
                "url": url,
                "platform": detected_platform,
                "fidelity_score": self._calculate_fidelity(products),
                "products": valid_products,
                "count": len(valid_products),
                "sys_code": "INGEST_SYNC_COMPLETE"
            }

    async def _detect_platform(self, url: str, client: httpx.AsyncClient) -> str:
        try:
            response = await client.get(url)
            text = response.text.lower()
            if "shopify" in text or "cdn.shopify.com" in text:
                return "shopify"
            if "wp-content/plugins/woocommerce" in text:
                return "woocommerce"
            return "generic"
        except:
            return "generic"

    def _calculate_fidelity(self, products: List) -> float:
        if not products: return 0.0
        # Check if products have critical data (Price, SKUs, Images)
        total_p = len(products)
        with_price = len([p for p in products if p.get('price')])
        with_images = len([p for p in products if p.get('images')])
        return ((with_price / total_p) + (with_images / total_p)) / 2.0
