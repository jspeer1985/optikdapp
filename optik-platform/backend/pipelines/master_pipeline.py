"""
Master Pipeline - Orchestrates the complete DApp conversion workflow
Integrates ScrapingPipeline with UniversalIngestionManager for end-to-end processing
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from pipelines.scraping_pipeline import ScrapingPipeline
from pipelines.ingestion_manager import UniversalIngestionManager
from pipelines.deployment_pipeline import DeploymentPipeline

logger = logging.getLogger(__name__)

class MasterPipeline:
    """
    Main orchestrator for the DApp conversion engine.
    Coordinates ingestion, processing, and deployment phases.
    """
    
    def __init__(self):
        self.scraping_pipeline = ScrapingPipeline()
        self.ingestion_manager = UniversalIngestionManager()
        self.deployment_pipeline = DeploymentPipeline()
    
    async def execute_full_pipeline(self, source_url: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the complete pipeline from source URL to deployed DApp
        
        Args:
            source_url: URL of the e-commerce store to convert
            config: Optional configuration for pipeline behavior
            
        Returns:
            Dict containing pipeline results and deployment info
        """
        job_id = f"job_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Phase 1: Ingestion via UniversalIngestionManager
            logger.info(f"Starting ingestion for {source_url}")
            
            ingestion_result = await self.ingestion_manager.ingest_store(source_url, config or {})
            
            if not ingestion_result.get("products"):
                raise ValueError("No products found during ingestion")
            
            # Phase 2: Processing via ScrapingPipeline
            logger.info("Processing scraped data")
            
            processing_result = await self.scraping_pipeline.process_products(
                ingestion_result["products"],
                config or {}
            )
            
            # Phase 3: Deployment
            logger.info("Deploying DApp")
            
            deployment_result = await self.deployment_pipeline.deploy(
                processing_result,
                config or {}
            )
            
            result = {
                "job_id": job_id,
                "status": "completed",
                "deployment_url": deployment_result.get("url"),
                "total_products": len(ingestion_result["products"])
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Master pipeline failed: {e}")
            error_result = {
                "job_id": job_id,
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
            
            return error_result
    
    async def get_pipeline_status(self, job_id: str) -> Dict[str, Any]:
        """Get the current status of a pipeline job"""
        return {"job_id": job_id, "status": "unknown"}
    
    async def cancel_pipeline(self, job_id: str) -> bool:
        """Cancel a running pipeline job"""
        return False
    
    async def list_recent_jobs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent pipeline jobs"""
        return []

# Singleton instance for application-wide use
master_pipeline = MasterPipeline()
