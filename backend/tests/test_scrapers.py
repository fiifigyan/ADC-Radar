import pytest
from scrapers import scraper_factory
from utils.exceptions import ScraperException

class TestScraperFactory:
    def test_get_default_scraper(self):
        scraper = scraper_factory.get_scraper('default')
        assert scraper is not None
    
    def test_invalid_scraper_type(self):
        with pytest.raises(ScraperException):
            scraper_factory.get_scraper('invalid_type')

class TestScraper:
    @pytest.mark.asyncio
    async def test_fetch_returns_data(self):
        scraper = scraper_factory.get_scraper('default')
        result = await scraper.fetch()
        assert result is not None
        assert isinstance(result, (list, dict))
