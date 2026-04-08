"""
Service to manage all scrapers and coordinate scraping operations
"""
import logging
from typing import List, Dict, Any
from datetime import datetime
from src.scrapers.devex_scraper import DevexScraper
from src.scrapers.impactpool_scraper import ImpactpoolScraper
from src.scrapers.undp_scraper import UndpScraper
from src.scrapers.worldbank_scraper import WorldBankScraper
from src.scrapers.developmentaid_scraper import DevelopmentaidScraper
from src.models.opportunity import Opportunity, SourcePlatform
from src.database.local_db import LocalDatabase

logger = logging.getLogger(__name__)

class ScraperService:
    """Manages all scrapers"""
    
    def __init__(self, db: LocalDatabase = None):
        self.db = db or LocalDatabase()
        self.scrapers = {
            SourcePlatform.DEVEX: DevexScraper(),
            SourcePlatform.IMPACTPOOL: ImpactpoolScraper(),
            SourcePlatform.UNDP: UndpScraper(),
            SourcePlatform.WORLD_BANK: WorldBankScraper(),
            SourcePlatform.DEVELOPMENT_AID: DevelopmentaidScraper(),
        }
        self.last_scrape_time = None
        self.scrape_results = {
            "total_scraped": 0,
            "total_saved": 0,
            "total_failed": 0,
            "last_run": None,
            "sources": {}
        }
    
    def scrape_all(self, max_results_per_source: int = 50) -> Dict[str, Any]:
        """Scrape from all configured sources"""
        logger.info("Starting scrape from all sources")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "sources": {},
            "summary": {
                "total_scraped": 0,
                "total_saved": 0,
                "total_failed": 0
            }
        }
        
        for source, scraper in self.scrapers.items():
            try:
                logger.info(f"Scraping from {source.value}")
                opportunities = scraper.scrape(max_results=max_results_per_source)
                
                saved = 0
                failed = 0
                for opp in opportunities:
                    try:
                        self.db.save_opportunity(opp)
                        saved += 1
                    except Exception as e:
                        logger.error(f"Failed to save opportunity: {e}")
                        failed += 1
                
                results["sources"][source.value] = {
                    "scraped": len(opportunities),
                    "saved": saved,
                    "failed": failed,
                    "status": "success"
                }
                
                results["summary"]["total_scraped"] += len(opportunities)
                results["summary"]["total_saved"] += saved
                results["summary"]["total_failed"] += failed
                
                logger.info(f"Scraped {len(opportunities)} from {source.value}, saved {saved}")
                
            except Exception as e:
                logger.error(f"Error scraping from {source.value}: {e}")
                results["sources"][source.value] = {
                    "scraped": 0,
                    "saved": 0,
                    "failed": 1,
                    "error": str(e),
                    "status": "failed"
                }
        
        self.last_scrape_time = datetime.now()
        self.scrape_results = results
        
        return results
    
    def scrape_source(self, source: SourcePlatform, max_results: int = 50) -> Dict[str, Any]:
        """Scrape from a specific source"""
        logger.info(f"Scraping from {source.value}")
        
        if source not in self.scrapers:
            return {
                "status": "error",
                "message": f"Source {source.value} not configured"
            }
        
        try:
            scraper = self.scrapers[source]
            opportunities = scraper.scrape(max_results=max_results)
            
            saved = 0
            failed_opps = []
            
            for opp in opportunities:
                try:
                    self.db.save_opportunity(opp)
                    saved += 1
                except Exception as e:
                    logger.error(f"Failed to save opportunity: {e}")
                    failed_opps.append({
                        "title": opp.title,
                        "error": str(e)
                    })
            
            return {
                "source": source.value,
                "scraped": len(opportunities),
                "saved": saved,
                "failed": len(failed_opps),
                "status": "success",
                "failed_opportunities": failed_opps if failed_opps else None,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scraping {source.value}: {e}")
            return {
                "source": source.value,
                "status": "error",
                "error": str(e)
            }
    
    def get_scrape_stats(self) -> Dict[str, Any]:
        """Get statistics about scraping"""
        opportunities = self.db.load_all_opportunities()
        
        by_source = {}
        for opp in opportunities:
            source = opp.get("source_platform", "Unknown")
            by_source[source] = by_source.get(source, 0) + 1
        
        return {
            "total_opportunities": len(opportunities),
            "by_source": by_source,
            "last_scrape": self.last_scrape_time.isoformat() if self.last_scrape_time else None,
            "available_sources": [s.value for s in self.scrapers.keys()]
        }
