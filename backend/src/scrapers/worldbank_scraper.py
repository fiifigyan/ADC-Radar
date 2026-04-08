"""
World Bank scraper
"""
from bs4 import BeautifulSoup
from typing import List
from src.scrapers.base_scraper import BaseScraper, ScrapedData
from src.models.opportunity import SourcePlatform

class WorldBankScraper(BaseScraper):
    """Scraper for World Bank job opportunities"""
    
    def __init__(self):
        super().__init__(SourcePlatform.WORLD_BANK, "https://www.worldbank.org/en/about/jobs/search")
    
    def parse_opportunities(self, html: str) -> List[ScrapedData]:
        """Parse World Bank job listings"""
        soup = BeautifulSoup(html, 'html.parser')
        opportunities = []
        
        # Find job postings - multiple selector strategies
        job_items = soup.select('.job-item, .position-card, .vacancy, .job-posting, li.job')
        
        for item in job_items[:30]:
            try:
                # Extract title - try multiple selectors
                title = "Untitled Opportunity"
                for selector in ['.position-title', 'h2', 'h3', '[class*="title"]', '[class*="name"]', 'a.job-link']:
                    title_elem = item.select_one(selector)
                    if title_elem:
                        extracted = self.clean_text(title_elem.get_text())
                        if extracted and len(extracted) > 3:
                            title = extracted
                            break
                
                # Extract organization - try multiple selectors
                organization = "World Bank"
                for selector in ['.organization', '.group', '.unit', '[class*="company"]', '[class*="org"]', '.employer']:
                    org_elem = item.select_one(selector)
                    if org_elem:
                        extracted = self.clean_text(org_elem.get_text())
                        if extracted and len(extracted) > 2:
                            organization = extracted
                            break
                
                # Extract description - try multiple selectors
                description = ""
                for selector in ['.job-description', '.summary', '.description', '[class*="desc"]', 'p']:
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
                        url = f"https://www.worldbank.org{url}" if url.startswith('/') else f"https://www.worldbank.org/{url}"
                
                # Extract deadline - try multiple selectors
                deadline = None
                for selector in ['.deadline', '.closing-date', '.application-deadline', '[class*="date"]']:
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
                self.logger.error(f"Error parsing World Bank job listing: {e}")
                continue
        
        return opportunities
