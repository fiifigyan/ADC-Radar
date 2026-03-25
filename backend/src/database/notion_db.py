"""
Notion database integration
"""
import os
from typing import List, Dict, Any
from notion_client import Client
from notion_client.errors import APIResponseError
from src.models.opportunity import Opportunity, ContractType, Region, Priority, SourcePlatform

class NotionDatabase:
    """Notion database manager"""
    
    def __init__(self, api_key: str = None, database_id: str = None):
        self.api_key = api_key or os.getenv('NOTION_API_KEY')
        self.database_id = database_id or os.getenv('NOTION_DATABASE_ID')
        
        if not self.api_key or not self.database_id:
            raise ValueError("Notion API key and database ID are required")
        
        self.client = Client(auth=self.api_key)
    
    def opportunity_to_notion_properties(self, opportunity: Opportunity) -> Dict[str, Any]:
        """Convert Opportunity to Notion properties"""
        properties = {
            "Opportunity Title": {
                "title": [
                    {
                        "text": {
                            "content": opportunity.title[:2000]
                        }
                    }
                ]
            },
            "Organization": {
                "rich_text": [
                    {
                        "text": {
                            "content": opportunity.organization
                        }
                    }
                ]
            },
            "Source Platform": {
                "select": {
                    "name": opportunity.source_platform.value
                }
            },
            "Contract Type": {
                "select": {
                    "name": opportunity.contract_type.value
                }
            },
            "Roster Call": {
                "checkbox": opportunity.is_roster_call
            },
            "Country": {
                "multi_select": [{"name": country} for country in opportunity.countries]
            },
            "Region": {
                "multi_select": [{"name": region.value} for region in opportunity.regions]
            },
            "Primary Skill": {
                "multi_select": [{"name": skill} for skill in opportunity.primary_skills[:3]]
            },
            "Secondary Skills": {
                "multi_select": [{"name": skill} for skill in opportunity.secondary_skills[:5]]
            },
            "Relevance Score": {
                "number": opportunity.relevance_score
            },
            "Priority": {
                "select": {
                    "name": opportunity.priority.value
                }
            },
            "Deadline": {
                "date": {
                    "start": opportunity.deadline.isoformat() if opportunity.deadline else None,
                    "end": None
                }
            },
            "Original Link": {
                "url": opportunity.url
            },
            "AI Summary": {
                "rich_text": [
                    {
                        "text": {
                            "content": opportunity.ai_summary[:2000]
                        }
                    }
                ]
            },
            "Confidence Score": {
                "number": opportunity.confidence_score
            }
        }
        
        return properties
    
    def add_opportunity(self, opportunity: Opportunity) -> str:
        """Add opportunity to Notion database"""
        try:
            properties = self.opportunity_to_notion_properties(opportunity)
            
            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            
            return response["id"]
            
        except APIResponseError as e:
            print(f"Notion API error: {e}")
            raise
        except Exception as e:
            print(f"Error adding opportunity to Notion: {e}")
            raise
    
    def add_opportunities(self, opportunities: List[Opportunity]) -> List[str]:
        """Add multiple opportunities to Notion"""
        page_ids = []
        
        for opportunity in opportunities:
            try:
                page_id = self.add_opportunity(opportunity)
                page_ids.append(page_id)
            except Exception as e:
                print(f"Failed to add opportunity '{opportunity.title}': {e}")
                continue
        
        return page_ids
    
    def get_high_priority_opportunities(self) -> List[Dict]:
        """Get high priority opportunities from Notion"""
        try:
            response = self.client.databases.query(
                database_id=self.database_id,
                filter={
                    "property": "Priority",
                    "select": {
                        "equals": "High"
                    }
                },
                sorts=[
                    {
                        "property": "Relevance Score",
                        "direction": "descending"
                    }
                ]
            )
            
            return response["results"]
            
        except Exception as e:
            print(f"Error querying Notion: {e}")
            return []