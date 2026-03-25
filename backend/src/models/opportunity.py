from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

class ContractType(Enum):
    INDIVIDUAL_CONSULTANCY = "Individual Consultancy"
    ICA = "ICA"
    SHORT_TERM_EXPERT = "Short-term Expert"
    ROSTER = "Roster"
    OTHER = "Other"

class Region(Enum):
    WEST_AFRICA = "West Africa"
    EAST_AFRICA = "East Africa"
    SOUTHERN_AFRICA = "Southern Africa"
    CENTRAL_AFRICA = "Central Africa"
    NORTH_AFRICA = "North Africa"
    PAN_AFRICAN = "Pan-African"
    GLOBAL_AFRICA_FOCUS = "Global w/ Africa focus"

class Priority(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class SourcePlatform(Enum):
    DEVEX = "Devex"
    IMPACTPOOL = "Impactpool"
    UNDP = "UNDP"
    WORLD_BANK = "World Bank"
    DEVELOPMENT_AID = "DevelopmentAid"
    MOCK = "Mock Data"

@dataclass
class Opportunity:
    """Data model for consultancy opportunities"""
    
    # Basic Information
    id: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d%H%M%S%f"))
    title: str = ""
    organization: str = ""
    description: str = ""
    source_platform: SourcePlatform = SourcePlatform.MOCK
    
    # Contract Details
    contract_type: ContractType = ContractType.OTHER
    is_roster_call: bool = False
    deadline: Optional[datetime] = None
    posted_date: datetime = field(default_factory=datetime.now)
    
    # Geography
    countries: List[str] = field(default_factory=list)
    regions: List[Region] = field(default_factory=list)
    
    # Skills
    primary_skills: List[str] = field(default_factory=list)
    secondary_skills: List[str] = field(default_factory=list)
    
    # AI Analysis
    relevance_score: int = 0
    priority: Priority = Priority.LOW
    ai_summary: str = ""
    confidence_score: int = 0
    
    # Links
    url: str = ""
    application_url: str = ""
    
    # Metadata
    scraped_at: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "title": self.title,
            "organization": self.organization,
            "description": self.description[:500] if self.description else "",
            "source_platform": self.source_platform.value,
            "contract_type": self.contract_type.value,
            "is_roster_call": self.is_roster_call,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "posted_date": self.posted_date.isoformat(),
            "countries": self.countries,
            "regions": [region.value for region in self.regions],
            "primary_skills": self.primary_skills,
            "secondary_skills": self.secondary_skills,
            "relevance_score": self.relevance_score,
            "priority": self.priority.value,
            "ai_summary": self.ai_summary,
            "confidence_score": self.confidence_score,
            "url": self.url,
            "application_url": self.application_url,
            "scraped_at": self.scraped_at.isoformat(),
            "processed_at": self.processed_at.isoformat() if self.processed_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Opportunity':
        """Create Opportunity from dictionary"""
        opp = cls()
        opp.id = data.get('id', opp.id)
        opp.title = data.get('title', '')
        opp.organization = data.get('organization', '')
        opp.description = data.get('description', '')
        
        # Set enums from strings
        source_str = data.get('source_platform', 'MOCK')
        opp.source_platform = SourcePlatform[source_str.replace(' ', '_').upper()]
        
        contract_str = data.get('contract_type', 'Other')
        opp.contract_type = ContractType(contract_str)
        
        priority_str = data.get('priority', 'Low')
        opp.priority = Priority(priority_str)
        
        # Set lists
        opp.countries = data.get('countries', [])
        opp.primary_skills = data.get('primary_skills', [])
        opp.secondary_skills = data.get('secondary_skills', [])
        
        # Set regions
        region_strings = data.get('regions', [])
        opp.regions = [Region(region_str) for region_str in region_strings if region_str]
        
        # Set dates
        if data.get('deadline'):
            opp.deadline = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00'))
        
        if data.get('posted_date'):
            opp.posted_date = datetime.fromisoformat(data['posted_date'].replace('Z', '+00:00'))
        
        # Set other fields
        opp.relevance_score = data.get('relevance_score', 0)
        opp.ai_summary = data.get('ai_summary', '')
        opp.confidence_score = data.get('confidence_score', 0)
        opp.url = data.get('url', '')
        opp.application_url = data.get('application_url', '')
        opp.is_roster_call = data.get('is_roster_call', False)
        
        return opp