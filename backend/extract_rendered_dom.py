"""Simple approach: Wait for DOM to render, then extract job elements"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup


def extract_jobs_from_rendered_dom():
    """Wait for jobs to render in DOM, then extract"""
    
    url = "https://www.impactpool.org/jobs"
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("Loading Impactpool...")
        driver.get(url)
        
        print("Waiting for job elements to appear (60 seconds max)...")
        
        # Try multiple wait strategies
        job_selectors = [
            '[class*="job"]',
            '[class*="position"]', 
            '[class*="posting"]',
            'article',
            '[role="article"]',
            '.opportunity',
            'li',
        ]
        
        found_elements = False
        for selector in job_selectors:
            try:
                # Wait up to 30 seconds for elements matching this selector
                wait = WebDriverWait(driver, 30)
                elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
                
                if len(elements) > 5:  # If we found many elements
                    print(f"✓ Found {len(elements)} elements with selector: {selector}")
                    found_elements = True
                    break
            except:
                pass
        
        # Get current HTML and parse
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        print(f"\nAnalyzing rendered HTML ({len(html)} bytes)...")
        
        # Look for links that might be job listings
        all_links = soup.find_all('a', href=True)
        print(f"Total links on page: {len(all_links)}")
        
        job_links = []
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Filter for job-related links
            if any(keyword in href.lower() or keyword in text.lower() 
                   for keyword in ['job', 'position', 'opportunity', 'posting']):
                job_links.append({
                    'href': href,
                    'text': text[:100],
                    'link': link
                })
        
        print(f"Found {len(job_links)} potential job links")
        
        if job_links:
            print("\nJob links found:")
            for i, link in enumerate(job_links[:10]):
                print(f"  {i+1}. {link['text']}")
                print(f"     URL: {link['href'][:80]}")
        
        # Try to find article-like elements
        articles = soup.find_all('article')
        print(f"\nArticle elements: {len(articles)}")
        
        if articles:
            print("\nSample article content:")
            for i, article in enumerate(articles[:2]):
                text = article.get_text(strip=True)[:200]
                classes = article.get('class', [])
                print(f"  Article {i+1} ({', '.join(classes[:3])}):")
                print(f"    {text}...")
        
        # Look for divs with specific structures  
        all_divs = soup.find_all('div')
        
        # Find divs that contain h2, h3, or link+text combination
        structured_divs = []
        for div in all_divs:
            heading = div.find(['h2', 'h3', 'h4'])
            link = div.find('a')
            text = div.get_text(strip=True)
            
            if heading or (link and len(text) > 50 and len(text) < 500):
                structured_divs.append({
                    'heading': heading.get_text(strip=True)[:50] if heading else '',
                    'text': text[:150],
                    'div': div
                })
        
        print(f"\nStructured divs (potential job cards): {len(structured_divs)}")
        if structured_divs:
            print("\nSample job-like divs:")
            for i, div in enumerate(structured_divs[:5]):
                if div['heading']:
                    print(f"  {i+1}. {div['heading']}")
                else:
                    print(f"  {i+1}. {div['text'][:80]}")
        
        # Check for text nodes that might be job titles
        print("\nLooking for text patterns that match job titles...")
        all_text = soup.get_text()
        lines = [line.strip() for line in all_text.split('\n') if len(line.strip()) > 20 and len(line.strip()) < 200]
        
        # Filter for likely titles
        likely_titles = []
        title_keywords = ['developer', 'coordinator', 'manager', 'specialist', 'officer', 'analyst', 'consultant']
        for line in lines:
            if any(keyword in line.lower() for keyword in title_keywords):
                likely_titles.append(line)
        
        print(f"Found {len(likely_titles)} lines matching job title patterns")
        if likely_titles:
            print("  Sample titles:")
            for title in likely_titles[:5]:
                print(f"    - {title}")
        
        return structured_divs or job_links
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    results = extract_jobs_from_rendered_dom()
    print(f"\n\nTotal results extracted: {len(results) if results else 0}")
