"""Advanced Selenium script with JavaScript fetch interception"""
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup


def intercept_with_js():
    """Use JavaScript to intercept fetch calls and extract job data"""
    
    url = "https://www.impactpool.org/jobs"
    
    # Setup Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    # Disable headless detection
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("1. Injecting fetch interceptor...")
        
        # JavaScript to intercept all fetch calls
        intercept_script = """
        window.__interceptedRequests = [];
        window.__interceptedResponses = {};
        
        // Intercept fetch
        const originalFetch = window.fetch;
        window.fetch = function(...args) {
            const request = args[0];
            console.log("Fetch called:", request);
            
            return originalFetch.apply(this, args)
                .then(response => {
                    const clonedResponse = response.clone();
                    clonedResponse.json().then(data => {
                        if (typeof request === 'string') {
                            window.__interceptedRequests.push({
                                url: request,
                                method: args[1]?.method || 'GET',
                                data: data
                            });
                        }
                    }).catch(() => {});
                    return response;
                });
        };
        
        // Intercept XMLHttpRequest
        const originalXHR = XMLHttpRequest.prototype.open;
        XMLHttpRequest.prototype.open = function(method, url, ...rest) {
            this.__url = url;
            this.__method = method;
            return originalXHR.apply(this, [method, url, ...rest]);
        };
        
        const originalSend = XMLHttpRequest.prototype.send;
        XMLHttpRequest.prototype.send = function(...args) {
            const xhr = this;
            const originalOnload = this.onload;
            
            this.onload = function() {
                try {
                    const data = JSON.parse(xhr.responseText);
                    window.__interceptedRequests.push({
                        url: xhr.__url,
                        method: xhr.__method,
                        data: data
                    });
                } catch(e) {}
                if (originalOnload) originalOnload.apply(this, arguments);
            };
            
            return originalSend.apply(this, args);
        };
        
        console.log("Interception ready");
        return "OK";
        """
        
        driver.execute_script(intercept_script)
        print("  ✓ Interceptor injected")
        
        print("\n2. Loading page and waiting for API calls...")
        driver.get(url)
        
        # Wait and check for intercepted requests
        for wait_sec in range(20):
            time.sleep(1)
            print(f"  Waiting... {wait_sec+1}/20 seconds", end='\r')
            
            intercepted = driver.execute_script("return window.__interceptedRequests;")
            if intercepted:
                print(f"\n  ✓ Captured {len(intercepted)} requests!")
                break
        else:
            print("\n  No requests captured in 20 seconds")
        
        # Get all intercepted data
        intercepted = driver.execute_script("return window.__interceptedRequests;")
        print(f"\n3. Extracting intercepted data ({len(intercepted)} requests):")
        print("-" * 80)
        
        job_data = []
        for i, req in enumerate(intercepted):
            url_str = req.get('url', 'unknown')[:80]
            print(f"\n  Request {i+1}: {url_str}")
            
            # Check if this looks like data we want
            data = req.get('data', {})
            
            if isinstance(data, dict):
                print(f"    Keys: {list(data.keys())[:5]}")
                
                # Look for job listings
                for key in data:
                    if 'job' in key.lower() or 'position' in key.lower() or 'opportunity' in key.lower():
                        items = data[key]
                        if isinstance(items, list):
                            print(f"    ✓ Found {len(items)} items under '{key}'")
                            job_data.extend(items)
                    elif key in ['data', 'items', 'results']:
                        items = data[key]
                        if isinstance(items, list) and len(items) > 0:
                            print(f"    ✓ Possible job data under '{key}': {len(items)} items")
                            # Sample first item
                            first = items[0]
                            if isinstance(first, dict):
                                print(f"      Sample: {json.dumps(first, default=str)[:200]}")
                                job_data.extend(items)
            
            elif isinstance(data, list):
                print(f"    Array with {len(data)} items")
                if len(data) > 0 and isinstance(data[0], dict):
                    job_data.extend(data)
        
        if job_data:
            print(f"\n4. Extracted {len(job_data)} potential job records!")
            print("-" * 80)
            
            # Display sample
            for idx, item in enumerate(job_data[:3]):
                print(f"\n  Item {idx+1}:")
                if isinstance(item, dict):
                    for key in list(item.keys())[:5]:
                        val = str(item[key])[:60]
                        print(f"    {key}: {val}")
            
            return job_data
        else:
            print("\n4. No job data found in network responses")
        
        # Fallback: check rendered DOM after waiting
        print("\n5. Checking rendered DOM...")
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for any text-heavy elements that might be job titles
        articles = soup.find_all('article')
        divs_with_text = soup.find_all('div', class_=lambda x: x and any(keyword in str(x).lower() for keyword in ['job', 'position', 'title']))
        
        print(f"  Found {len(articles)} articles, {len(divs_with_text)} divs with job-related classes")
        
        if articles:
            print(f"\n  First article text (first 300 chars):")
            print(f"  {articles[0].get_text(strip=True)[:300]}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()


def test_all_sites():
    """Test interception on all job sites"""
    sites = {
        'Impactpool': 'https://www.impactpool.org/jobs',
        'Devex': 'https://www.devex.com/jobs/search',
        'UNDP': 'https://jobs.undp.org',
        'World Bank': 'https://www.worldbank.org/en/about/jobs/search',
        'DevelopmentAid': 'https://www.developmentaid.org',
    }
    
    print("Starting interception for all sites...\n")
    intercept_with_js()


if __name__ == "__main__":
    intercept_with_js()
