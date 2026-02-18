import logging
import asyncio
import os
from typing import Dict, Any, List, Optional
from agents.scraper_agent import ShopifyScraperAgent, WooCommerceScraperAgent
from agents.analyzer_agent import StoreAnalyzerAgent
from agents.converter_agent import Web3ConverterAgent
from agents.deployer_agent import SolanaDeployerAgent
from utils.image_processor import ImageProcessor
from utils.nft_generator import NFTGenerator

logger = logging.getLogger(__name__)

class ConversionPipeline:
    """
    Enterprise pipeline for Web2 to Web3 store conversion.
    """
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.shopify_scraper = ShopifyScraperAgent()
        self.woo_scraper = WooCommerceScraperAgent()
        self.analyzer = StoreAnalyzerAgent()
        self.converter = Web3ConverterAgent()
        self.image_processor = ImageProcessor()

    async def scrape_store(self, url: str, platform: str, api_key: str = None, api_secret: str = None) -> Dict[str, Any]:
        logger.info(f"Pipeline {self.job_id}: Scraping {url}")
        import httpx
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            if platform == 'shopify':
                products = await self.shopify_scraper.scrape_products(url, client)
            elif platform == 'woocommerce':
                products = await self.woo_scraper.scrape_products(url, client, api_key=api_key, api_secret=api_secret)
            else:
                raise ValueError(f"Unsupported platform: {platform}")

        return {
            "store_info": {"name": url.split("//")[-1].split(".")[0], "platform": platform},
            "url": url,
            "platform": platform,
            "products": products,
        }

    async def analyze_store(self, store_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Pipeline {self.job_id}: Analyzing store")
        return await self.analyzer.analyze(store_data)

    async def convert_to_web3(self, store_data: Dict[str, Any], analysis: Dict[str, Any], tier: str) -> Dict[str, Any]:
        logger.info(f"Pipeline {self.job_id}: Converting to Web3 with tier {tier}")
        
        # Determine activated agents based on tier
        tier_mapping = {
            'basic': ['Core Optik AI'],
            'growth': ['Marketing Agent', 'Product Agent'],
            'global': ['Marketing Agent', 'Product Agent', 'UI Design Agent'],
            'scale': ['Marketing Agent', 'Product Agent', 'UI Design Agent', 'Security Agent'],
            'elite': ['Marketing Agent', 'Product Agent', 'UI Design Agent', 'Security Agent', 'NFT Assistant', 'Optik AI+']
        }
        active_agents = tier_mapping.get(tier.lower(), ['Core Optik AI'])
        
        logger.info(f"Activating {len(active_agents)} agents for {tier} tier conversion")
        
        pairing_token = os.getenv("OPTIK_PAIRING_TOKEN", "OPTIK")
        collection_symbol = os.getenv("OPTIK_COLLECTION_SYMBOL", pairing_token)
        products = store_data.get("products", [])
        converted_products = []
        for p in products:
            conv = await self.converter.convert(p)
            image_url = await self.image_processor.upload_to_ipfs(conv["image"])
            attributes = NFTGenerator.format_attributes(p)
            attributes.append({"trait_type": "Pairing Token", "value": pairing_token})
            metadata = NFTGenerator.generate_metadata(
                name=conv["title"],
                symbol=collection_symbol,
                description=conv["description"],
                image_url=image_url,
                attributes=attributes,
                seller_fee_basis_points=int(os.getenv("DEFAULT_ROYALTY_BPS", "500")),
                external_url=store_data.get("url"),
            )
            metadata_url = await self.image_processor.upload_json(metadata, conv["title"])

            converted_products.append({
                "id": p.get("id"),
                "title": conv["title"],
                "description": conv["description"],
                "price_sol": conv["price_sol"],
                "price": conv["price"],
                "currency": conv["currency"],
                "image_url": image_url,
                "metadata_url": metadata_url,
                "pairing_token": pairing_token,
            })

        return {
            "store": {
                "name": store_data.get("store_info", {}).get("name"),
                "url": store_data.get("url"),
                "platform": store_data.get("platform"),
                "currency": "USD",
                "pairing_token": pairing_token,
            },
            "products": converted_products,
            "tier": tier,
            "active_agents": active_agents,
        }

    async def generate_nfts(self, web3_store: Dict[str, Any]) -> List[Dict[str, Any]]:
        logger.info(f"Pipeline {self.job_id}: Generating NFTs")
        nfts = []
        for p in web3_store.get("products", []):
            nfts.append({
                "product_id": p.get("id"),
                "metadata_url": p.get("metadata_url"),
                "image_url": p.get("image_url"),
            })
        return nfts
