"""
UNDP (United Nations Development Programme) scraper
"""
from bs4 import BeautifulSoup
from typing import List
from src.scrapers.base_scraper import BaseScraper, ScrapedData
from src.models.opportunity import SourcePlatform

class UndpScraper(BaseScraper):
    """Scraper for UNDP job opportunities"""
    
    def __init__(self):
        super().__init__(SourcePlatform.UNDP, "https://jobs.undp.org")
    
    def parse_opportunities(self, html: str) -> List[ScrapedData]:
        """Parse UNDP job listings with flexible selectors"""
        soup = BeautifulSoup(html, 'html.parser')
        opportunities = []
        
        job_listings = soup.select(
            '.vacancy-item, .job-posting, .vacancy, [class*="vacancy"], '
            '[class*="opportunity"], [class*="posting"], '
            'div[role="article"], article'
        )
        
        for item in job_listings[:30]:
            try:
                # Extract title - flexible approach
                title = None
                for selector in ['h2', 'h3', '[class*="title"]', '[class*="name"]', 'a.job-link']:
                    title_elem = item.select_one(selector)
                    if title_elem:
                        extracted = self.clean_text(title_elem.get_text())
                        if extracted and len(extracted) > 3:
                            title = extracted
                            break
                
                if not title:
                    title = "Untitled Opportunity"
                
                # Extract organization - flexible approach
                organization = None
                for selector in ['[class*="office"]', '[class*="org"]', '[class*="employer"]', '.entity', 'strong']:
                    org_elem = item.select_one(selector)
                    if org_elem:
                        extracted = self.clean_text(org_elem.get_text())
                        if extracted and len(extracted) > 2 and extracted.lower() not in ['home', 'n/a']:
                            organization = extracted
                            break
                
                if not organization:
                    organization = "UNDP"
                
                # Extract description
                description = ""
                for selector in ['[class*="desc"]', '[class*="summary"]', '.content', 'p']:
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
                        url = f"https://jobs.undp.org{url}" if url.startswith('/') else f"https://jobs.undp.org/{url}"
                
                # Extract deadline
                deadline = None
                for selector in ['[class*="deadline"]', '[class*="closing"]', '[class*="expires"]', 'time']:
                    deadline_elem = item.select_one(selector)
                    if deadline_elem:
                        deadline = self.clean_text(deadline_elem.get_text())
                        if deadline:
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
                self.logger.error(f"Error parsing UNDP job listing: {e}")
                continue
        
        return opportunities
