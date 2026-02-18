import logging
from typing import Dict, Any

from pipelines.ingestion_manager import UniversalIngestionManager

logger = logging.getLogger(__name__)

class ScrapingPipeline:
    """
    Point 1 Fix: The DApp Conversion Engine Ingestion.
    Consolidated to use UniversalIngestionManager for 99% platform coverage.
    """
    def __init__(self):
        self.manager = UniversalIngestionManager()

    async def run(self, url: str, platform: str = None, api_credentials: Dict[str, str] = None) -> Dict[str, Any]:
        logger.info(f"🚀 RUNNING UNIVERSAL INGESTION: {url}")
        
        # If we have direct API credentials (e.g. Shopify Private App), we could still use integrations.
        # Otherwise, we use the Manager's intelligent scraping fleet.
        
        result = await self.manager.ingest(url, platform)
        
        # Log fidelity for Audit (Strategic Point 1)
        if result['fidelity_score'] < 0.7:
            logger.warning(f"⚠️ LOW FIDELITY INGESTION ({result['fidelity_score']}) for {url}")
            
        return result
