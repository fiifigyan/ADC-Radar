"""
Weekly insights summarizer
"""
import json
import logging
from typing import List, Dict, Any
from openai import OpenAI
from src.models.opportunity import Opportunity

logger = logging.getLogger(__name__)

class WeeklySummarizer:
    """Generates weekly insights from opportunities"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def generate_insights(self, opportunities: List[Opportunity]) -> Dict[str, Any]:
        """Generate weekly insights from opportunities"""
        try:
            # Prepare data for AI
            opportunities_data = [opp.to_dict() for opp in opportunities]
            
            # Limit to reasonable size
            if len(opportunities_data) > 50:
                opportunities_data = opportunities_data[:50]
            
            from config.prompts import WEEKLY_INSIGHTS_PROMPT
            
            prompt = WEEKLY_INSIGHTS_PROMPT.format(
                opportunities_json=json.dumps(opportunities_data, indent=2)
            )
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert analyst for development consultancy markets in Africa."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            # Parse response
            result_text = response.choices[0].message.content
            result_text = result_text.replace('```json', '').replace('```', '').strip()
            
            insights = json.loads(result_text)
            
            # Add basic statistics
            insights['total_opportunities'] = len(opportunities)
            insights['high_priority_count'] = sum(1 for opp in opportunities if opp.priority.value == "High")
            insights['medium_priority_count'] = sum(1 for opp in opportunities if opp.priority.value == "Medium")
            insights['low_priority_count'] = sum(1 for opp in opportunities if opp.priority.value == "Low")
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")
            
            # Return basic insights without AI
            return self._generate_basic_insights(opportunities)
    
    def _generate_basic_insights(self, opportunities: List[Opportunity]) -> Dict[str, Any]:
        """Generate basic insights without AI (fallback)"""
        if not opportunities:
            return {
                "most_requested_skills": [],
                "most_active_organizations": [],
                "active_regions": [],
                "trends": ["No opportunities found this week"],
                "recommendations": ["Check back next week for new opportunities"],
                "total_opportunities": 0,
                "high_priority_count": 0,
                "medium_priority_count": 0,
                "low_priority_count": 0
            }
        
        # Count skills
        skill_count = {}
        for opp in opportunities:
            for skill in opp.primary_skills + opp.secondary_skills:
                skill_count[skill] = skill_count.get(skill, 0) + 1
        
        # Count organizations
        org_count = {}
        for opp in opportunities:
            org_count[opp.organization] = org_count.get(opp.organization, 0) + 1
        
        # Count regions
        region_count = {}
        for opp in opportunities:
            for region in opp.regions:
                region_name = region.value
                region_count[region_name] = region_count.get(region_name, 0) + 1
        
        return {
            "most_requested_skills": [
                {"skill": skill, "count": count}
                for skill, count in sorted(skill_count.items(), key=lambda x: x[1], reverse=True)[:5]
            ],
            "most_active_organizations": [
                {"organization": org, "count": count}
                for org, count in sorted(org_count.items(), key=lambda x: x[1], reverse=True)[:5]
            ],
            "active_regions": [
                {"region": region, "count": count}
                for region, count in sorted(region_count.items(), key=lambda x: x[1], reverse=True)[:5]
            ],
            "trends": [
                f"Found {len(opportunities)} opportunities this week",
                f"{sum(1 for opp in opportunities if opp.priority.value == 'High')} high priority opportunities",
                f"Top skill: {max(skill_count.items(), key=lambda x: x[1])[0] if skill_count else 'None'}",
                f"Most active organization: {max(org_count.items(), key=lambda x: x[1])[0] if org_count else 'None'}",
                f"Deadlines approaching: {sum(1 for opp in opportunities if opp.deadline and (opp.deadline - opp.scraped_at).days < 7)}"
            ],
            "recommendations": [
                "Focus on high-priority opportunities first",
                "Update your skills based on demand",
                "Network with active organizations"
            ],
            "total_opportunities": len(opportunities),
            "high_priority_count": sum(1 for opp in opportunities if opp.priority.value == "High"),
            "medium_priority_count": sum(1 for opp in opportunities if opp.priority.value == "Medium"),
            "low_priority_count": sum(1 for opp in opportunities if opp.priority.value == "Low")
        }