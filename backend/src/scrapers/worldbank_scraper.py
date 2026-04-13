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
        super().__init__(SourcePlatform.WORLD_BANK, "https://worldbankgroup.csod.com/ux/ats/careersite/1/home")
    
    def parse_opportunities(self, html: str) -> List[ScrapedData]:
        """Parse World Bank job listings from CSOD ATS platform"""
        soup = BeautifulSoup(html, 'html.parser')
        opportunities = []
        
        # World Bank uses CSOD ATS - job listings appear as links with job titles
        # Find all links that contain job postings
        all_links = soup.find_all('a', href=True)
        
        job_links = []
        for link in all_links:
            text = link.get_text(strip=True)
            href = link.get('href', '')
            
            # Filter for actual job links (not navigation/utility links)
            if (len(text) > 10 and len(text) < 200 and 
                ('job' in href.lower() or 'position' in text.lower() or 
                 'specialist' in text.lower() or 'manager' in text.lower() or 
                 'assistant' in text.lower() or 'officer' in text.lower())):
                job_links.append(link)
        
        # Process unique job listings (limit to 30)
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
                    url = f"https://worldbankgroup.csod.com{url}"
                
                # Look for associated metadata (location, deadline) near the link
                description = title
                parent = link.parent
                
                # Try to get additional info from parent div/li
                if parent:
                    parent_text = parent.get_text(strip=True)
                    if len(parent_text) > len(title):
                        description = parent_text[:300]
                
                opportunity = ScrapedData(
                    title=title,
                    organization="World Bank",
                    description=description,
                    url=url if url.startswith('http') else f"https://worldbankgroup.csod.com{url}"
                )
                
                opportunities.append(opportunity)
                
                if len(opportunities) >= 30:
                    break
                    
            except Exception as e:
                self.logger.error(f"Error parsing World Bank job: {e}")
                continue
        
        return opportunities

