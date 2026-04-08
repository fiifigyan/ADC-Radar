# AI Processing Integration Guide

## Overview

The ADC-Radar now includes AI-powered analysis for opportunity classification and summarization using OpenAI's GPT-3.5-turbo model.

## Features

### AI Analysis Capabilities

1. **Relevance Scoring** (0-100)
   - Evaluates how well opportunities align with African development focus
   - Considers opportunity quality and professional standards
   - Used to prioritize opportunities

2. **Confidence Scoring** (0-100)
   - Indicates reliability of AI assessment
   - Based on available information completeness
   - Helps identify opportunities needing manual review

3. **Priority Classification** (Low/Medium/High)
   - Recommends action level based on potential impact
   - Helps with opportunity triage
   - Integrated with dashboard filtering

4. **AI Summarization**
   - Auto-generates concise opportunity summaries
   - Extracts key details (role, responsibilities, requirements)
   - Useful for quick review of long descriptions

## Setup Instructions

### 1. Get OpenAI API Key

1. Go to https://platform.openai.com/account/api-keys
2. Create a new API key
3. Copy the key (you won't see it again)

### 2. Configure Environment Variable

Add to your `backend/.env` file:

```env
OPENAI_API_KEY=sk-your-api-key-here
```

### 3. Restart Backend

```bash
cd backend
python -m src.main
```

The AI processor will initialize automatically on startup.

## Usage

### Via Frontend

1. Navigate to the **Analyze** page
2. Check AI status (top of page shows if configured)
3. Options:
   - **Analyze All Unanalyzed** - Analyze all opportunities without AI analysis
   - **Select Source & Analyze** - Analyze opportunities from specific source
   - **Individual Analysis** - Click "Analyze" button on specific opportunity

### Via API

#### Check AI Status
```bash
GET http://localhost:5000/api/ai/status
```

#### Analyze Single Opportunity
```bash
POST http://localhost:5000/api/analyze/{opportunity_id}
```

#### Batch Analyze All
```bash
POST http://localhost:5000/api/analyze/batch/all
```

#### Batch Analyze by Source
```bash
POST http://localhost:5000/api/analyze/batch/by-source
Content-Type: application/json

{
  "source": "Devex"
}
```

### Automatic Analysis During Scraping

You can integrate AI analysis into the scraping workflow by adding this to your scheduler:

```python
# After scraping, automatically analyze new opportunities
from src.ai_processor import get_ai_processor

ai = get_ai_processor()
new_opportunities = db.load_as_objects()
unanalyzed = [opp for opp in new_opportunities if opp.processed_at is None]
ai.batch_analyze(unanalyzed)
```

## Data Structure

### Analyzed Opportunity Fields

```json
{
  "id": "string",
  "title": "string",
  "organization": "string",
  "description": "string",
  "relevance_score": 0-100,
  "confidence_score": 0-100,
  "priority": "High|Medium|Low",
  "ai_summary": "string",
  "processed_at": "ISO datetime or null"
}
```

## Cost Considerations

### OpenAI API Pricing

- Analysis uses **GPT-3.5-turbo** (most cost-effective)
- ~$0.001-0.002 per opportunity analyzed
- Budget estimate: $1 for 500-1000 opportunities

### Cost Optimization Tips

1. Analyze only new opportunities (not processed_at is null)
2. Use batch analysis for efficiency
3. Cache summaries to avoid re-running
4. Filter opportunities before analysis

## Troubleshooting

### "AI processing disabled" Message

**Cause**: `OPENAI_API_KEY` not set in environment

**Solution**:
1. Verify `.env` file has `OPENAI_API_KEY=sk-...`
2. Restart backend after adding key
3. Check AI status at `/api/ai/status`

### Analysis Returns Default Values

**Cause**: API error or rate limiting

**Solution**:
1. Check API key validity
2. Verify internet connection
3. Check OpenAI account has credits
4. Wait a moment and retry

### Confidence Score is 0

**Cause**: Insufficient information in opportunity description

**Solution**:
- Opportunities with incomplete data get lower confidence
- Manual review recommended
- Consider scraping more detailed sources

## Advanced Configuration

### Customize Analysis Prompt

Edit `backend/src/ai_processor/ai_service.py`:

```python
def _build_classification_prompt(self, opp: Opportunity) -> str:
    # Modify the prompt here for different analysis criteria
```

### Use Different AI Model

Change model in `backend/src/ai_processor/ai_service.py`:

```python
self.model = "gpt-4"  # Requires GPT-4 API access
```

### Batch Analysis with Custom Filtering

```python
from src.ai_processor import get_ai_processor
from src.database.local_db import LocalDatabase

db = LocalDatabase()
ai = get_ai_processor()

# Custom filter: analyze only high-priority deadlines
opps = db.load_as_objects()
urgent = [o for o in opps if o.deadline and o.processed_at is None]
ai.batch_analyze(urgent)
```

## Integration with Other Features

### With Scheduling

Create a schedule that analyzes opportunities daily after scraping:

1. Set up scraping schedule (e.g., 8:00 AM daily)
2. Schedule analysis for 9:00 AM
3. Both run automatically

### With Dashboard Filtering

Opportunities are filterable by:
- Relevance score (use for smart ranking)
- Priority level (High/Medium/Low)
- AI summary (for quick preview)

### With Notion Sync

AI analysis fields sync to Notion:
- Relevance Score (database property)
- Priority Level (select property)
- AI Summary (text property)

## FAQ

**Q: Can I use a different AI provider?**
A: Currently integrated with OpenAI. Modifications needed to use Azure/Anthropic APIs.

**Q: How long does analysis take?**
A: ~2-3 seconds per opportunity. Batch of 10 takes ~30 seconds.

**Q: Can I see the AI reasoning?**
A: Reasoning is included in backend logs. Add `processed_at` field shows when analyzed.

**Q: What if I want to change analysis criteria?**
A: Modify `_build_classification_prompt()` in `ai_service.py` to customize assessment criteria.

## Support

For issues:
1. Check API status: GET `/api/ai/status`
2. Verify API key and credits at platform.openai.com
3. Check backend logs for detailed error messages
4. Test with a single opportunity first before batch operations
