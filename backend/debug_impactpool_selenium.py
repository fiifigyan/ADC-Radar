"""Debug Impactpool with Selenium to see what's being rendered"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

def debug_impactpool_selenium():
    url = "https://www.impactpool.org/jobs"
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver = None
    try:
        # Create driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Load page
        print("Loading Impactpool with Selenium...")
        driver.get(url)
        
        print("Waiting for page to load (10 seconds)...")
        time.sleep(10)
        
        # Check for any article elements
        articles = driver.find_elements(By.TAG_NAME, "article")
        print(f"\nFound {len(articles)} <article> elements")
        
        # Check for job-related divs
        job_divs = driver.find_elements(By.CSS_SELECTOR, "[class*='job']")
        print(f"Found {len(job_divs)} elements with 'job' in class")
        
        # Get the HTML
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        print("\n=== HTML Structure Analysis ===")
        print(f"Total page size: {len(html)} bytes")
        
        # Check for h2, h3 tags
        h2_tags = soup.find_all('h2')
        h3_tags = soup.find_all('h3')
        print(f"Found {len(h2_tags)} <h2> tags")
        print(f"Found {len(h3_tags)} <h3> tags")
        
        if h2_tags:
            print("\nFirst 5 <h2> contents:")
            for h2 in h2_tags[:5]:
                text = h2.get_text(strip=True)[:80]
                print(f"  - {text}")
        
        if h3_tags:
            print("\nFirst 5 <h3> contents:")
            for h3 in h3_tags[:5]:
                text = h3.get_text(strip=True)[:80]
                print(f"  - {text}")
        
        # Check for any text that looks like job titles
        articles = soup.find_all('article')
        print(f"\nArticles found in HTML: {len(articles)}")
        if articles:
            print("First article HTML (first 500 chars):")
            print(articles[0].prettify()[:500])
        
        # Look for the main jobs container
        containers = soup.find_all(class_=lambda x: x and 'job' in x.lower())
        print(f"\nElements with 'job' in class: {len(containers)}")
        
        # Check page source for 'job' keyword
        job_mentions = html.count('job')
        print(f"\nKeyword 'job' appears {job_mentions} times in page")
        
        # Check if there's a script that loads jobs (API call)
        scripts = soup.find_all('script')
        print(f"\nTotal <script> tags: {len(scripts)}")
        
        for i, script in enumerate(scripts):
            if script.string and ('impactpool' in script.string.lower() or 'api' in script.string.lower() or 'jobs' in script.string.lower()):
                print(f"\nScript {i} excerpt (first 300 chars):")
                print(script.string[:300])
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    debug_impactpool_selenium()
