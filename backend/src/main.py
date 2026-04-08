from flask import Flask, jsonify, request
from flask_cors import CORS
from src.database.local_db import LocalDatabase
from src.database.notion_db import NotionDatabase
from src.scrapers.scraper_service import ScraperService
from src.scheduling.scheduler_service import get_scheduler_service
from src.ai_processor.ai_service import get_ai_processor
from src.models.opportunity import Opportunity, SourcePlatform, Priority
from datetime import datetime
import json
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize databases and services
db = LocalDatabase()
scraper_service = ScraperService(db)
ai_processor = get_ai_processor()

# Initialize scheduler service
scheduler_service = get_scheduler_service()
scheduler_service.set_scraper_service(scraper_service)
scheduler_service.start()

# Try to initialize Notion database (optional)
notion_db = None
try:
    notion_db = NotionDatabase()
    app.logger.info("Notion database initialized successfully")
except Exception as e:
    app.logger.warning(f"Notion database not available: {e}")
    app.logger.info("Using local database only")

@app.route("/api/opportunities", methods=["GET"])
def get_opportunities():
    """Get all opportunities"""
    opportunities = db.load_all_opportunities()
    return jsonify(opportunities), 200

@app.route("/api/opportunities/<opportunity_id>", methods=["GET"])
def get_opportunity(opportunity_id):
    """Get a single opportunity by ID"""
    opportunities = db.load_all_opportunities()
    for opp in opportunities:
        if opp.get("id") == opportunity_id:
            return jsonify(opp), 200
    return jsonify({"error": "Opportunity not found"}), 404

@app.route("/api/opportunities", methods=["POST"])
def create_opportunity():
    """Create a new opportunity"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Parse source_platform
        source_platform_str = data.get("source_platform", "Mock Data")
        try:
            # Try to match the string value to enum
            source_platform = SourcePlatform(source_platform_str)
        except ValueError:
            # Default to MOCK if not found
            source_platform = SourcePlatform.MOCK
        
        # Parse priority
        priority_str = data.get("priority", "Medium")
        try:
            priority = Priority(priority_str)
        except ValueError:
            priority = Priority.MEDIUM
        
        # Create opportunity object
        opp = Opportunity(
            title=data.get("title", ""),
            organization=data.get("organization", ""),
            description=data.get("description", ""),
            source_platform=source_platform,
            deadline=data.get("deadline"),
            url=data.get("url", ""),
            priority=priority
        )
        
        # Save to database
        opp_id = db.save_opportunity(opp)
        
        app.logger.info(f"Created opportunity: {opp.title}")
        
        return jsonify({
            "id": opp_id,
            "message": "Opportunity created successfully"
        }), 201
    except ValueError as ve:
        app.logger.error(f"Validation error: {ve}")
        return jsonify({"error": f"Validation error: {str(ve)}"}), 400
    except Exception as e:
        app.logger.error(f"Error creating opportunity: {e}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/search", methods=["GET"])
def search_opportunities():
    """Search opportunities by query"""
    query = request.args.get("q", "").lower()
    opportunities = db.load_all_opportunities()
    
    results = [
        opp for opp in opportunities
        if query in opp.get("title", "").lower() or 
           query in opp.get("organization", "").lower() or
           query in opp.get("description", "").lower()
    ]
    
    return jsonify(results), 200

@app.route("/api/opportunities/filter", methods=["GET"])
def filter_opportunities():
    """Filter opportunities by criteria"""
    priority = request.args.get("priority")
    source = request.args.get("source")
    
    opportunities = db.load_all_opportunities()
    
    if priority:
        opportunities = [o for o in opportunities if o.get("priority") == priority]
    if source:
        opportunities = [o for o in opportunities if o.get("source_platform") == source]
    
    return jsonify(opportunities), 200

@app.route("/api/notion/sync", methods=["POST"])
def sync_to_notion():
    """Sync all local opportunities to Notion database"""
    if not notion_db:
        return jsonify({"error": "Notion database not configured"}), 503
    
    try:
        opportunities = db.load_as_objects()
        synced = []
        failed = []
        
        for opp in opportunities:
            try:
                page_id = notion_db.add_opportunity(opp)
                synced.append({
                    "id": opp.id,
                    "title": opp.title,
                    "notion_page_id": page_id
                })
            except Exception as e:
                failed.append({
                    "id": opp.id,
                    "title": opp.title,
                    "error": str(e)
                })
        
        return jsonify({
            "message": f"Synced {len(synced)} opportunities to Notion",
            "synced": synced,
            "failed": failed
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/notion/status", methods=["GET"])
def notion_status():
    """Check Notion database connection status"""
    if not notion_db:
        return jsonify({
            "status": "disconnected",
            "message": "Notion database not configured"
        }), 200
    
    try:
        # Try to query the database
        notion_db.client.databases.retrieve(notion_db.database_id)
        return jsonify({
            "status": "connected",
            "database_id": notion_db.database_id,
            "message": "Successfully connected to Notion database"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/api/scrape", methods=["POST"])
def trigger_scrape():
    """Trigger scraping from all sources"""
    try:
        max_results = request.args.get("max_results", 50, type=int)
        
        app.logger.info("Triggering scrape from all sources")
        results = scraper_service.scrape_all(max_results_per_source=max_results)
        
        return jsonify(results), 200
    except Exception as e:
        app.logger.error(f"Error triggering scrape: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/scrape/<source>", methods=["POST"])
def scrape_source(source):
    """Trigger scraping from a specific source"""
    try:
        # Find matching source
        source_found = None
        for sp in SourcePlatform:
            if sp.value.lower() == source.lower():
                source_found = sp
                break
        
        if not source_found:
            return jsonify({
                "error": f"Source '{source}' not found",
                "available_sources": [s.value for s in SourcePlatform]
            }), 400
        
        max_results = request.args.get("max_results", 50, type=int)
        
        app.logger.info(f"Triggering scrape from {source_found.value}")
        results = scraper_service.scrape_source(source_found, max_results=max_results)
        
        return jsonify(results), 200
    except Exception as e:
        app.logger.error(f"Error scraping {source}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/scrape/stats", methods=["GET"])
def scrape_stats():
    """Get scraping statistics"""
    try:
        stats = scraper_service.get_scrape_stats()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Schedule Management Endpoints

@app.route("/api/schedules", methods=["GET"])
def get_schedules():
    """Get all schedules"""
    try:
        schedules = scheduler_service.get_schedules()
        return jsonify({
            "schedules": schedules,
            "status": scheduler_service.get_scheduler_status()
        }), 200
    except Exception as e:
        app.logger.error(f"Error getting schedules: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/schedules/<name>", methods=["GET"])
def get_schedule(name):
    """Get a specific schedule"""
    try:
        schedule = scheduler_service.get_schedule(name)
        if not schedule:
            return jsonify({"error": f"Schedule '{name}' not found"}), 404
        return jsonify(schedule), 200
    except Exception as e:
        app.logger.error(f"Error getting schedule: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/schedules", methods=["POST"])
def create_schedule():
    """Create a new schedule"""
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({"error": "Schedule name is required"}), 400
        
        name = data.pop('name')
        result = scheduler_service.create_schedule(name, data)
        
        status_code = 201 if result['status'] == 'success' else 400
        return jsonify(result), status_code
    except Exception as e:
        app.logger.error(f"Error creating schedule: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/schedules/<name>", methods=["PUT"])
def update_schedule(name):
    """Update an existing schedule"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        result = scheduler_service.update_schedule(name, data)
        
        status_code = 200 if result['status'] == 'success' else 400
        return jsonify(result), status_code
    except Exception as e:
        app.logger.error(f"Error updating schedule: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/schedules/<name>", methods=["DELETE"])
def delete_schedule(name):
    """Delete a schedule"""
    try:
        result = scheduler_service.delete_schedule(name)
        
        status_code = 200 if result['status'] == 'success' else 400
        return jsonify(result), status_code
    except Exception as e:
        app.logger.error(f"Error deleting schedule: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/scheduler/status", methods=["GET"])
def scheduler_status():
    """Get scheduler status"""
    try:
        status = scheduler_service.get_scheduler_status()
        return jsonify(status), 200
    except Exception as e:
        app.logger.error(f"Error getting scheduler status: {e}")
        return jsonify({"error": str(e)}), 500

# AI Analysis Endpoints

@app.route("/api/ai/status", methods=["GET"])
def ai_status():
    """Get AI processor status"""
    try:
        status = ai_processor.get_status()
        return jsonify(status), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/analyze/<opportunity_id>", methods=["POST"])
def analyze_opportunity(opportunity_id):
    """Analyze a single opportunity with AI"""
    try:
        opportunities = db.load_as_objects()
        
        target_opp = None
        for opp in opportunities:
            if opp.id == opportunity_id:
                target_opp = opp
                break
        
        if not target_opp:
            return jsonify({"error": "Opportunity not found"}), 404
        
        # Analyze the opportunity
        analyzed_opp = ai_processor.analyze_opportunity(target_opp)
        
        # Save updated opportunity
        db.save_opportunity(analyzed_opp)
        
        app.logger.info(f"Analyzed opportunity: {analyzed_opp.title}")
        
        return jsonify({
            "status": "success",
            "opportunity": analyzed_opp.to_dict(),
            "message": f"Analyzed opportunity: relevance={analyzed_opp.relevance_score}, confidence={analyzed_opp.confidence_score}"
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error analyzing opportunity: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/analyze/batch/all", methods=["POST"])
def analyze_all_opportunities():
    """Analyze all unanalyzed opportunities with AI"""
    try:
        opportunities = db.load_as_objects()
        
        # Filter unanalyzed opportunities
        unanalyzed = [opp for opp in opportunities if opp.processed_at is None]
        
        app.logger.info(f"Starting batch analysis of {len(unanalyzed)} unanalyzed opportunities")
        
        # Analyze all
        analyzed = ai_processor.batch_analyze(unanalyzed)
        
        # Save all
        for opp in analyzed:
            db.save_opportunity(opp)
        
        results = {
            "status": "success",
            "total_analyzed": len(analyzed),
            "opportunities": [opp.to_dict() for opp in analyzed]
        }
        
        return jsonify(results), 200
        
    except Exception as e:
        app.logger.error(f"Error batch analyzing opportunities: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/analyze/batch/by-source", methods=["POST"])
def analyze_by_source():
    """Analyze opportunities from a specific source"""
    try:
        data = request.get_json()
        source = data.get("source") if data else None
        
        if not source:
            return jsonify({"error": "Source parameter required"}), 400
        
        opportunities = db.load_as_objects()
        
        # Filter by source
        source_opps = [opp for opp in opportunities if opp.source_platform.value == source and opp.processed_at is None]
        
        app.logger.info(f"Analyzing {len(source_opps)} unanalyzed opportunities from {source}")
        
        # Analyze all
        analyzed = ai_processor.batch_analyze(source_opps)
        
        # Save all
        for opp in analyzed:
            db.save_opportunity(opp)
        
        results = {
            "status": "success",
            "source": source,
            "total_analyzed": len(analyzed),
            "opportunities": [opp.to_dict() for opp in analyzed]
        }
        
        return jsonify(results), 200
        
    except Exception as e:
        app.logger.error(f"Error batch analyzing opportunities: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.teardown_appcontext
def shutdown_scheduler(exception=None):
    """Stop scheduler on app shutdown"""
    try:
        scheduler_service.stop()
    except Exception as e:
        app.logger.error(f"Error shutting down scheduler: {e}")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
