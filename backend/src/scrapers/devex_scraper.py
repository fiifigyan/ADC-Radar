"""
Devex.com scraper - Note: Requires proper HTML parsing based on actual Devex structure
"""
from bs4 import BeautifulSoup
from typing import List
import re
from src.scraper.base_scraper import BaseScraper, ScrapedData
from src.models.opportunity import SourcePlatform

class DevexScraper(BaseScraper):
    """Scraper for Devex.com opportunities"""
    
    def __init__(self):
        super().__init__(SourcePlatform.DEVEX, "https://www.devex.com/jobs")
    
    def parse_opportunities(self, html: str) -> List[ScrapedData]:
        """Parse Devex job listings"""
        soup = BeautifulSoup(html, 'html.parser')
        opportunities = []
        
        # Note: This is a template. Actual selectors need to be updated
        # based on Devex's current HTML structure
        
        # Example job listings (update based on actual HTML inspection)
        job_cards = soup.select('.job-card, .job-listing, [class*="job"]')
        
        for card in job_cards[:20]:  # Limit to 20 for demo
            try:
                # Extract title
                title_elem = card.select_one('.job-title, h3, h4')
                title = self.clean_text(title_elem.get_text()) if title_elem else "Untitled Opportunity"
                
                # Extract organization
                org_elem = card.select_one('.organization, .company, .employer')
                organization = self.clean_text(org_elem.get_text()) if org_elem else "Unknown Organization"
                
                # Extract description
                desc_elem = card.select_one('.description, .summary, .snippet')
                description = self.clean_text(desc_elem.get_text()) if desc_elem else ""
                
                # Extract URL
                link_elem = card.select_one('a[href]')
                url = link_elem['href'] if link_elem else ""
                if url and not url.startswith('http'):
                    url = f"https://www.devex.com{url}" if url.startswith('/') else f"https://www.devex.com/{url}"
                
                # Extract deadline (if available)
                deadline_elem = card.select_one('.deadline, .closing-date, .expires')
                deadline = self.clean_text(deadline_elem.get_text()) if deadline_elem else None
                
                opportunity = ScrapedData(
                    title=title,
                    organization=organization,
                    description=description,
                    url=url,
                    deadline=deadline,
                    raw_html=str(card)[:1000]  # Store first 1000 chars for debugging
                )
                
                opportunities.append(opportunity)
                
            except Exception as e:
                print(f"Error parsing job card: {e}")
                continue
        
        return opportunities