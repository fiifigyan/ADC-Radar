"""
Scraper module for Africa Digital Consultancy Radar
"""

from src.scraper.base_scraper import BaseScraper, ScrapedData
from src.scraper.mock_scraper import MockScraper
from src.scraper.devex_scraper import DevexScraper

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