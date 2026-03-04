from apify_client import ApifyClient
import pandas as pd

client = ApifyClient("apify_api_ssIG4xWWpymcNfQq9jBMXcv5aa6qJz4n9140")

# 1. Search for Shopify Stores using Google Search Scraper
print("Searching for store URLs...")
search_input = {
    "queries": "site:myshopify.com 'contact us'",
    "maxPagesPerQuery": 1,
    "resultsPerPage": 20
}
search_run = client.actor("apify/google-search-scraper").call(run_input=search_input)
search_results = client.dataset(search_run["defaultDatasetId"]).list_items().items

store_urls = []
for result in search_results:
    if "organicResults" in result:
        for entry in result["organicResults"]:
            url = entry["url"]
            # cleanup to get domain
            from urllib.parse import urlparse
            p = urlparse(url)
            store_urls.append(f"{p.scheme}://{p.netloc}")

store_urls = list(set(store_urls))[:10]
print(f"Found {len(store_urls)} store candidates: {store_urls}")

# 2. Extract Details with Contact Details Scraper
print("Scraping contact details...")
contact_input = {
    "startUrls": [{"url": u} for u in store_urls],
    "maxRequestsPerStartUrl": 5,
    "maxRequestsPerCrawl": 50
}
contact_run = client.actor("apify/contact-details-scraper").call(run_input=contact_input)
contact_results = client.dataset(contact_run["defaultDatasetId"]).list_items().items

# 3. Save to XLSX
df = pd.DataFrame(contact_results)
df.to_excel("shopify_leads.xlsx", index=False)
print("Finished! Leads saved to shopify_leads.xlsx")
