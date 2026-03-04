"""
Shopify Data Scraping API Routes
Endpoints for scraping e-commerce stores' conversion data for dApp integration
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging
from datetime import datetime

from shopify_data_scraper import (
    get_shopify_scraper, 
    ShopifyStoreConfig, 
    ConversionData
)
from config.settings import get_settings
from utils.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/shopify-scraping", tags=["shopify-scraping"])

# Pydantic models for API requests/responses
class StoreConfigRequest(BaseModel):
    store_domain: str = Field(..., description="Shopify store domain (e.g., mystore.myshopify.com)")
    client_id: str = Field(..., description="Shopify app client ID")
    client_secret: str = Field(..., description="Shopify app client secret")
    access_token: Optional[str] = Field(None, description="Shopify access token (for legacy apps)")
    store_name: str = Field("", description="Human-readable store name")
    niche: str = Field("", description="Store niche/category")
    target_metrics: List[str] = Field(
        default=["conversion_rate", "average_order_value", "traffic_sources"],
        description="Metrics to scrape"
    )

class BatchScrapeRequest(BaseModel):
    stores: List[StoreConfigRequest]
    parallel: bool = Field(True, description="Run scraping in parallel")

class ScrapeResponse(BaseModel):
    success: bool
    store_domain: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    scrape_timestamp: str

class BatchScrapeResponse(BaseModel):
    success: bool
    total_stores: int
    successful_scrapes: int
    failed_scrapes: int
    results: Dict[str, ScrapeResponse]
    execution_time_seconds: float

class DappDataResponse(BaseModel):
    export_timestamp: str
    stores: Dict[str, Any]
    aggregated_insights: Dict[str, Any]
    market_opportunities: List[Dict[str, Any]]

@router.post("/scrape-single", response_model=ScrapeResponse)
async def scrape_single_store(
    request: StoreConfigRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Scrape conversion data from a single Shopify store
    """
    try:
        scraper = get_shopify_scraper()
        
        # Convert request to config
        store_config = ShopifyStoreConfig(
            store_domain=request.store_domain,
            client_id=request.client_id,
            client_secret=request.client_secret,
            access_token=request.access_token,
            store_name=request.store_name,
            niche=request.niche,
            target_metrics=request.target_metrics
        )
        
        # Perform scraping
        conversion_data = await scraper.scrape_store_data(store_config)
        
        # Get cached insights
        cached_data = scraper.get_cached_data(request.store_domain)
        insights = cached_data.get('insights') if cached_data else {}
        
        return ScrapeResponse(
            success=True,
            store_domain=request.store_domain,
            data={
                "metrics": conversion_data.to_dict(),
                "insights": insights,
                "dapp_opportunities": insights.get('dapp_opportunities', [])
            },
            scrape_timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Failed to scrape store {request.store_domain}: {str(e)}")
        return ScrapeResponse(
            success=False,
            store_domain=request.store_domain,
            error=str(e),
            scrape_timestamp=datetime.now().isoformat()
        )

@router.post("/scrape-batch", response_model=BatchScrapeResponse)
async def scrape_multiple_stores(
    request: BatchScrapeRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Scrape conversion data from multiple Shopify stores
    """
    start_time = datetime.now()
    
    try:
        scraper = get_shopify_scraper()
        
        # Convert requests to configs
        store_configs = [
            ShopifyStoreConfig(
                store_domain=store.store_domain,
                client_id=store.client_id,
                client_secret=store.client_secret,
                access_token=store.access_token,
                store_name=store.store_name,
                niche=store.niche,
                target_metrics=store.target_metrics
            )
            for store in request.stores
        ]
        
        # Perform batch scraping
        scraped_data = await scraper.batch_scrape_stores(store_configs)
        
        # Build response
        results = {}
        successful_count = 0
        failed_count = 0
        
        for config in store_configs:
            domain = config.store_domain
            if domain in scraped_data:
                # Successful scrape
                cached_data = scraper.get_cached_data(domain)
                insights = cached_data.get('insights') if cached_data else {}
                
                results[domain] = ScrapeResponse(
                    success=True,
                    store_domain=domain,
                    data={
                        "metrics": scraped_data[domain].to_dict(),
                        "insights": insights,
                        "dapp_opportunities": insights.get('dapp_opportunities', [])
                    },
                    scrape_timestamp=datetime.now().isoformat()
                )
                successful_count += 1
            else:
                # Failed scrape
                results[domain] = ScrapeResponse(
                    success=False,
                    store_domain=domain,
                    error="Scraping failed - check logs for details",
                    scrape_timestamp=datetime.now().isoformat()
                )
                failed_count += 1
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return BatchScrapeResponse(
            success=True,
            total_stores=len(request.stores),
            successful_scrapes=successful_count,
            failed_scrapes=failed_count,
            results=results,
            execution_time_seconds=execution_time
        )
        
    except Exception as e:
        logger.error(f"Batch scraping failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch scraping failed: {str(e)}")

@router.get("/export-dapp-data", response_model=DappDataResponse)
async def export_dapp_data(
    store_domains: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Export scraped data in format suitable for dApp integration
    """
    try:
        scraper = get_shopify_scraper()
        
        # Parse store domains
        domains = None
        if store_domains:
            domains = [domain.strip() for domain in store_domains.split(',')]
        
        # Export data
        dapp_data = scraper.export_data_for_dapp(domains)
        
        return DappDataResponse(**dapp_data)
        
    except Exception as e:
        logger.error(f"Failed to export dApp data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.get("/cached-data/{store_domain}")
async def get_cached_store_data(
    store_domain: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get cached scraped data for a specific store
    """
    try:
        scraper = get_shopify_scraper()
        cached_data = scraper.get_cached_data(store_domain)
        
        if not cached_data:
            raise HTTPException(status_code=404, detail="No cached data found for this store")
        
        return {
            "store_domain": store_domain,
            "cached_at": cached_data['timestamp'].isoformat(),
            "data": cached_data['data'].to_dict(),
            "insights": cached_data['insights']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get cached data for {store_domain}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve cached data: {str(e)}")

@router.get("/scraping-status")
async def get_scraping_status(
    current_user: dict = Depends(get_current_user)
):
    """
    Get status of scraping operations and cached data
    """
    try:
        scraper = get_shopify_scraper()
        
        # Get all cached stores
        cached_stores = list(scraper.scraped_data_cache.keys())
        
        # Calculate statistics
        total_stores = len(cached_stores)
        recent_scrapes = 0
        total_revenue = 0
        
        for domain in cached_stores:
            cached = scraper.scraped_data_cache[domain]
            # Check if scraped in last 24 hours
            if (datetime.now() - cached['timestamp']).total_seconds() < 86400:
                recent_scrapes += 1
            total_revenue += cached['data'].total_revenue
        
        return {
            "total_cached_stores": total_stores,
            "recent_scrapes_24h": recent_scrapes,
            "total_market_revenue": total_revenue,
            "cached_stores": cached_stores,
            "mcp_server_status": "active",
            "last_update": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get scraping status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@router.delete("/cache/{store_domain}")
async def clear_store_cache(
    store_domain: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Clear cached data for a specific store
    """
    try:
        scraper = get_shopify_scraper()
        
        if store_domain in scraper.scraped_data_cache:
            del scraper.scraped_data_cache[store_domain]
            return {"message": f"Cache cleared for {store_domain}"}
        else:
            raise HTTPException(status_code=404, detail="No cached data found for this store")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to clear cache for {store_domain}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")

@router.get("/market-insights")
async def get_market_insights(
    current_user: dict = Depends(get_current_user)
):
    """
    Get aggregated market insights from all scraped stores
    """
    try:
        scraper = get_shopify_scraper()
        
        if not scraper.scraped_data_cache:
            return {"message": "No scraped data available"}
        
        # Aggregate metrics across all stores
        all_conversion_rates = []
        all_aovs = []
        all_revenue = []
        niches = {}
        opportunities = []
        
        for domain, cached in scraper.scraped_data_cache.items():
            data = cached['data']
            insights = cached['insights']
            
            all_conversion_rates.append(data.conversion_rate)
            all_aovs.append(data.average_order_value)
            all_revenue.append(data.total_revenue)
            
            # Collect dApp opportunities
            if 'dapp_opportunities' in insights:
                opportunities.extend(insights['dapp_opportunities'])
        
        # Calculate insights
        market_insights = {
            "total_stores_analyzed": len(scraper.scraped_data_cache),
            "average_conversion_rate": sum(all_conversion_rates) / len(all_conversion_rates) if all_conversion_rates else 0,
            "average_aov": sum(all_aovs) / len(all_aovs) if all_aovs else 0,
            "total_market_revenue": sum(all_revenue),
            "top_dapp_opportunities": [
                opp for opp in opportunities 
                if opp.get('opportunity') in [o.get('opportunity') for o in opportunities]
            ][:5],
            "market_trends": {
                "high_conversion_stores": len([r for r in all_conversion_rates if r > 3.0]),
                "high_aov_stores": len([a for a in all_aovs if a > 100]),
                "revenue_distribution": {
                    "under_10k": len([r for r in all_revenue if r < 10000]),
                    "10k_to_100k": len([r for r in all_revenue if 10000 <= r < 100000]),
                    "over_100k": len([r for r in all_revenue if r >= 100000])
                }
            },
            "recommendations": {
                "best_dapp_features": [
                    "Token-based loyalty programs",
                    "Cart recovery with NFT incentives", 
                    "Premium NFT collectibles",
                    "Segmented dApp experiences"
                ],
                "target_store_profiles": [
                    "Stores with >3% conversion rate",
                    "Stores with AOV > $100",
                    "Stores with high cart abandonment (>70%)"
                ]
            }
        }
        
        return market_insights
        
    except Exception as e:
        logger.error(f"Failed to generate market insights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")
