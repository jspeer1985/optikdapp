import httpx
import logging
import json
import hmac
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ShopifyIntegration:
    """
    Complete Shopify integration for product extraction, webhook management,
    and store synchronization with the Optik platform
    """
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None, access_token: Optional[str] = None, store_domain: Optional[str] = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.store_domain = store_domain
        self.base_url = f"https://{store_domain}.myshopify.com/admin/api/2023-10" if store_domain else None

    async def extract_products(self, store_url: str, limit: int = 250) -> Dict[str, Any]:
        """
        Extract products from Shopify store with fallback methods
        
        Args:
            store_url: Shopify store URL
            limit: Maximum number of products to fetch
            
        Returns:
            Dict with products and metadata
        """
        try:
            # If we have API access, use Admin API
            if self.access_token and self.base_url:
                return await self._fetch_via_admin_api(limit)
            else:
                # Fallback to storefront scraping
                return await self._scrape_storefront(store_url)
                
        except Exception as e:
            logger.error(f"Shopify extraction failed: {e}")
            return {"error": str(e)}

    async def _fetch_via_admin_api(self, limit: int) -> Dict[str, Any]:
        """Fetch products using Shopify Admin API"""
        if not self.base_url or not self.access_token:
            raise ValueError("Missing Shopify API credentials")
        
        headers = {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json"
        }
        
        products = []
        page_info = None
        
        async with httpx.AsyncClient() as client:
            while len(products) < limit:
                url = f"{self.base_url}/products.json"
                params = {"limit": min(250, limit - len(products))}
                
                if page_info:
                    params["page_info"] = page_info
                
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                batch_products = data.get("products", [])
                
                if not batch_products:
                    break
                
                products.extend([self.format_for_web3(p) for p in batch_products])
                
                # Check for pagination
                link_header = response.headers.get("Link", "")
                if 'rel="next"' not in link_header:
                    break
                    
                # Extract next page info
                for link in link_header.split(","):
                    if 'rel="next"' in link:
                        page_info = link.split("page_info=")[1].split(">")[0]
                        break
        
        return {
            "products": products[:limit],
            "count": len(products),
            "source": "shopify_admin_api",
            "extracted_at": datetime.utcnow().isoformat()
        }

    async def _scrape_storefront(self, store_url: str) -> Dict[str, Any]:
        """Scrape products from Shopify storefront"""
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # Get products via JSON endpoint
            products_url = f"{store_url.rstrip('/')}/products.json"
            products_response = await client.get(products_url)
            
            if products_response.status_code == 200:
                products_data = products_response.json()
                products = [self.format_for_web3(p) for p in products_data.get("products", [])]
            else:
                products = []
            
            return {
                "products": products,
                "count": len(products),
                "source": "shopify_storefront_scraping",
                "extracted_at": datetime.utcnow().isoformat()
            }

    async def fetch_all_products(self, store_url: str) -> List[Dict[str, Any]]:
        """
        Legacy method - fetches products using the public .json endpoint.
        """
        endpoint = f"{store_url.rstrip('/')}/products.json"
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                response = await client.get(endpoint, timeout=20.0)
                if response.status_code == 200:
                    return response.json().get("products", [])
                else:
                    logger.error(f"Failed to fetch products from {endpoint}: {response.status_code}")
                    return []
            except Exception as e:
                logger.error(f"Shopify integration error for {store_url}: {e}")
                return []

    def format_for_web3(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced Shopify product formatting for the internal pipeline.
        """
        variants = product.get("variants", [])
        primary_variant = variants[0] if variants else {}
        
        return {
            "external_id": str(product.get("id")),
            "title": product.get("title"),
            "description": product.get("body_html"),
            "price": float(primary_variant.get("price", 0)),
            "currency": primary_variant.get("presentment_prices", [{}])[0].get("price", {}).get("currency_code", "USD") if primary_variant.get("presentment_prices") else "USD",
            "images": [img.get("src") for img in product.get("images", [])],
            "sku": primary_variant.get("sku"),
            "variants": [
                {
                    "id": v.get("id"),
                    "title": v.get("title"),
                    "price": float(v.get("price", 0)),
                    "sku": v.get("sku"),
                    "inventory_quantity": v.get("inventory_quantity"),
                    "available": v.get("available", True)
                } for v in variants
            ],
            "tags": product.get("tags", "").split(", ") if product.get("tags") else [],
            "product_type": product.get("product_type"),
            "vendor": product.get("vendor"),
            "handle": product.get("handle"),
            "created_at": product.get("created_at"),
            "updated_at": product.get("updated_at"),
            "raw": product
        }

    async def setup_webhooks(self, webhook_url: str) -> Dict[str, Any]:
        """Setup Shopify webhooks for real-time sync"""
        if not self.base_url or not self.access_token:
            raise ValueError("Missing Shopify API credentials")
        
        webhooks = [
            {
                "topic": "products/create",
                "address": webhook_url,
                "format": "json"
            },
            {
                "topic": "products/update", 
                "address": webhook_url,
                "format": "json"
            },
            {
                "topic": "products/delete",
                "address": webhook_url,
                "format": "json"
            }
        ]
        
        headers = {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json"
        }
        
        created_webhooks = []
        
        async with httpx.AsyncClient() as client:
            for webhook in webhooks:
                response = await client.post(
                    f"{self.base_url}/webhooks.json",
                    headers=headers,
                    json={"webhook": webhook}
                )
                
                if response.status_code == 201:
                    created_webhooks.append(response.json())
                else:
                    logger.warning(f"Failed to create webhook {webhook['topic']}: {response.text}")
        
        return {
            "created_webhooks": created_webhooks,
            "count": len(created_webhooks)
        }

    def verify_webhook(self, payload: str, hmac_header: str) -> bool:
        """Verify Shopify webhook signature"""
        if not self.api_secret:
            return False
        
        calculated_hmac = hmac.new(
            self.api_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).digest()
        
        return hmac.compare_digest(
            calculated_hmac.hexdigest(),
            hmac_header
        )

    async def get_store_info(self) -> Dict[str, Any]:
        """Get Shopify store information"""
        if not self.base_url or not self.access_token:
            raise ValueError("Missing Shopify API credentials")
        
        headers = {"X-Shopify-Access-Token": self.access_token}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/shop.json", headers=headers)
            response.raise_for_status()
            
            shop_data = response.json().get("shop", {})
            
            return {
                "name": shop_data.get("name"),
                "domain": shop_data.get("domain"),
                "email": shop_data.get("email"),
                "currency": shop_data.get("currency"),
                "timezone": shop_data.get("iana_timezone"),
                "created_at": shop_data.get("created_at")
            }
