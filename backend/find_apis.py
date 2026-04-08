"""Practical network interception - find and call internal APIs directly"""
import requests
import json
import time
from urllib.parse import urljoin
import re


def find_api_endpoints():
    """Find API endpoints by analyzing page requests and scripts"""
    
    print("=" * 80)
    print("IMPACTPOOL API DISCOVERY")
    print("=" * 80)
    
    # Try direct API endpoints (common patterns)
    base_url = "https://www.impactpool.org"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.impactpool.org/jobs',
        'Accept': 'application/json'
    }
    
    # Common API patterns to try
    api_patterns = [
        f"{base_url}/api/jobs",
        f"{base_url}/api/opportunities",
        f"{base_url}/api/search",
        f"{base_url}/api/listings",
        f"{base_url}/jobs/api",
        f"{base_url}/graphql",
    ]
    
    print("\n1. Testing common API endpoints:")
    print("-" * 80)
    
    for api_url in api_patterns:
        try:
            response = requests.get(api_url, headers=headers, timeout=5)
            print(f"  {api_url}")
            print(f"    Status: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"    ✓ Valid JSON response!")
                    print(f"    Keys: {list(data.keys())[:5] if isinstance(data, dict) else f'{len(data)} items'}")
                    if isinstance(data, dict) and 'jobs' in data:
                        print(f"    Found {len(data['jobs'])} jobs!")
                        return data
                except:
                    print(f"    Response: {response.text[:100]}")
        except Exception as e:
            print(f"  {api_url} - {str(e)[:50]}")
    
    # Try fetching the jobs page and analyzing its network requests
    print("\n2. Analyzing page source for API calls:")
    print("-" * 80)
    
    try:
        response = requests.get(f"{base_url}/jobs", headers=headers, timeout=10)
        html = response.text
        
        # Look for fetch/XHR calls in JavaScript
        fetch_patterns = [
            r'fetch\([\'"]([^\'"]+)[\'"]',
            r'fetch\([\'"]([^\'"]+)',
            r'url:\s*[\'"]([^\'"]*api[^\'"]*)[\'"]',
            r'https://[^\s"\'<>]*api[^\s"\'<>]*',
        ]
        
        apis_found = set()
        for pattern in fetch_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                if match and len(match) > 10:  # Filter out noise
                    apis_found.add(match)
        
        for api in list(apis_found)[:10]:
            print(f"  Found: {api[:100]}")
            
            # Try to call it
            if api.startswith('http'):
                try:
                    api_response = requests.get(api, headers=headers, timeout=5)
                    print(f"    Status: {api_response.status_code}")
                    if api_response.status_code == 200:
                        try:
                            data = api_response.json()
                            print(f"    ✓ Returns JSON")
                            if isinstance(data, dict):
                                print(f"    Keys: {list(data.keys())[:5]}")
                                # Look for job data
                                for key in data:
                                    if 'job' in key.lower() or 'position' in key.lower():
                                        print(f"    ✓ Contains job data under '{key}'")
                                        return api, data
                        except:
                            pass
                except:
                    pass
    
    except Exception as e:
        print(f"Error analyzing page: {e}")
    
    # Try Contentful API (many sites use it)
    print("\n3. Testing Contentful CMS (common for job boards):")
    print("-" * 80)
    
    try:
        response = requests.get(f"{base_url}/jobs", headers=headers, timeout=10)
        if 'contentful' in response.text.lower():
            print("  ✓ Site uses Contentful!")
            
            # Extract Contentful space ID if present
            match = re.search(r'space["\']?\s*:\s*["\']([^"\']+)["\']', response.text)
            if match:
                space_id = match.group(1)
                print(f"  Space ID: {space_id}")
                
                # Try Contentful API
                contentful_urls = [
                    f"https://cdn.contentful.com/spaces/{space_id}/entries",
                    f"https://preview.contentful.com/spaces/{space_id}/entries",
                ]
                
                for cf_url in contentful_urls:
                    try:
                        cf_response = requests.get(cf_url, timeout=5)
                        print(f"    {cf_url}: {cf_response.status_code}")
                    except:
                        pass
    except:
        pass
    
    # Try GraphQL endpoint (modern APIs often use it)
    print("\n4. Testing GraphQL endpoint:")
    print("-" * 80)
    
    graphql_query = """
    query {
        jobs {
            id
            title
            organization
            description
        }
    }
    """
    
    try:
        response = requests.post(
            f"{base_url}/graphql",
            json={"query": graphql_query},
            headers=headers,
            timeout=5
        )
        print(f"  GraphQL: {response.status_code}")
        if response.status_code == 200:
            print(f"  Response: {response.text[:200]}")
    except:
        pass
    
    print("\n" + "=" * 80)
    print("SUMMARY: Run browser DevTools Network tab to identify API endpoints")
    print("Then we can call them directly from Python\n")


if __name__ == "__main__":
    find_api_endpoints()
