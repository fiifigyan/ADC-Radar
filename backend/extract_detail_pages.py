"""Fetch job detail pages for clean data extraction"""
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import requests


def extract_jobs_from_detail_pages():
    """Extract jobs by fetching detail pages"""
    
    base_url = "https://www.impactpool.org/jobs"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = None
    try:
        print("Step 1: Getting job URLs from listing page...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(base_url)
        
        time.sleep(20)  # Wait for jobs to render
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract job URLs
        job_links = soup.find_all('a', href=re.compile(r'/jobs/\d+'))
        job_urls = []
        
        for link in job_links:
            href = link.get('href', '')
            if href.startswith('/jobs/'):
                job_urls.append(f"https://www.impactpool.org{href}")
        
        print(f"Found {len(job_urls)} job URLs")
        driver.quit()
        driver = None
        
        print("\nStep 2: Fetching detail pages...")
        print("=" * 80)
        
        jobs = []
        for i, job_url in enumerate(job_urls[:10], 1):  # Limit to 10 for speed
            try:
                print(f"{i}. Fetching {job_url.split('/')[-1]}...")
                
                # Fetch detail page
                response = requests.get(job_url, headers=headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract job data
                title = None
                organization = None
                location = None
                description = None
                deadline = None
                
                # Try common patterns
                # Title (usually in h1 or large heading)
                for h_tag in soup.find_all(['h1', 'h2', 'h3']):
                    text = h_tag.get_text(strip=True)
                    if len(text) > 10 and len(text) < 200:
                        title = text
                        break
                
                # Look for structured data
                # Organization often in bold after title
                for strong in soup.find_all('strong'):
                    text = strong.get_text(strip=True)
                    if any(keyword in text.lower() for keyword in ['organization', 'employer', 'by']):
                        next_text = strong.find_next_sibling()
                        if next_text:
                            organization = next_text.get_text(strip=True)
                            break
                
                # Try to find with specific patterns
                all_text = soup.get_text()
                
                # Look for patterns like "Organization: XX"
                org_match = re.search(r'(?:organization|employer|posted by):\s*([^\n]+)', all_text, re.I)
                if org_match:
                    organization = org_match.group(1).strip()[:100]
                
                # Location
                loc_match = re.search(r'(?:location|based in|workplace):\s*([^\n]+)', all_text, re.I)
                if loc_match:
                    location = loc_match.group(1).strip()[:100]
                
                # Deadline
                deadline_match = re.search(r'(?:deadline|closing date|apply by):\s*([^\n]+)', all_text, re.I)
                if deadline_match:
                    deadline = deadline_match.group(1).strip()[:100]
                
                # Description (first 500 chars of main content)
                p_tags = soup.find_all('p')
                for p in p_tags:
                    text = p.get_text(strip=True)
                    if len(text) > 100:
                        description = text[:500]
                        break
                
                # If we didn't find title, use page title
                if not title:
                    title_tag = soup.find('title')
                    if title_tag:
                        title = title_tag.get_text().split('-')[0].strip()
                
                if title and len(title) > 5:
                    jobs.append({
                        'title': title,
                        'organization': organization or 'Unknown Organization',
                        'location': location or 'Not specified',
                        'url': job_url,
                        'deadline': deadline,
                        'source': 'Impactpool'
                    })
                    
                    print(f"   ✓ {title}")
                    print(f"     Org: {organization or 'Unknown'}")
                    print(f"     Location: {location or 'Not specified'}")
                else:
                    print(f"   ✗ Could not extract title")
                
            except Exception as e:
                print(f"   Error: {str(e)[:80]}")
        
        print("=" * 80)
        print(f"\nExtracted {len(jobs)} jobs from detail pages\n")
        
        if jobs:
            print("Sample job data:")
            for job in jobs[:3]:
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


if __name__ == "__main__":
    jobs = extract_jobs_from_detail_pages()
    print(f"\nTotal: {len(jobs)} jobs")
