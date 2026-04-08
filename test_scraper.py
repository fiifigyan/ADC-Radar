import requests
import json

# Use the specific source endpoint instead of scrape_all
url = "http://localhost:5000/api/scrape/impactpool"
params = {"max_results": 1}

print("Testing Impactpool Scraper with JobTextParser...")
print("=" * 80)

try:
    response = requests.post(url, params=params, timeout=120)
    data = response.json()
    
    if "scraped_data" in data:
        print(f"\nScraped {len(data['scraped_data'])} opportunities\n")
        
        for i, job in enumerate(data['scraped_data'], 1):
            print(f"Job {i}:")
            print(f"  Title: {job.get('title', 'N/A')}")
            print(f"  Organization: {job.get('organization', 'N/A')}")
            print(f"  Location: {job.get('location', 'N/A')}")
            print(f"  URL: {job.get('url', 'N/A')[:70]}")
            print()
    else:
        print("Response:", json.dumps(data, indent=2))
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
