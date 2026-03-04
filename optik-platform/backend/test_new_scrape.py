import asyncio
import json
from agents.scraper_agent import ShopifyScraperAgent

async def main():
    scraper = ShopifyScraperAgent()
    try:
        url = "https://breeo.myshopify.com"
        print(f"Scraping {url}...")
        res = await scraper.preview_store(url, limit=5)
        print(json.dumps(res, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
