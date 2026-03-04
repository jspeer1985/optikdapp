import requests
import pandas as pd
import time

APIFY_TOKEN = "apify_api_ssIG4xWWpymcNfQq9jBMXcv5aa6qJz4n9140"

def run_apify_actor(actor_id, input_data):
    url = f"https://api.apify.com/v2/acts/{actor_id}/run?token={APIFY_TOKEN}"
    res = requests.post(url, json=input_data)
    if res.status_code != 201:
        print(f"Error starting actor: {res.text}")
        return None
    run_id = res.json()["data"]["id"]
    print(f"Started run {run_id} for actor {actor_id}")
    return run_id

def wait_for_run(actor_id, run_id):
    url = f"https://api.apify.com/v2/acts/{actor_id}/runs/{run_id}?token={APIFY_TOKEN}"
    while True:
        res = requests.get(url)
        status = res.json()["data"]["status"]
        if status in ["SUCCEEDED", "FAILED", "ABORTED"]:
            return status
        print(f"Status: {status}...")
        time.sleep(10)

def get_dataset_items(dataset_id):
    url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}"
    res = requests.get(url)
    return res.json()

# Proposed Strategy: 
# 1. Use Google Search Scraper to find "powered by shopify" sites
# 2. Extract domains
# 3. Use Contact Details Scraper on those domains

# For this demo, we'll try to find some and scrape contact info.
actor_search = "apify/google-search-scraper"
search_input = {
    "queries": "site:myshopify.com \"contact us\"",
    "maxPagesPerQuery": 1,
    "resultsPerPage": 20
}

# 1. Run Search
run_id = run_apify_actor(actor_search, search_input)
if run_id:
    status = wait_for_run(actor_search, run_id)
    if status == "SUCCEEDED":
        # Get dataset
        run_data = requests.get(f"https://api.apify.com/v2/acts/{actor_search}/runs/{run_id}?token={APIFY_TOKEN}").json()
        dataset_id = run_data["data"]["defaultDatasetId"]
        results = get_dataset_items(dataset_id)
        
        urls = [r["url"] for r in results if "organicResults" in r for r in r["organicResults"]]
        print(f"Found {len(urls)} candidates.")
        
        # 2. Run Contact Scraper
        actor_contact = "apify/contact-details-scraper"
        contact_input = {
            "startUrls": [{"url": u} for u in urls[:5]], # limit for first run
            "maxRequestsPerStartUrl": 1,
            "maxRequestsPerCrawl": 5
        }
        
        c_run_id = run_apify_actor(actor_contact, contact_input)
        if c_run_id:
            c_status = wait_for_run(actor_contact, c_run_id)
            if c_status == "SUCCEEDED":
                c_run_data = requests.get(f"https://api.apify.com/v2/acts/{actor_contact}/runs/{c_run_id}?token={APIFY_TOKEN}").json()
                c_dataset_id = c_run_data["data"]["defaultDatasetId"]
                final_results = get_dataset_items(c_dataset_id)
                
                # Report
                df = pd.DataFrame(final_results)
                df.to_excel("leads.xlsx", index=False)
                print("Leads saved to leads.xlsx")
