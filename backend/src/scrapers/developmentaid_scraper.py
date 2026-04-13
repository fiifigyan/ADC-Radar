"""
DevelopmentAid.org scraper
"""
from bs4 import BeautifulSoup
from typing import List
from src.scrapers.base_scraper import BaseScraper, ScrapedData
from src.models.opportunity import SourcePlatform

class DevelopmentaidScraper(BaseScraper):
    """Scraper for DevelopmentAid.org opportunities"""
    
    def __init__(self):
        super().__init__(SourcePlatform.DEVELOPMENT_AID, "https://www.developmentaid.org/jobs")
    
    def parse_opportunities(self, html: str) -> List[ScrapedData]:
        """Parse DevelopmentAid job listings"""
        soup = BeautifulSoup(html, 'html.parser')
        opportunities = []
        
        # DevelopmentAid.org lists jobs as links - find all links that look like job postings
        all_links = soup.find_all('a', href=True)
        
        job_links = []
        for link in all_links:
            text = link.get_text(strip=True)
            href = link.get('href', '')
            
            # Filter for job/opportunity-related links
            # Exclude category pages, AMP versions, and special pages
            if (len(text) > 10 and len(text) < 250 and 
                ('job' in href.lower() or '/job/' in href.lower() or 
                 'position' in href.lower() or 'opportunity' in href.lower()) and
                not '/amp/' in href.lower() and  # Exclude AMP versions
                not '/jobs-in-' in href.lower() and  # Exclude country/region category pages
                not 'publish' in text.lower()):  # Exclude "Publish a Job" link
                job_links.append(link)
        
        seen_titles = set()
        for link in job_links[:50]:
            try:
                title = link.get_text(strip=True)
                
                # Skip duplicates and invalid entries
                if title in seen_titles or len(title) < 5:
                    continue
                
                seen_titles.add(title)
                
                # Extract URL
                url = link.get('href', '')
                if url and not url.startswith('http'):
                    url = f"https://www.developmentaid.org{url}"
                
                # Extract description from parent container
                description = title
                parent = link.parent
                for _ in range(3):  # Look up 3 levels
                    if parent and parent.name:
                        parent_text = parent.get_text(strip=True)
                        if len(parent_text) > len(title) + 20:
                            description = parent_text[:300]
                            break
                        parent = parent.parent
                
                opportunity = ScrapedData(
                    title=title,
                    organization="DevelopmentAid.org",
                    description=description,
                    url=url
                )
                
                opportunities.append(opportunity)
                
                if len(opportunities) >= 30:
                    break
                    
            except Exception as e:
                self.logger.error(f"Error parsing DevelopmentAid job: {e}")
                continue
        
        return opportunities
