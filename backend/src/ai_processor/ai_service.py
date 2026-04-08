"""
AI Processor service for analyzing opportunities
Classifies relevance, summarizes descriptions, and generates insights
"""

import logging
import os
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from openai import OpenAI, OpenAIError
from src.models.opportunity import Opportunity, Priority

logger = logging.getLogger(__name__)

# Initialize OpenAI client with safe error handling
client = None
try:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        client = OpenAI(api_key=api_key)
    else:
        logger.warning("OPENAI_API_KEY environment variable not set. AI processing will be disabled.")
except Exception as e:
    logger.warning(f"Failed to initialize OpenAI client: {e}. AI processing will be disabled.")

class AIProcessor:
    """Processor for AI-based opportunity analysis"""
    
    def __init__(self):
        """Initialize AI processor"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = "gpt-3.5-turbo"
        self.available = bool(self.api_key)
        
        if not self.available:
            logger.warning("OpenAI API key not configured. AI processing disabled.")
    
    def classify_opportunity(self, opportunity: Opportunity) -> Tuple[int, int, Priority]:
        """
        Classify an opportunity for relevance using AI
        Returns: (relevance_score, confidence_score, priority)
        """
        if not self.available:
            logger.warning("AI processing disabled. Returning default values.")
            return 50, 0, Priority.MEDIUM
        
        try:
            if client is None:
                logger.warning("OpenAI client not available. Returning default values.")
                return 50, 0, Priority.MEDIUM
                
            prompt = self._build_classification_prompt(opportunity)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at evaluating development and consultancy opportunities for African projects. Analyze opportunities and provide structured assessments."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content
            relevance_score, confidence_score, priority = self._parse_classification_response(result_text)
            
            logger.info(f"Classified '{opportunity.title}': relevance={relevance_score}, confidence={confidence_score}")
            return relevance_score, confidence_score, priority
            
        except OpenAIError as e:
            logger.error(f"OpenAI API error during classification: {e}")
            return 50, 0, Priority.MEDIUM
        except Exception as e:
            logger.error(f"Error classifying opportunity: {e}")
            return 50, 0, Priority.MEDIUM
    
    def summarize_description(self, opportunity: Opportunity, max_length: int = 200) -> str:
        """
        Summarize a long opportunity description
        Returns: Concise summary
        """
        if not self.available:
            # Fallback: simple truncation
            return opportunity.description[:max_length] if opportunity.description else ""
        
        try:
            if client is None:
                # Fallback: simple truncation
                return opportunity.description[:max_length] if opportunity.description else ""
                
            # If description is already short, return as-is
            if len(opportunity.description) <= max_length:
                return opportunity.description
            
            prompt = f"""Summarize the following consultancy opportunity description in {max_length} characters or less.
Focus on key details: role, responsibilities, requirements, and benefits.
Be concise and informative.

Description:
{opportunity.description}

Summary:"""
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at summarizing job and consultancy opportunities concisely."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=100
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info(f"Summarized '{opportunity.title}': {len(summary)} chars")
            return summary
            
        except OpenAIError as e:
            logger.error(f"OpenAI API error during summarization: {e}")
            return opportunity.description[:max_length]
        except Exception as e:
            logger.error(f"Error summarizing description: {e}")
            return opportunity.description[:max_length]
    
    def analyze_opportunity(self, opportunity: Opportunity) -> Opportunity:
        """
        Perform full AI analysis on an opportunity
        Updates: relevance_score, confidence_score, priority, ai_summary, processed_at
        Returns: Updated opportunity object
        """
        logger.info(f"Analyzing opportunity: {opportunity.title}")
        
        # Classify
        relevance_score, confidence_score, priority = self.classify_opportunity(opportunity)
        opportunity.relevance_score = relevance_score
        opportunity.confidence_score = confidence_score
        opportunity.priority = priority
        
        # Summarize
        summary = self.summarize_description(opportunity)
        opportunity.ai_summary = summary
        
        # Mark as processed
        opportunity.processed_at = datetime.now()
        
        logger.info(f"Analysis complete for '{opportunity.title}'")
        return opportunity
    
    def _build_classification_prompt(self, opp: Opportunity) -> str:
        """Build the prompt for opportunity classification"""
        return f"""Analyze this African development consultancy opportunity and evaluate its relevance and quality.

Title: {opp.title}
Organization: {opp.organization}
Source: {opp.source_platform.value}
Deadline: {opp.deadline.strftime('%Y-%m-%d') if opp.deadline else 'Not specified'}
Countries: {', '.join(opp.countries) if opp.countries else 'Not specified'}
Regions: {', '.join([r.value for r in opp.regions]) if opp.regions else 'Not specified'}

Description:
{opp.description[:1000]}

Please provide:
1. A relevance score (0-100) based on: opportunity quality, African focus, professional standards
2. A confidence score (0-100) based on how much information you had to assess
3. A priority level (Low/Medium/High) based on potential impact and ROI

Format your response as:
RELEVANCE_SCORE: [0-100]
CONFIDENCE_SCORE: [0-100]
PRIORITY: [Low/Medium/High]
REASONING: [2-3 sentence explanation]"""
    
    def _parse_classification_response(self, response: str) -> Tuple[int, int, Priority]:
        """Parse the AI classification response"""
        try:
            lines = response.strip().split('\n')
            relevance = 50
            confidence = 50
            priority = Priority.MEDIUM
            
            for line in lines:
                if 'RELEVANCE_SCORE' in line:
                    relevance = int(''.join(filter(str.isdigit, line.split(':')[1])))
                    relevance = max(0, min(100, relevance))  # Clamp 0-100
                elif 'CONFIDENCE_SCORE' in line:
                    confidence = int(''.join(filter(str.isdigit, line.split(':')[1])))
                    confidence = max(0, min(100, confidence))  # Clamp 0-100
                elif 'PRIORITY' in line:
                    priority_text = line.split(':')[1].strip().lower()
                    if 'high' in priority_text:
                        priority = Priority.HIGH
                    elif 'low' in priority_text:
                        priority = Priority.LOW
                    else:
                        priority = Priority.MEDIUM
            
            return relevance, confidence, priority
            
        except Exception as e:
            logger.error(f"Error parsing classification response: {e}")
            return 50, 0, Priority.MEDIUM
    
    def batch_analyze(self, opportunities: list) -> list:
        """
        Analyze multiple opportunities
        Returns: List of updated opportunities
        """
        logger.info(f"Starting batch analysis of {len(opportunities)} opportunities")
        
        analyzed = []
        for i, opp in enumerate(opportunities, 1):
            try:
                analyzed_opp = self.analyze_opportunity(opp)
                analyzed.append(analyzed_opp)
                logger.info(f"  [{i}/{len(opportunities)}] Analyzed: {opp.title}")
            except Exception as e:
                logger.error(f"Error analyzing opportunity {i}: {e}")
                analyzed.append(opp)
        
        logger.info(f"Batch analysis complete. Analyzed {len(analyzed)} opportunities.")
        return analyzed
    
    @staticmethod
    def get_status() -> Dict[str, Any]:
        """Get AI processor status"""
        api_key = os.getenv("OPENAI_API_KEY")
        return {
            "available": bool(api_key),
            "configured": bool(api_key),
            "model": "gpt-3.5-turbo",
            "message": "OpenAI API configured" if api_key else "OpenAI API key not set in environment"
        }


# Global instance
ai_processor: Optional[AIProcessor] = None


def get_ai_processor() -> AIProcessor:
    """Get or create the global AI processor instance"""
    global ai_processor
    if ai_processor is None:
        ai_processor = AIProcessor()
    return ai_processor
