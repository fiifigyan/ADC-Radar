"""
Scraper module for Africa Digital Consultancy Radar
"""

from src.scrapers.base_scraper import BaseScraper, ScrapedData
from src.scrapers.devex_scraper import DevexScraper
from src.scrapers.impactpool_scraper import ImpactpoolScraper
from src.scrapers.undp_scraper import UndpScraper
from src.scrapers.worldbank_scraper import WorldBankScraper
from src.scrapers.developmentaid_scraper import DevelopmentaidScraper

__all__ = [
    'BaseScraper',
    'ScrapedData',
    'MockScraper',
    'DevexScraper',
    'ScraperFactory'
]

class ScraperFactory:
    """Factory to create appropriate scrapers"""
    
    @staticmethod
    def create_scraper(platform: str):
        """
        Create scraper instance based on platform
        
        Args:
            platform: Platform name ('devex', 'mock', etc.)
        
        Returns:
            Scraper instance
        """
        scrapers = {
            'devex': DevexScraper,
            'mock': MockScraper,
            # Add more scrapers here as they're implemented
        }
        
        scraper_class = scrapers.get(platform.lower())
        if scraper_class:
            return scraper_class()
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    
    @staticmethod
    def get_available_scrapers():
        """Get list of available scraper platforms"""
        return ['devex', 'mock']