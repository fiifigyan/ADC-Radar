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
        super().__init__(SourcePlatform.DEVELOPMENT_AID, "https://www.developmentaid.org")
    
    def parse_opportunities(self, html: str) -> List[ScrapedData]:
        """Parse DevelopmentAid job listings"""
        soup = BeautifulSoup(html, 'html.parser')
        opportunities = []
        
        # Find opportunities - multiple selector strategies
        opp_items = soup.select('.opportunity-item, .aid-opportunity, .posting, .job-item, li.opportunity')
        
        for item in opp_items[:30]:
            try:
                # Extract title - try multiple selectors
                title = "Untitled Opportunity"
                for selector in ['.opportunity-title', 'h2', 'h3', '[class*="title"]', '[class*="name"]', 'a.job-link']:
                    title_elem = item.select_one(selector)
                    if title_elem:
                        extracted = self.clean_text(title_elem.get_text())
                        if extracted and len(extracted) > 3:
                            title = extracted
                            break
                
                # Extract organization - try multiple selectors
                organization = "Unknown Organization"
                for selector in ['.organization', '.donor', '.implementing-partner', '[class*="company"]', '[class*="org"]', '.employer']:
                    org_elem = item.select_one(selector)
                    if org_elem:
                        extracted = self.clean_text(org_elem.get_text())
                        if extracted and len(extracted) > 2:
                            organization = extracted
                            break
                
                # Extract description - try multiple selectors
                description = ""
                for selector in ['.description', '.summary', '.content', '[class*="desc"]', 'p']:
                    desc_elem = item.select_one(selector)
                    if desc_elem:
                        extracted = self.clean_text(desc_elem.get_text())
                        if extracted and len(extracted) > 10:
                            description = extracted
                            break
                
                # Extract URL
                url = ""
                link_elem = item.select_one('a[href]')
                if link_elem:
                    url = link_elem.get('href', '')
                    if url and not url.startswith('http'):
                        url = f"https://www.developmentaid.org{url}" if url.startswith('/') else f"https://www.developmentaid.org/{url}"
                
                # Extract deadline - try multiple selectors
                deadline = None
                for selector in ['.deadline', '.closing-date', '.expires', '[class*="date"]']:
                    deadline_elem = item.select_one(selector)
                    if deadline_elem:
                        extracted = self.clean_text(deadline_elem.get_text())
                        if extracted:
                            deadline = extracted
                            break
                
                opportunity = ScrapedData(
                    title=title,
                    organization=organization,
                    description=description,
                    url=url,
                    deadline=deadline
                )
                
                opportunities.append(opportunity)
                
            except Exception as e:
                self.logger.error(f"Error parsing DevelopmentAid listing: {e}")
                continue
        
        return opportunities
