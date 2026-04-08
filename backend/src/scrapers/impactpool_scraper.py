"""
Impactpool.org scraper with advanced Selenium rendering and intelligent text parsing
"""
from bs4 import BeautifulSoup
from typing import List
import re
from src.scrapers.base_scraper import BaseScraper, ScrapedData
from src.models.opportunity import SourcePlatform
from src.utils.job_parser import JobTextParser


class ImpactpoolScraper(BaseScraper):
    """Scraper for Impactpool.org opportunities with Selenium and smart text parsing"""
    
    def __init__(self):
        super().__init__(SourcePlatform.IMPACTPOOL, "https://www.impactpool.org/jobs")
    
    def parse_opportunities(self, html: str) -> List[ScrapedData]:
        """Parse Impactpool job listings from rendered HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        opportunities = []
        parser = JobTextParser()
        
        # Extract job links from rendered page
        job_links = soup.find_all('a', href=re.compile(r'/jobs/\d+'))
        
        for link in job_links[:30]:
            try:
                href = link.get('href', '')
                full_text = link.get_text(strip=True)
                
                if not full_text or len(full_text) < 10:
                    continue
                
                # Use intelligent text parser to extract components
                parsed = parser.extract_components(full_text)
                title = parsed['title']
                organization = parsed['organization']
                location = parsed['location']
                
                if title == 'Untitled Opportunity' or len(title) < 5:
                    continue
                
                # Build URL
                url = f"https://www.impactpool.org{href}" if href.startswith('/') else href
                
                opportunity = ScrapedData(
                    title=title,
                    organization=organization,
                    description=f"Location: {location}" if location else "",
                    url=url,
                    deadline=None
                )
                
                opportunities.append(opportunity)
                
            except Exception as e:
                self.logger.error(f"Error parsing Impactpool job: {e}")
                continue
        
        return opportunities
