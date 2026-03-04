"""
Shopify Data Scraper - Conversion Intelligence for dApp Store
Scrapes e-commerce owners' conversion data from Shopify stores using MCP server
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import subprocess
import tempfile
from pathlib import Path

from optik_gpt.assistant.shopify_ai import get_shopify_ai, StoreMetrics
from config.settings import get_settings

logger = logging.getLogger(__name__)

@dataclass
class ShopifyStoreConfig:
    """Configuration for a Shopify store to scrape."""
    store_domain: str
    client_id: str
    client_secret: str
    access_token: Optional[str] = None
    store_name: str = ""
    niche: str = ""
    target_metrics: List[str] = None
    
    def __post_init__(self):
        if self.target_metrics is None:
            self.target_metrics = [
                "conversion_rate", "average_order_value", "traffic_sources",
                "top_products", "cart_abandonment_rate", "customer_lifetime_value"
            ]

@dataclass
class ConversionData:
    """Scraped conversion data from Shopify store."""
    store_domain: str
    scrape_timestamp: datetime
    conversion_rate: float
    average_order_value: float
    total_revenue: float
    total_orders: int
    unique_visitors: int
    cart_abandonment_rate: float
    customer_lifetime_value: float
    top_products: List[Dict[str, Any]]
    traffic_sources: Dict[str, float]
    conversion_funnel: Dict[str, Any]
    product_performance: List[Dict[str, Any]]
    customer_segments: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['scrape_timestamp'] = self.scrape_timestamp.isoformat()
        return data

class ShopifyDataScraper:
    """
    Advanced Shopify data scraper using MCP server integration
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.shopify_ai = get_shopify_ai()
        self.mcp_server_path = self._find_mcp_server()
        self.scraped_data_cache = {}
        
    def _find_mcp_server(self) -> str:
        """Find the shopify-mcp server executable."""
        try:
            # Try to find shopify-mcp in node_modules
            result = subprocess.run(
                ["which", "shopify-mcp"], 
                capture_output=True, 
                text=True,
                cwd="/home/kali/Dapp_Optik"
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
            
        # Fallback to npx
        return "npx shopify-mcp"
    
    async def scrape_store_data(self, store_config: ShopifyStoreConfig) -> ConversionData:
        """
        Scrape comprehensive conversion data from a Shopify store
        """
        logger.info(f"Starting data scrape for store: {store_config.store_domain}")
        
        try:
            # Get basic store metrics using MCP server
            raw_data = await self._fetch_shopify_data_via_mcp(store_config)
            
            # Process and enrich the data
            conversion_data = await self._process_raw_data(raw_data, store_config)
            
            # Generate AI insights
            insights = await self._generate_ai_insights(conversion_data, store_config)
            
            # Cache the data
            self.scraped_data_cache[store_config.store_domain] = {
                'data': conversion_data,
                'insights': insights,
                'timestamp': datetime.now()
            }
            
            logger.info(f"Successfully scraped data for {store_config.store_domain}")
            return conversion_data
            
        except Exception as e:
            logger.error(f"Failed to scrape data for {store_config.store_domain}: {str(e)}")
            raise
    
    async def _fetch_shopify_data_via_mcp(self, store_config: ShopifyStoreConfig) -> Dict[str, Any]:
        """
        Fetch data from Shopify using MCP server
        """
        # Create temporary config for MCP server
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            mcp_config = {
                "store_domain": store_config.store_domain,
                "client_id": store_config.client_id,
                "client_secret": store_config.client_secret
            }
            if store_config.access_token:
                mcp_config["access_token"] = store_config.access_token
                
            json.dump(mcp_config, f)
            temp_config_path = f.name
        
        try:
            # Prepare MCP server command
            cmd_args = [
                self.mcp_server_path,
                "--domain", store_config.store_domain,
                "--clientId", store_config.client_id,
                "--clientSecret", store_config.client_secret
            ]
            
            if store_config.access_token:
                cmd_args.extend(["--accessToken", store_config.access_token])
            
            # Execute MCP server to get data
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd="/home/kali/Dapp_Optik"
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"MCP server error: {stderr.decode()}")
            
            # Parse the response
            try:
                response_data = json.loads(stdout.decode())
                return response_data
            except json.JSONDecodeError:
                # If MCP server doesn't return JSON, create structured data from output
                return self._parse_mcp_output(stdout.decode())
                
        finally:
            # Clean up temporary file
            os.unlink(temp_config_path)
    
    def _parse_mcp_output(self, output: str) -> Dict[str, Any]:
        """
        Parse MCP server output when not in JSON format
        """
        # This is a fallback parser - implement based on actual MCP output format
        return {
            "products": [],
            "orders": [],
            "customers": [],
            "raw_output": output
        }
    
    async def _process_raw_data(self, raw_data: Dict[str, Any], 
                               store_config: ShopifyStoreConfig) -> ConversionData:
        """
        Process raw Shopify data into structured conversion metrics
        """
        logger.info("Processing raw Shopify data...")
        
        # Extract products
        products = raw_data.get('products', [])
        orders = raw_data.get('orders', [])
        customers = raw_data.get('customers', [])
        
        # Calculate conversion metrics
        total_revenue = sum(float(order.get('totalPriceSet', {}).get('shopMoney', {}).get('amount', 0)) 
                          for order in orders)
        total_orders = len(orders)
        
        # Estimate visitors (this would typically come from Shopify Analytics)
        unique_visitors = self._estimate_visitors(orders, customers)
        
        # Calculate conversion rate
        conversion_rate = (total_orders / unique_visitors * 100) if unique_visitors > 0 else 0
        
        # Calculate average order value
        average_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Calculate cart abandonment rate (estimated)
        cart_abandonment_rate = self._estimate_cart_abandonment(orders, customers)
        
        # Calculate customer lifetime value
        customer_lifetime_value = self._calculate_clv(orders, customers)
        
        # Get top products
        top_products = self._get_top_products(products, orders)
        
        # Analyze traffic sources (estimated from order data)
        traffic_sources = self._analyze_traffic_sources(orders)
        
        # Build conversion funnel
        conversion_funnel = self._build_conversion_funnel(
            unique_visitors, total_orders, total_revenue
        )
        
        # Analyze product performance
        product_performance = self._analyze_product_performance(products, orders)
        
        # Segment customers
        customer_segments = self._segment_customers(customers, orders)
        
        return ConversionData(
            store_domain=store_config.store_domain,
            scrape_timestamp=datetime.now(),
            conversion_rate=conversion_rate,
            average_order_value=average_order_value,
            total_revenue=total_revenue,
            total_orders=total_orders,
            unique_visitors=unique_visitors,
            cart_abandonment_rate=cart_abandonment_rate,
            customer_lifetime_value=customer_lifetime_value,
            top_products=top_products,
            traffic_sources=traffic_sources,
            conversion_funnel=conversion_funnel,
            product_performance=product_performance,
            customer_segments=customer_segments
        )
    
    def _estimate_visitors(self, orders: List[Dict], customers: List[Dict]) -> int:
        """Estimate unique visitors from orders and customers."""
        # This is a simplified estimation - in reality, you'd get this from Shopify Analytics
        customer_emails = set()
        for order in orders:
            email = order.get('email', '')
            if email:
                customer_emails.add(email)
        
        # Estimate visitors as customers * conversion factor (typically 2-5x)
        base_customers = len(customer_emails)
        estimated_visitors = int(base_customers * 3.5)  # 3.5x industry average
        
        return max(estimated_visitors, len(customers))
    
    def _estimate_cart_abandonment(self, orders: List[Dict], customers: List[Dict]) -> float:
        """Estimate cart abandonment rate."""
        # Industry average is around 70%
        # This could be improved with actual cart data from Shopify
        return 69.8
    
    def _calculate_clv(self, orders: List[Dict], customers: List[Dict]) -> float:
        """Calculate customer lifetime value."""
        if not orders:
            return 0
        
        # Group orders by customer
        customer_orders = {}
        for order in orders:
            email = order.get('email', '')
            if email:
                if email not in customer_orders:
                    customer_orders[email] = []
                customer_orders[email].append(float(order.get('totalPriceSet', {}).get('shopMoney', {}).get('amount', 0)))
        
        # Calculate average customer value
        customer_values = [sum(orders_list) for orders_list in customer_orders.values()]
        return sum(customer_values) / len(customer_values) if customer_values else 0
    
    def _get_top_products(self, products: List[Dict], orders: List[Dict]) -> List[Dict[str, Any]]:
        """Get top performing products."""
        product_sales = {}
        
        # Count sales per product
        for order in orders:
            for line_item in order.get('lineItems', []):
                product_id = line_item.get('productId', '')
                title = line_item.get('title', 'Unknown Product')
                quantity = int(line_item.get('quantity', 0))
                price = float(line_item.get('discountedUnitPriceSet', {}).get('shopMoney', {}).get('amount', 0))
                
                if product_id not in product_sales:
                    product_sales[product_id] = {
                        'title': title,
                        'quantity_sold': 0,
                        'revenue': 0
                    }
                
                product_sales[product_id]['quantity_sold'] += quantity
                product_sales[product_id]['revenue'] += quantity * price
        
        # Sort by revenue and return top 10
        sorted_products = sorted(product_sales.values(), 
                               key=lambda x: x['revenue'], reverse=True)
        return sorted_products[:10]
    
    def _analyze_traffic_sources(self, orders: List[Dict]) -> Dict[str, float]:
        """Analyze traffic sources from order data."""
        # This is a simplified analysis - in reality, you'd get this from Shopify Analytics
        return {
            "organic_search": 35.2,
            "direct": 25.8,
            "social_media": 18.5,
            "paid_ads": 15.3,
            "email": 3.2,
            "other": 2.0
        }
    
    def _build_conversion_funnel(self, visitors: int, orders: int, revenue: float) -> Dict[str, Any]:
        """Build conversion funnel data."""
        return {
            "visitors": visitors,
            "product_views": int(visitors * 0.6),  # 60% view products
            "add_to_cart": int(visitors * 0.2),   # 20% add to cart
            "checkout": int(visitors * 0.08),      # 8% start checkout
            "orders": orders,
            "revenue": revenue,
            "conversion_rates": {
                "visit_to_product_view": 60.0,
                "product_view_to_cart": 33.3,
                "cart_to_checkout": 40.0,
                "checkout_to_order": (orders / (visitors * 0.08) * 100) if visitors > 0 else 0
            }
        }
    
    def _analyze_product_performance(self, products: List[Dict], orders: List[Dict]) -> List[Dict[str, Any]]:
        """Analyze individual product performance."""
        performance_data = []
        
        for product in products[:20]:  # Limit to top 20 products
            product_id = product.get('id', '')
            title = product.get('title', 'Unknown')
            
            # Calculate metrics for this product
            product_orders = [o for o in orders if any(li.get('productId') == product_id for li in o.get('lineItems', []))]
            total_quantity = sum(int(li.get('quantity', 0)) 
                               for order in product_orders 
                               for li in order.get('lineItems', []) 
                               if li.get('productId') == product_id)
            
            if total_quantity > 0:
                performance_data.append({
                    'product_id': product_id,
                    'title': title,
                    'orders_count': len(product_orders),
                    'total_quantity_sold': total_quantity,
                    'average_price': float(product.get('priceRange', {}).get('minVariantPrice', {}).get('amount', 0))
                })
        
        return sorted(performance_data, key=lambda x: x['total_quantity_sold'], reverse=True)
    
    def _segment_customers(self, customers: List[Dict], orders: List[Dict]) -> List[Dict[str, Any]]:
        """Segment customers based on their behavior."""
        # Group orders by customer
        customer_orders = {}
        for order in orders:
            email = order.get('email', '')
            if email:
                if email not in customer_orders:
                    customer_orders[email] = []
                customer_orders[email].append(order)
        
        segments = {
            "VIP": [],      # High value, frequent buyers
            "Regular": [],  # Average customers
            "New": [],      # First-time buyers
            "At_Risk": []   # Haven't purchased recently
        }
        
        for email, cust_orders in customer_orders.items():
            total_spent = sum(float(o.get('totalPriceSet', {}).get('shopMoney', {}).get('amount', 0)) 
                             for o in cust_orders)
            order_count = len(cust_orders)
            last_order = max(o.get('createdAt', '') for o in cust_orders) if cust_orders else ''
            
            # Simple segmentation logic
            if total_spent > 500 and order_count > 5:
                segments["VIP"].append({"email": email, "total_spent": total_spent, "orders": order_count})
            elif order_count == 1:
                segments["New"].append({"email": email, "total_spent": total_spent, "orders": order_count})
            elif order_count > 1:
                segments["Regular"].append({"email": email, "total_spent": total_spent, "orders": order_count})
            else:
                segments["At_Risk"].append({"email": email, "total_spent": total_spent, "orders": order_count})
        
        return [{"segment": k, "count": len(v), "total_value": sum(c["total_spent"] for c in v)} 
                for k, v in segments.items() if v]
    
    async def _generate_ai_insights(self, conversion_data: ConversionData, 
                                  store_config: ShopifyStoreConfig) -> Dict[str, Any]:
        """Generate AI-powered insights from the conversion data."""
        try:
            # Convert to StoreMetrics for AI analysis
            store_metrics = StoreMetrics(
                conversion_rate=conversion_data.conversion_rate,
                average_order_value=conversion_data.average_order_value,
                traffic_sources=conversion_data.traffic_sources,
                top_products=conversion_data.top_products,
                cart_abandonment_rate=conversion_data.cart_abandonment_rate,
                customer_lifetime_value=conversion_data.customer_lifetime_value,
                inventory_levels={},  # Would need additional data
                profit_margins={}    # Would need additional data
            )
            
            # Generate optimization recommendations
            recommendations = await self.shopify_ai.generate_optimization_plan(store_metrics)
            
            # Analyze store performance
            performance_analysis = await self.shopify_ai.analyze_store_performance({
                'conversion_rate': conversion_data.conversion_rate,
                'average_order_value': conversion_data.average_order_value,
                'total_revenue': conversion_data.total_revenue,
                'cart_abandonment_rate': conversion_data.cart_abandonment_rate,
                'customer_lifetime_value': conversion_data.customer_lifetime_value,
                'top_products': conversion_data.top_products,
                'traffic_sources': conversion_data.traffic_sources
            })
            
            return {
                'recommendations': [asdict(rec) for rec in recommendations],
                'performance_analysis': performance_analysis,
                'competitive_insights': self._generate_competitive_insights(conversion_data),
                'dapp_opportunities': self._identify_dapp_opportunities(conversion_data, store_config)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate AI insights: {str(e)}")
            return {'error': str(e)}
    
    def _generate_competitive_insights(self, conversion_data: ConversionData) -> Dict[str, Any]:
        """Generate competitive insights."""
        industry_benchmarks = {
            "ecommerce_overall": {"conversion_rate": 2.5, "aov": 85.0, "cart_abandonment": 69.8},
            "fashion": {"conversion_rate": 1.8, "aov": 95.0, "cart_abandonment": 72.1},
            "electronics": {"conversion_rate": 1.2, "aov": 150.0, "cart_abandonment": 75.3},
            "beauty": {"conversion_rate": 3.2, "aov": 65.0, "cart_abandonment": 68.5}
        }
        
        # Compare against benchmarks (using overall as default)
        benchmark = industry_benchmarks["ecommerce_overall"]
        
        return {
            "conversion_vs_benchmark": {
                "store_rate": conversion_data.conversion_rate,
                "benchmark_rate": benchmark["conversion_rate"],
                "performance": "above" if conversion_data.conversion_rate > benchmark["conversion_rate"] else "below"
            },
            "aov_vs_benchmark": {
                "store_aov": conversion_data.average_order_value,
                "benchmark_aov": benchmark["aov"],
                "performance": "above" if conversion_data.average_order_value > benchmark["aov"] else "below"
            },
            "abandonment_vs_benchmark": {
                "store_rate": conversion_data.cart_abandonment_rate,
                "benchmark_rate": benchmark["cart_abandonment"],
                "performance": "better" if conversion_data.cart_abandonment_rate < benchmark["cart_abandonment"] else "worse"
            }
        }
    
    def _identify_dapp_opportunities(self, conversion_data: ConversionData, 
                                   store_config: ShopifyStoreConfig) -> List[Dict[str, Any]]:
        """Identify opportunities for dApp integration."""
        opportunities = []
        
        # High cart abandonment -> dApp recovery solution
        if conversion_data.cart_abandonment_rate > 70:
            opportunities.append({
                "opportunity": "Cart Recovery dApp",
                "description": "Implement blockchain-based cart recovery with token incentives",
                "potential_impact": "15-25% recovery rate",
                "implementation_complexity": "medium"
            })
        
        # Low conversion rate -> dApp loyalty program
        if conversion_data.conversion_rate < 2.0:
            opportunities.append({
                "opportunity": "Token Loyalty Program",
                "description": "Create NFT-based loyalty program to increase repeat purchases",
                "potential_impact": "20-30% conversion increase",
                "implementation_complexity": "high"
            })
        
        # High AOV -> premium dApp features
        if conversion_data.average_order_value > 100:
            opportunities.append({
                "opportunity": "Premium NFT Collectibles",
                "description": "Offer exclusive NFTs with high-value purchases",
                "potential_impact": "10-15% AOV increase",
                "implementation_complexity": "low"
            })
        
        # Multiple customer segments -> personalized dApp experiences
        if len(conversion_data.customer_segments) > 2:
            opportunities.append({
                "opportunity": "Segmented dApp Experiences",
                "description": "Create personalized dApp experiences for different customer segments",
                "potential_impact": "25-35% engagement increase",
                "implementation_complexity": "medium"
            })
        
        return opportunities
    
    async def batch_scrape_stores(self, store_configs: List[ShopifyStoreConfig]) -> Dict[str, ConversionData]:
        """
        Scrape multiple stores in parallel
        """
        logger.info(f"Starting batch scrape for {len(store_configs)} stores")
        
        tasks = [self.scrape_store_data(config) for config in store_configs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        scraped_data = {}
        for config, result in zip(store_configs, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to scrape {config.store_domain}: {str(result)}")
            else:
                scraped_data[config.store_domain] = result
        
        return scraped_data
    
    def get_cached_data(self, store_domain: str) -> Optional[Dict[str, Any]]:
        """Get cached scraped data for a store."""
        return self.scraped_data_cache.get(store_domain)
    
    def export_data_for_dapp(self, store_domains: List[str] = None) -> Dict[str, Any]:
        """
        Export scraped data in format suitable for dApp integration
        """
        if store_domains is None:
            store_domains = list(self.scraped_data_cache.keys())
        
        dapp_data = {
            "export_timestamp": datetime.now().isoformat(),
            "stores": {},
            "aggregated_insights": {},
            "market_opportunities": []
        }
        
        all_conversion_rates = []
        all_aovs = []
        all_revenue = []
        
        for domain in store_domains:
            cached = self.scraped_data_cache.get(domain)
            if cached:
                data = cached['data']
                insights = cached['insights']
                
                dapp_data["stores"][domain] = {
                    "metrics": data.to_dict(),
                    "insights": insights,
                    "dapp_opportunities": insights.get('dapp_opportunities', [])
                }
                
                all_conversion_rates.append(data.conversion_rate)
                all_aovs.append(data.average_order_value)
                all_revenue.append(data.total_revenue)
        
        # Calculate aggregated insights
        if all_conversion_rates:
            dapp_data["aggregated_insights"] = {
                "average_conversion_rate": sum(all_conversion_rates) / len(all_conversion_rates),
                "average_aov": sum(all_aovs) / len(all_aovs),
                "total_market_revenue": sum(all_revenue),
                "store_count": len(store_domains),
                "high_potential_stores": [
                    domain for domain in store_domains
                    if self.scraped_data_cache.get(domain, {}).get('data', {}).get('conversion_rate', 0) > 3.0
                ]
            }
        
        return dapp_data

# Global instance
_shopify_scraper = None

def get_shopify_scraper() -> ShopifyDataScraper:
    """Get or create the Shopify scraper instance."""
    global _shopify_scraper
    if _shopify_scraper is None:
        _shopify_scraper = ShopifyDataScraper()
    return _shopify_scraper
