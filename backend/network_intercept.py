"""Advanced network interception for Impactpool using Selenium CDP"""
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.devtools.devtools_network_manager import DevToolsNetworkManager


def intercept_impactpool():
    """Intercept network calls to find API endpoints"""
    url = "https://www.impactpool.org/jobs"
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    # Enable CDP (Chrome DevTools Protocol)
    chrome_options.add_argument("--enable-automation=false")
    
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Execute CDP commands to monitor network
        print("Opening Impactpool and monitoring network traffic...")
        driver.execute_cdp_cmd('Network.enable', {})
        
        # Store network requests
        network_events = []
        
        def handle_network_response(response):
            """Capture network responses"""
            if 'job' in response['url'].lower() or 'api' in response['url'].lower():
                network_events.append({
                    'url': response['url'],
                    'status': response.get('status', 'unknown'),
                    'type': response.get('type', 'unknown')
                })
                print(f"Intercepted: {response['url'][:100]}")
        
        # Get the CDP session and listen to network events
        import json
        try:
            # Set up network event logging via CDP
            driver.execute_cdp_cmd('Network.setRequestInterception', {
                "patterns": [{"interceptionStage": "HeadersReceived"}]
            })
        except:
            pass
        
        driver.get(url)
        
        # Wait for network activity
        print("\nWaiting 15 seconds for API calls...")
        for i in range(15):
            print(f"  {i+1}/15...", end='', flush=True)
            time.sleep(1)
        print()
        
        # Try to extract from localStorage/sessionStorage
        print("\nChecking browser storage...")
        try:
            local_data = driver.execute_script("return window.localStorage;")
            print(f"localStorage keys: {list(local_data.keys()) if local_data else 'empty'}")
        except:
            pass
        
        # Check for API calls in page scripts
        print("\nSearching for API endpoints in page scripts...")
        scripts = driver.find_elements(By.TAG_NAME, "script")
        api_endpoints = set()
        
        for script in scripts:
            content = script.get_attribute("textContent")
            if content and len(content) > 0:
                # Look for common API patterns
                if 'api' in content.lower() or 'https://' in content:
                    # Extract URLs that might be API endpoints
                    import re
                    urls = re.findall(r'https://[^\s"\'<>]+', content)
                    for api_url in urls:
                        if 'api' in api_url.lower() or 'graphql' in api_url.lower():
                            api_endpoints.add(api_url)
                            print(f"  Found: {api_url[:100]}")
        
        # Check network requests made by the page
        print("\nExecuting script to find fetch calls...")
        response = driver.execute_script("""
            return window.__networkRequests || [];
        """)
        print(f"Network requests captured: {response}")
        
        # Try alternative: check page source for API patterns
        html = driver.page_source
        print(f"\nPage size: {len(html)} bytes")
        
        # Look for contentful assets or app data
        if 'contentful' in html.lower():
            print("✓ Site uses Contentful CMS!")
            # Extract Contentful API calls
            import re
            matches = re.findall(r'https://cdn\.contentful\.com/[^\s"\'<>]+', html)
            for match in matches[:5]:
                print(f"  Contentful endpoint: {match[:100]}")
        
        if 'www.impactpool.org/api' in html:
            print("✓ Found internal API references")
        
        # Check for fetch/XHR being made
        print("\nChecking for active XHR/fetch requests...")
        try:
            logs = driver.get_log('performance')
            print(f"Performance logs: {len(logs)} events")
            for log in logs[:5]:
                print(f"  - {log.get('message', '')[:100]}")
        except:
            pass
        
        return api_endpoints
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    endpoints = intercept_impactpool()
    print(f"\n\nFound {len(endpoints)} potential API endpoints:")
    for ep in endpoints:
        print(f"  - {ep}")
