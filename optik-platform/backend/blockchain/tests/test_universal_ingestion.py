import asyncio
import json
from unittest.mock import MagicMock, patch
import httpx
from pipelines.ingestion_manager import UniversalIngestionManager

async def test_meta_ingestion():
    manager = UniversalIngestionManager()
    
    # Mocking a custom "Magento" or "Custom" store HTML with JSON-LD
    mock_html = """
    <html>
        <head>
            <title>Premium Tech Store</title>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org/",
                "@type": "Product",
                "name": "Optik Quantum Watch",
                "image": ["https://example.com/watch.jpg"],
                "description": "The ultimate timepiece for the Web3 explorer.",
                "sku": "OPT-QNT-001",
                "offers": {
                    "@type": "Offer",
                    "priceCurrency": "USD",
                    "price": "599.00",
                    "availability": "https://schema.org/InStock"
                }
            }
            </script>
        </head>
        <body>
            <h1>Optik Quantum Watch</h1>
            <p>Welcome to our custom bespoke store.</p>
        </body>
    </html>
    """

    print("\n🚀 TESTING UNIVERSAL INGESTION (MetaScraper Fallback)")
    print("-" * 60)
    print("Target: https://bespoke-watch-store.com (Non-Shopify/Non-Woo)")

    # Mocking httpx Response
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.text = mock_html
    mock_response.url = httpx.URL("https://bespoke-watch-store.com")

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await manager.ingest("https://bespoke-watch-store.com")
        
        print(f"\n[DETECTION] Platform Identified: {result['platform'].upper()}")
        print(f"[FIDELITY] Data Integrity Score: {result['fidelity_score'] * 100}%")
        
        if result['count'] > 0:
            product = result['products'][0]
            print(f"\n[EXTRACTED DATA]")
            print(f"📦 Product: {product['title']}")
            print(f"💰 Price:   {product['price']} {product['currency']}")
            print(f"🆔 SKU:     {product['sku']}")
            print(f"🖼️ Images:  {len(product['images'])} found")
            print(f"\n✅ SUCCESS: Custom platform data successfully normalized to Optik standard.")
        else:
            print("\n❌ FAILED: No product data found via MetaScraper.")

    print("-" * 60)

if __name__ == "__main__":
    asyncio.run(test_meta_ingestion())
