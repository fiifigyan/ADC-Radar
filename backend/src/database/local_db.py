"""
Local JSON database for storing opportunities
"""
import json
import os
from typing import List, Dict, Any
from datetime import datetime
from src.models.opportunity import Opportunity

class LocalDatabase:
    """Local JSON-based database for opportunities"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.opportunities_file = os.path.join(data_dir, "opportunities.json")
        self.ensure_data_dir()
    
    def ensure_data_dir(self):
        """Create data directory if it doesn't exist"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create empty opportunities file if it doesn't exist
        if not os.path.exists(self.opportunities_file):
            with open(self.opportunities_file, 'w') as f:
                json.dump([], f)
    
    def save_opportunity(self, opportunity: Opportunity) -> str:
        """Save opportunity to local database"""
        opportunities = self.load_all_opportunities()
        
        # Check if opportunity already exists (by ID or title+organization)
        existing_ids = [opp.get('id') for opp in opportunities]
        if opportunity.id in existing_ids:
            # Update existing
            for i, opp in enumerate(opportunities):
                if opp.get('id') == opportunity.id:
                    opportunities[i] = opportunity.to_dict()
                    break
        else:
            # Add new
            opportunities.append(opportunity.to_dict())
        
        # Save to file
        with open(self.opportunities_file, 'w') as f:
            json.dump(opportunities, f, indent=2, default=str)
        
        return opportunity.id
    
    def save_opportunities(self, opportunities: List[Opportunity]):
        """Save multiple opportunities"""
        for opportunity in opportunities:
            self.save_opportunity(opportunity)
    
    def load_all_opportunities(self) -> List[Dict[str, Any]]:
        """Load all opportunities from database"""
        try:
            with open(self.opportunities_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def load_as_objects(self) -> List[Opportunity]:
        """Load opportunities as Opportunity objects"""
        data = self.load_all_opportunities()
        opportunities = []
        
        for item in data:
            try:
                opp = Opportunity.from_dict(item)
                opportunities.append(opp)
            except Exception as e:
                print(f"Error loading opportunity: {e}")
                continue
        
        return opportunities
    
    def get_this_week_opportunities(self) -> List[Opportunity]:
        """Get opportunities added this week"""
        all_opps = self.load_as_objects()
        this_week = []
        
        current_week = datetime.now().isocalendar()[1]
        
        for opp in all_opps:
            opp_week = opp.scraped_at.isocalendar()[1]
            if opp_week == current_week:
                this_week.append(opp)
        
        return this_week
    
    def get_high_priority(self) -> List[Opportunity]:
        """Get high priority opportunities"""
        all_opps = self.load_as_objects()
        return [opp for opp in all_opps if opp.priority.value == "High"]
    
    def get_by_skill(self, skill: str) -> List[Opportunity]:
        """Get opportunities by skill"""
        all_opps = self.load_as_objects()
        skill_lower = skill.lower()
        
        results = []
        for opp in all_opps:
            all_skills = [s.lower() for s in opp.primary_skills + opp.secondary_skills]
            if skill_lower in all_skills:
                results.append(opp)
        
        return results
    
    def delete_old_opportunities(self, days_old: int = 30):
        """Delete opportunities older than specified days"""
        all_opps = self.load_as_objects()
        cutoff_date = datetime.now() - datetime.timedelta(days=days_old)
        
        recent_opps = [opp for opp in all_opps if opp.scraped_at > cutoff_date]
        
        # Save only recent opportunities
        with open(self.opportunities_file, 'w') as f:
            json.dump([opp.to_dict() for opp in recent_opps], f, indent=2, default=str)
        
        return len(all_opps) - len(recent_opps)