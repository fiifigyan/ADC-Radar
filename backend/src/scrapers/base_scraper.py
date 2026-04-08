import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from src.models.opportunity import Opportunity, SourcePlatform

logger = logging.getLogger(__name__)

# Optional Selenium imports for JavaScript rendering
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logger.warning("Selenium not installed. JavaScript rendering will be unavailable.")

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
        self.logger = logger
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
    
    def fetch_page_with_selenium(self, url: str, wait_time: int = 25) -> Optional[str]:
        """Fetch HTML content using Selenium (handles JavaScript-rendered content)"""
        if not SELENIUM_AVAILABLE:
            logger.warning("Selenium not available. Falling back to requests.")
            return self.fetch_page(url)
        
        driver = None
        try:
            # Setup Chrome options
            chrome_options = ChromeOptions()
            chrome_options.add_argument("--headless")  # Run in background
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument(f"user-agent={self.session.headers.get('User-Agent')}")
            
            # Create driver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Load page
            logger.info(f"Loading {url} with Selenium (waiting {wait_time} seconds)...")
            driver.get(url)
            
            # Wait for dynamic content to load
            # Increased wait time to allow API calls to complete
            time.sleep(min(wait_time, 30))
            
            # Return rendered HTML
            html = driver.page_source
            logger.info(f"Successfully loaded {url} with Selenium")
            return html
            
        except Exception as e:
            logger.error(f"Failed to fetch {url} with Selenium: {e}")
            # Try fallback to regular requests
            return self.fetch_page(url)
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def parse_opportunities(self, html: str) -> List[ScrapedData]:
        """Parse opportunities from HTML - to be implemented by child classes"""
        raise NotImplementedError("Child classes must implement this method")
    
    def scrape(self, max_results: int = 50) -> List[Opportunity]:
        """Main scraping method using Selenium for JavaScript rendering"""
        logger.info(f"Starting scrape for {self.platform.value}")
        
        # Use Selenium to handle JavaScript-rendered content (10-second wait for jobs to load)
        html = self.fetch_page_with_selenium(self.base_url, wait_time=10)
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