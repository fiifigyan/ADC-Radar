"""
Mock scraper for testing without real web scraping
"""
import json
import random
from datetime import datetime, timedelta
from typing import List
from src.scraper.base_scraper import BaseScraper, ScrapedData
from src.models.opportunity import Opportunity, SourcePlatform

class MockScraper(BaseScraper):
    """Mock scraper that generates sample data for testing"""
    
    def __init__(self):
        super().__init__(SourcePlatform.MOCK, "mock://data")
        
        # Sample data
        self.sample_titles = [
            "Digital Transformation Consultant - West Africa",
            "Data Analyst for Health Information Systems",
            "ICT Policy Expert - ECOWAS Region",
            "AI/Machine Learning Consultant for Agriculture",
            "Digital Trade Specialist - AfCFTA",
            "MIS Dashboard Developer - Remote",
            "Cybersecurity Expert - African Development Bank",
            "Blockchain Consultant for Financial Inclusion",
            "E-Government Specialist - Kenya",
            "Data Visualization Expert - Nigeria"
        ]
        
        self.sample_organizations = [
            "UNDP", "World Bank", "African Development Bank",
            "UNOPS", "GIZ", "DFID", "USAID",
            "Bill & Melinda Gates Foundation",
            "Mastercard Foundation", "African Union"
        ]
        
        self.sample_descriptions = [
            "Seeking an expert in digital transformation to support government initiatives in West Africa.",
            "Data analyst needed to develop health information systems across multiple African countries.",
            "ICT policy expert required to advise on regional digital integration policies.",
            "AI consultant to implement machine learning solutions for agricultural productivity.",
            "Digital trade specialist to support implementation of the African Continental Free Trade Area.",
            "Developer needed to create management information system dashboards for monitoring and evaluation.",
            "Cybersecurity expert to strengthen digital infrastructure protection across Africa.",
            "Blockchain consultant to develop financial inclusion solutions for underserved populations.",
            "E-government specialist to digitize public services in East African countries.",
            "Data visualization expert to create interactive dashboards for development indicators."
        ]
    
    def scrape(self, max_results: int = 10) -> List[Opportunity]:
        """Generate mock opportunities"""
        opportunities = []
        
        for i in range(min(max_results, 10)):
            # Random deadline (1-60 days from now)
            deadline = datetime.now() + timedelta(days=random.randint(1, 60))
            
            opp = Opportunity(
                title=random.choice(self.sample_titles),
                organization=random.choice(self.sample_organizations),
                description=random.choice(self.sample_descriptions),
                source_platform=SourcePlatform.MOCK,
                url=f"https://example.com/opportunity/{i}",
                deadline=deadline,
                posted_date=datetime.now() - timedelta(days=random.randint(0, 7))
            )
            
            opportunities.append(opp)
        
        return opportunities
    
    def parse_opportunities(self, html: str) -> List[ScrapedData]:
        """Mock implementation - not used"""
        return []