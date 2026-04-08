"""Debug script to inspect Impactpool HTML structure"""
import requests
from bs4 import BeautifulSoup

def debug_impactpool():
    url = "https://www.impactpool.org/jobs"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print("=" * 80)
        print("IMPACTPOOL SCRAPING DEBUG")
        print("=" * 80)
        
        # Check common job card selectors
        selectors_to_test = [
            '.job-card',
            '.opportunity-card',
            '[class*="job"]',
            '[class*="opportunity"]',
            'div[role="article"]',
            'article',
            'li[data-job]',
            '.position',
            '.vacancy',
            '[class*="listing"]',
            'tr',
            'div.item',
        ]
        
        print("\n1. Testing CSS selectors for job cards:")
        print("-" * 80)
        for selector in selectors_to_test:
            elements = soup.select(selector)
            print(f"  {selector:<30} -> Found {len(elements)} elements")
        
        # Find all divs and check their classes
        print("\n2. Common div classes on page:")
        print("-" * 80)
        divs = soup.find_all('div', limit=100)
        classes_found = {}
        for div in divs:
            if div.get('class'):
                class_str = ' '.join(div.get('class'))
                if 'job' in class_str.lower() or 'opp' in class_str.lower() or 'position' in class_str.lower():
                    count = classes_found.get(class_str, 0)
                    classes_found[class_str] = count + 1
        
        for class_str, count in sorted(classes_found.items(), key=lambda x: x[1], reverse=True)[:20]:
            print(f"  {class_str:<50} x{count}")
        
        # Check for h2, h3 tags (likely job titles)
        print("\n3. Heading tags (likely job titles):")
        print("-" * 80)
        h2_count = len(soup.find_all('h2'))
        h3_count = len(soup.find_all('h3'))
        print(f"  <h2> tags found: {h2_count}")
        print(f"  <h3> tags found: {h3_count}")
        
        if h2_count > 0:
            print("\n  First 5 <h2> contents:")
            for h2 in soup.find_all('h2')[:5]:
                text = h2.get_text(strip=True)[:80]
                print(f"    - {text}")
        
        # Check for links that might be job links
        print("\n4. Sample links on page:")
        print("-" * 80)
        links = soup.find_all('a', href=True, limit=20)
        for i, link in enumerate(links[:10], 1):
            href = link.get('href', '')[:60]
            text = link.get_text(strip=True)[:60]
            print(f"  {i}. href: {href}")
            print(f"     text: {text}")
        
        # Check page structure
        print("\n5. Page structure check:")
        print("-" * 80)
        print(f"  Total page size: {len(response.text)} bytes")
        print(f"  Total <p> tags: {len(soup.find_all('p'))}")
        print(f"  Total <a> tags: {len(soup.find_all('a'))}")
        print(f"  Total <span> tags: {len(soup.find_all('span'))}")
        
    except requests.RequestException as e:
        print(f"Error fetching Impactpool: {e}")
        print("Note: Website might require special headers or JavaScript rendering")

if __name__ == "__main__":
    debug_impactpool()
