"""Smart parser for rendered Impactpool job data"""
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup


def parse_impactpool_jobs():
    """Load Impactpool and smartly parse job data from rendered DOM"""
    
    url = "https://www.impactpool.org/jobs"
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0")
    
    driver = None
    try:
        print("Step 1: Loading Impactpool with Selenium...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)
        
        # Wait for page to fully render
        print("Step 2: Waiting for jobs to render (30 seconds)...")
        time.sleep(30)
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        print("Step 3: Parsing job data from rendered HTML...")
        print("=" * 80)
        
        jobs = []
        
        # Find all job links
        job_links = soup.find_all('a', href=re.compile(r'/jobs/\d+'))
        print(f"Found {len(job_links)} job links\n")
        
        for i, link in enumerate(job_links[:30]):  # Limit to 30 for testing
            try:
                href = link.get('href', '')
                
                # Get full text of the link (title, org, location combined)
                full_text = link.get_text(strip=True)
                
                if not full_text or len(full_text) < 10:
                    continue
                
                print(f"{i+1}. Raw text: {full_text[:100]}")
                
                # Try to parse: Usually format is "Title Organization Location"
                # Parse by patterns
                lines = full_text.split('\n')
                
                title = ''
                organization = ''
                location = ''
                
                # First non-empty line is usually the title
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 5:
                        if not title:
                            title = line
                        elif not organization:
                            organization = line
                        elif not location:
                            location = line
                        if title and organization and location:
                            break
                
                # Clean up extracted data
                title = title.strip()
                organization = organization.strip()
                location = location.strip()
                
                # Filter out common noise patterns
                noise_patterns = [
                    'level not specified',
                    'contractors',
                    'consultancy',
                    'temporary appointment',
                    'locally recruited',
                ]
                
                if any(noise in title.lower() for noise in noise_patterns):
                    title = ''
                
                # Extract better organization if possible
                # Common org prefixes to look for
                for line in lines[1:]:
                    line = line.strip()
                    if any(c.isupper() for c in line) and len(line) > 3:
                        if line not in title:
                            organization = line
                            break
                
                if title and len(title) > 3:
                    job_url = f"https://www.impactpool.org{href}" if href.startswith('/') else href
                    
                    jobs.append({
                        'title': title,
                        'organization': organization or 'Unknown Organization',
                        'location': location,
                        'url': job_url,
                        'source': 'Impactpool'
                    })
                    
                    print(f"   ✓ Title: {title}")
                    print(f"     Org: {organization}")
                    print(f"     Location: {location}")
                
            except Exception as e:
                print(f"   Error parsing: {e}")
            
            print()
        
        print("=" * 80)
        print(f"\nSuccessfully parsed {len(jobs)} jobs!\n")
        
        # Display summary
        if jobs:
            print("Sample jobs:")
            for job in jobs[:5]:
                print(f"\n  Title: {job['title']}")
                print(f"  Organization: {job['organization']}")
                print(f"  Location: {job['location']}")
                print(f"  URL: {job['url']}")
        
        return jobs
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()


def parse_other_sites():
    """Test parsing on other job sites"""
    sites = {
        'Devex': 'https://www.devex.com/jobs/search',
        'UNDP': 'https://jobs.undp.org',
        'World Bank': 'https://www.worldbank.org/en/about/jobs/search', 
        'DevelopmentAid': 'https://www.developmentaid.org',
    }
    
    for site_name, site_url in sites.items():
        print(f"\n\nTesting {site_name}...")
        print("=" * 80)
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            driver.get(site_url)
            time.sleep(.15)
            
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Look for job links
            job_links = soup.find_all('a', href=re.compile(r'(job|position|opportunity)', re.I))
            print(f"  Found {len(job_links)} job-related links")
            
            # Check for rendered content
            text_content = soup.get_text()
            job_mentions = len(re.findall(r'\b(job|position|opportunity)\b', text_content, re.I))
            print(f"  Job-related mentions: {job_mentions}")
            
            driver.quit()
            
        except Exception as e:
            print(f"  Error: {str(e)[:100]}")


if __name__ == "__main__":
    jobs = parse_impactpool_jobs()
    print(f"\n\nTotal jobs extracted: {len(jobs)}")
