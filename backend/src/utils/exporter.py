"""
Export opportunities to various formats
"""
import csv
import json
import pandas as pd
from typing import List
from datetime import datetime
from src.models.opportunity import Opportunity

class Exporter:
    """Export opportunities to different formats"""
    
    @staticmethod
    def to_json(opportunities: List[Opportunity], filename: str = None):
        """Export opportunities to JSON file"""
        data = [opp.to_dict() for opp in opportunities]
        
        if filename:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        
        return json.dumps(data, indent=2, default=str)
    
    @staticmethod
    def to_csv(opportunities: List[Opportunity], filename: str = None):
        """Export opportunities to CSV file"""
        if not opportunities:
            return ""
        
        # Prepare data
        data = []
        for opp in opportunities:
            row = opp.to_dict()
            # Flatten lists
            row['countries'] = ', '.join(row['countries'])
            row['regions'] = ', '.join(row['regions'])
            row['primary_skills'] = ', '.join(row['primary_skills'])
            row['secondary_skills'] = ', '.join(row['secondary_skills'])
            data.append(row)
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        if filename:
            df.to_csv(filename, index=False, encoding='utf-8')
        
        return df.to_csv(index=False)
    
    @staticmethod
    def to_excel(opportunities: List[Opportunity], filename: str = None):
        """Export opportunities to Excel file"""
        if not opportunities:
            return None
        
        # Prepare data
        data = []
        for opp in opportunities:
            row = opp.to_dict()
            # Flatten lists
            row['countries'] = ', '.join(row['countries'])
            row['regions'] = ', '.join(row['regions'])
            row['primary_skills'] = ', '.join(row['primary_skills'])
            row['secondary_skills'] = ', '.join(row['secondary_skills'])
            data.append(row)
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        if filename:
            df.to_excel(filename, index=False)
        
        return df
    
    @staticmethod
    def to_markdown(opportunities: List[Opportunity]) -> str:
        """Export opportunities to Markdown format"""
        if not opportunities:
            return "# No opportunities found"
        
        markdown = f"# Africa Digital Consultancy Radar\n"
        markdown += f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        
        # Group by priority
        high_priority = [opp for opp in opportunities if opp.priority.value == "High"]
        medium_priority = [opp for opp in opportunities if opp.priority.value == "Medium"]
        low_priority = [opp for opp in opportunities if opp.priority.value == "Low"]
        
        if high_priority:
            markdown += f"## 🔥 High Priority Opportunities ({len(high_priority)})\n\n"
            for opp in high_priority:
                markdown += Exporter._opportunity_to_markdown(opp)
        
        if medium_priority:
            markdown += f"\n## 📈 Medium Priority Opportunities ({len(medium_priority)})\n\n"
            for opp in medium_priority[:10]:  # Limit to 10
                markdown += Exporter._opportunity_to_markdown(opp)
        
        return markdown
    
    @staticmethod
    def _opportunity_to_markdown(opportunity: Opportunity) -> str:
        """Convert single opportunity to markdown"""
        md = f"### {opportunity.title}\n"
        md += f"**Organization:** {opportunity.organization}  \n"
        md += f"**Score:** {opportunity.relevance_score}/100  \n"
        md += f"**Priority:** {opportunity.priority.value}  \n"
        
        if opportunity.deadline:
            days_left = (opportunity.deadline - datetime.now()).days
            md += f"**Deadline:** {opportunity.deadline.strftime('%Y-%m-%d')} ({days_left} days left)  \n"
        
        if opportunity.primary_skills:
            md += f"**Skills:** {', '.join(opportunity.primary_skills)}  \n"
        
        if opportunity.regions:
            md += f"**Regions:** {', '.join([r.value for r in opportunity.regions])}  \n"
        
        md += f"\n*{opportunity.ai_summary}*\n"
        md += f"\n[View Opportunity]({opportunity.url})\n"
        md += "---\n\n"
        
        return md