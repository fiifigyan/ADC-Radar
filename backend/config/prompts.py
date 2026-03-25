CLASSIFICATION_PROMPT = """You are an expert screening development consultancy opportunities in Africa.

OPPORTUNITY TEXT:
{opportunity_text}

ANALYZE AND RETURN JSON WITH:
1. contract_type: "Individual Consultancy", "ICA", "Short-term Expert", "Roster", or "Other"
2. africa_focus: true/false
3. regions: array of regions if Africa-focused (West Africa, East Africa, Southern Africa, Central Africa, North Africa, Pan-African)
4. skills: array of relevant skills (Data, Digital, ICT, AI, Analytics, Digital Trade, MIS, Dashboards, Technology)
5. private_sector_context: true/false
6. summary: 2-3 sentence summary
7. confidence_score: 0-100 how confident you are in this analysis

OUTPUT FORMAT:
{
  "contract_type": "string",
  "africa_focus": boolean,
  "regions": ["string"],
  "skills": ["string"],
  "private_sector_context": boolean,
  "summary": "string",
  "confidence_score": number
}"""

WEEKLY_INSIGHTS_PROMPT = """Analyze these opportunities from this week and provide insights:

{opportunities_json}

PROVIDE JSON WITH:
1. most_requested_skills: top 5 skills
2. most_active_organizations: top 5 organizations
3. active_regions: regions with most opportunities
4. trends: 5 bullet point trends
5. recommendations: 3 recommendations for consultants

OUTPUT FORMAT:
{
  "most_requested_skills": [{"skill": "string", "count": number}],
  "most_active_organizations": [{"organization": "string", "count": number}],
  "active_regions": [{"region": "string", "count": number}],
  "trends": ["string"],
  "recommendations": ["string"]
}"""