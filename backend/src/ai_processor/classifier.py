"""
AI-powered opportunity classifier using OpenAI
"""
import json
import logging
from typing import Dict, Any, List
from openai import OpenAI
from src.models.opportunity import Opportunity, ContractType, Region, Priority

logger = logging.getLogger(__name__)

class OpportunityClassifier:
    """Classifies opportunities using AI"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def classify(self, opportunity: Opportunity) -> Dict[str, Any]:
        """Classify a single opportunity using AI"""
        try:
            # Prepare the prompt
            from config.prompts import CLASSIFICATION_PROMPT
            
            prompt = CLASSIFICATION_PROMPT.format(
                opportunity_text=opportunity.description[:2000]  # Limit to 2000 chars
            )
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in development consultancy opportunities."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500
            )
            
            # Parse the response
            result_text = response.choices[0].message.content
            
            # Clean the response (remove markdown code blocks)
            result_text = result_text.replace('```json', '').replace('```', '').strip()
            
            # Parse JSON
            ai_result = json.loads(result_text)
            
            return ai_result
            
        except Exception as e:
            logger.error(f"AI classification failed: {e}")
            # Return default result
            return {
                "contract_type": "Other",
                "africa_focus": False,
                "regions": [],
                "skills": [],
                "private_sector_context": False,
                "summary": "Analysis failed",
                "confidence_score": 0
            }
    
    def calculate_relevance_score(self, ai_result: Dict[str, Any]) -> int:
        """Calculate relevance score based on AI analysis"""
        score = 0
        
        # Check for digital/data skills
        digital_skills = {"data", "digital", "ict", "ai", "analytics", "technology", "mis", "dashboard", "software", "tech"}
        detected_skills = [skill.lower() for skill in ai_result.get("skills", [])]
        
        has_digital_skill = any(
            any(digital_skill in detected_skill or detected_skill in digital_skill 
                for digital_skill in digital_skills)
            for detected_skill in detected_skills
        )
        
        if has_digital_skill:
            score += 40
        
        # Africa focus
        if ai_result.get("africa_focus", False):
            score += 25
        
        # Private sector context
        if ai_result.get("private_sector_context", False):
            score += 15
        
        # Individual consultancy
        contract_type = ai_result.get("contract_type", "").lower()
        if any(term in contract_type for term in ["individual", "ica", "short-term", "expert"]):
            score += 10
        
        # Confidence adjustment
        confidence = ai_result.get("confidence_score", 0)
        score = int(score * (confidence / 100.0))
        
        return min(score, 100)
    
    def update_opportunity_from_ai(self, opportunity: Opportunity, ai_result: Dict[str, Any]) -> Opportunity:
        """Update opportunity with AI analysis results"""
        # Update contract type
        contract_map = {
            "individual consultancy": ContractType.INDIVIDUAL_CONSULTANCY,
            "ica": ContractType.ICA,
            "short-term expert": ContractType.SHORT_TERM_EXPERT,
            "roster": ContractType.ROSTER
        }
        
        contract_str = ai_result.get("contract_type", "").lower()
        opportunity.contract_type = contract_map.get(contract_str, ContractType.OTHER)
        
        # Set roster call flag
        opportunity.is_roster_call = "roster" in contract_str.lower()
        
        # Update skills
        opportunity.primary_skills = ai_result.get("skills", [])[:3]  # Top 3 as primary
        if len(ai_result.get("skills", [])) > 3:
            opportunity.secondary_skills = ai_result.get("skills", [])[3:]
        
        # Update regions
        region_map = {
            "west africa": Region.WEST_AFRICA,
            "east africa": Region.EAST_AFRICA,
            "southern africa": Region.SOUTHERN_AFRICA,
            "central africa": Region.CENTRAL_AFRICA,
            "north africa": Region.NORTH_AFRICA,
            "pan-african": Region.PAN_AFRICAN
        }
        
        regions = []
        for region_str in ai_result.get("regions", []):
            if region_str.lower() in region_map:
                regions.append(region_map[region_str.lower()])
        opportunity.regions = regions
        
        # Update AI summary
        opportunity.ai_summary = ai_result.get("summary", "")
        opportunity.confidence_score = ai_result.get("confidence_score", 0)
        
        # Calculate relevance score
        relevance_score = self.calculate_relevance_score(ai_result)
        opportunity.relevance_score = relevance_score
        
        # Set priority based on score
        if relevance_score >= 80:
            opportunity.priority = Priority.HIGH
        elif relevance_score >= 60:
            opportunity.priority = Priority.MEDIUM
        else:
            opportunity.priority = Priority.LOW
        
        # Mark as processed
        from datetime import datetime
        opportunity.processed_at = datetime.now()
        
        return opportunity