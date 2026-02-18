import httpx
import logging
import base64
import json
import hmac
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class WooCommerceIntegration:
    """
    Complete WooCommerce integration for product extraction, webhook management,
    and store synchronization with the Optik platform
    """
    
    def __init__(self, consumer_key: Optional[str] = None, consumer_secret: Optional[str] = None, site_url: Optional[str] = None):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.site_url = site_url
        self.api_base = f"{site_url.rstrip('/')}/wp-json/wc/v3" if site_url else None

    async def extract_products(self, site_url: str, limit: int = 100) -> Dict[str, Any]:
        """
        Extract products from WooCommerce store with fallback methods
        
        Args:
            site_url: WooCommerce site URL
            limit: Maximum number of products to fetch
            
        Returns:
            Dict with products and metadata
        """
        try:
            # If we have API credentials, use REST API
            if self.consumer_key and self.consumer_secret:
                return await self._fetch_via_rest_api(site_url, limit)
            else:
                # Fallback to scraping
                return await self._scrape_storefront(site_url)
                
        except Exception as e:
            logger.error(f"WooCommerce extraction failed: {e}")
            return {"error": str(e)}

    async def _fetch_via_rest_api(self, site_url: str, limit: int) -> Dict[str, Any]:
        """Fetch products using WooCommerce REST API v3"""
        api_url = f"{site_url.rstrip('/')}/wp-json/wc/v3/products"
        
        products = []
        page = 1
        per_page = min(100, limit)
        
        auth = (self.consumer_key, self.consumer_secret)
        
        async with httpx.AsyncClient(auth=auth) as client:
            while len(products) < limit:
                params = {
                    "page": page,
                    "per_page": per_page,
                    "status": "publish"
                }
                
                response = await client.get(api_url, params=params, timeout=30.0)
                
                if response.status_code != 200:
                    logger.error(f"WooCommerce API error: {response.status_code} - {response.text}")
                    break
                
                batch_products = response.json()
                if not batch_products:
                    break
                
                products.extend([self.format_product(p) for p in batch_products])
                page += 1
                
                # Check if we got all products
                if len(batch_products) < per_page:
                    break
        
        return {
            "products": products[:limit],
            "count": len(products),
            "source": "woocommerce_rest_api",
            "extracted_at": datetime.utcnow().isoformat()
        }

    async def _scrape_storefront(self, site_url: str) -> Dict[str, Any]:
        """Scrape products from WooCommerce storefront"""
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # Try to access products page
            products_url = f"{site_url.rstrip('/')}/shop/"
            
            try:
                response = await client.get(products_url)
                if response.status_code == 200:
                    # This would require BeautifulSoup parsing
                    # For now, return empty as this is complex
                    products = []
                else:
                    products = []
            except:
                products = []
            
            return {
                "products": products,
                "count": len(products),
                "source": "woocommerce_storefront_scraping",
                "extracted_at": datetime.utcnow().isoformat()
            }

    async def fetch_products(self, site_url: str) -> List[Dict[str, Any]]:
        """
        Legacy method - fetches products using the WooCommerce REST API v3.
        """
        if not self.consumer_key or not self.consumer_secret:
            logger.error("Missing WooCommerce API credentials")
            return []
            
        endpoint = f"{site_url.rstrip('/')}/wp-json/wc/v3/products"
        
        async with httpx.AsyncClient(auth=(self.consumer_key, self.consumer_secret)) as client:
            try:
                response = await client.get(endpoint, timeout=20.0)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"WooCommerce API error for {site_url}: {e}")
                return []

    def format_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced WooCommerce product formatting for the Optik pipeline.
        """
        # Handle different product types (simple, variable, etc.)
        product_type = product.get("type", "simple")
        
        # Get price based on product type
        if product_type == "variable":
            price = product.get("price", 0) or 0
            regular_price = product.get("regular_price", 0) or 0
        else:
            price = float(product.get("price", 0))
            regular_price = float(product.get("regular_price", price))
        
        # Handle images
        images = product.get("images", [])
        primary_image = images[0] if images else {}
        
        # Handle attributes for variations
        attributes = product.get("attributes", [])
        variations = product.get("variations", [])
        
        return {
            "external_id": str(product.get("id")),
            "title": product.get("name"),
            "description": product.get("description"),
            "short_description": product.get("short_description"),
            "price": price,
            "regular_price": regular_price,
            "sale_price": float(product.get("sale_price", 0)) if product.get("sale_price") else None,
            "currency": "USD",  # WooCommerce currency is set per store
            "images": [img.get("src") for img in images],
            "primary_image": primary_image.get("src"),
            "sku": product.get("sku"),
            "product_type": product_type,
            "status": product.get("status"),
            "stock_status": product.get("stock_status"),
            "manage_stock": product.get("manage_stock", False),
            "stock_quantity": product.get("stock_quantity"),
            "categories": [cat.get("name") for cat in product.get("categories", [])],
            "tags": [tag.get("name") for tag in product.get("tags", [])],
            "attributes": [
                {
                    "name": attr.get("name"),
                    "options": attr.get("options", []),
                    "visible": attr.get("visible", False),
                    "variation": attr.get("variation", False)
                } for attr in attributes
            ],
            "variations": variations,
            "weight": product.get("weight"),
            "dimensions": product.get("dimensions", {}),
            "shipping_required": product.get("shipping_required", True),
            "shipping_taxable": product.get("shipping_taxable", True),
            "featured": product.get("featured", False),
            "catalog_visibility": product.get("catalog_visibility", "visible"),
            "total_sales": product.get("total_sales", 0),
            "virtual": product.get("virtual", False),
            "downloadable": product.get("downloadable", False),
            "download_limit": product.get("download_limit"),
            "download_expiry": product.get("download_expiry"),
            "external_url": product.get("external_url"),
            "button_text": product.get("button_text"),
            "purchase_note": product.get("purchase_note"),
            "reviews_allowed": product.get("reviews_allowed", True),
            "average_rating": product.get("average_rating"),
            "rating_count": product.get("rating_count", 0),
            "related_ids": product.get("related_ids", []),
            "upsell_ids": product.get("upsell_ids", []),
            "cross_sell_ids": product.get("cross_sell_ids", []),
            "parent_id": product.get("parent_id"),
            "grouped_products": product.get("grouped_products", []),
            "menu_order": product.get("menu_order", 0),
            "date_created": product.get("date_created"),
            "date_modified": product.get("date_modified"),
            "raw": product
        }

    async def setup_webhooks(self, webhook_url: str) -> Dict[str, Any]:
        """Setup WooCommerce webhooks for real-time sync"""
        if not self.consumer_key or not self.consumer_secret or not self.api_base:
            raise ValueError("Missing WooCommerce API credentials")
        
        webhooks = [
            {
                "name": "Product Created",
                "status": "active",
                "topic": "product.created",
                "delivery_url": webhook_url
            },
            {
                "name": "Product Updated",
                "status": "active", 
                "topic": "product.updated",
                "delivery_url": webhook_url
            },
            {
                "name": "Product Deleted",
                "status": "active",
                "topic": "product.deleted", 
                "delivery_url": webhook_url
            }
        ]
        
        auth = (self.consumer_key, self.consumer_secret)
        created_webhooks = []
        
        async with httpx.AsyncClient(auth=auth) as client:
            for webhook in webhooks:
                response = await client.post(
                    f"{self.api_base}/webhooks",
                    json=webhook
                )
                
                if response.status_code == 201:
                    created_webhooks.append(response.json())
                else:
                    logger.warning(f"Failed to create webhook {webhook['topic']}: {response.text}")
        
        return {
            "created_webhooks": created_webhooks,
            "count": len(created_webhooks)
        }

    async def get_store_info(self) -> Dict[str, Any]:
        """Get WooCommerce store information"""
        if not self.consumer_key or not self.consumer_secret or not self.api_base:
            raise ValueError("Missing WooCommerce API credentials")
        
        auth = (self.consumer_key, self.consumer_secret)
        
        async with httpx.AsyncClient(auth=auth) as client:
            # Get general settings
            response = await client.get(f"{self.api_base}/settings/general")
            response.raise_for_status()
            
            general_settings = response.json()
            
            # Get system status
            system_response = await client.get(f"{self.api_base}/system_status")
            system_status = system_response.json() if system_response.status_code == 200 else {}
            
            return {
                "store_url": self.site_url,
                "currency": general_settings.get("woocommerce_currency", "USD"),
                "currency_symbol": general_settings.get("woocommerce_currency_symbol", "$"),
                "store_address": general_settings.get("woocommerce_store_address"),
                "store_city": general_settings.get("woocommerce_store_city"),
                "store_postcode": general_settings.get("woocommerce_store_postcode"),
                "store_country": general_settings.get("woocommerce_default_country"),
                "version": system_status.get("version"),
                "environment": system_status.get("environment"),
                "api_version": system_status.get("api_version")
            }

    def verify_webhook(self, payload: str, signature: str) -> bool:
        """Verify WooCommerce webhook signature"""
        if not self.consumer_secret:
            return False
        
        calculated_signature = base64.b64encode(
            hmac.new(
                self.consumer_secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).digest()
        ).decode()
        
        return hmac.compare_digest(calculated_signature, signature)
