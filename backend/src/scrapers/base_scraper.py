import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from src.models.opportunity import Opportunity, SourcePlatform

logger = logging.getLogger(__name__)

@dataclass
class ScrapedData:
    """Container for scraped opportunity data"""
    title: str
    organization: str
    description: str
    url: str
    deadline: Optional[str] = None
    posted_date: Optional[str] = None
    raw_html: Optional[str] = None

class BaseScraper:
    """Base class for all scrapers"""
    
    def __init__(self, platform: SourcePlatform, base_url: str):
        self.platform = platform
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch HTML content from URL"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None
    
    def parse_opportunities(self, html: str) -> List[ScrapedData]:
        """Parse opportunities from HTML - to be implemented by child classes"""
        raise NotImplementedError("Child classes must implement this method")
    
    def scrape(self, max_results: int = 50) -> List[Opportunity]:
        """Main scraping method"""
        logger.info(f"Starting scrape for {self.platform.value}")
        
        html = self.fetch_page(self.base_url)
        if not html:
            return []
        
        scraped_data_list = self.parse_opportunities(html)
        
        # Convert to Opportunity objects
        opportunities = []
        for scraped_data in scraped_data_list[:max_results]:
            opp = Opportunity(
                title=scraped_data.title,
                organization=scraped_data.organization,
                description=scraped_data.description,
                source_platform=self.platform,
                url=scraped_data.url
            )
            opportunities.append(opp)
        
        logger.info(f"Scraped {len(opportunities)} opportunities from {self.platform.value}")
        return opportunities
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove common noise
        noise = ['\n', '\t', '\r', '•', '·']
        for char in noise:
            text = text.replace(char, ' ')
        
        return text.strip()