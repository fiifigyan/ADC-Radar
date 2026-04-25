import atexit
import logging
import os
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS

from src.ai_processor.ai_service import get_ai_processor
from src.database.local_db import LocalDatabase
from src.database.notion_db import NotionDatabase
from src.models.opportunity import Opportunity, Priority, SourcePlatform
from src.scheduling.scheduler_service import get_scheduler_service
from src.scrapers.scraper_service import ScraperService

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("adc-radar")

# ── App ───────────────────────────────────────────────────────────────────────
app = Flask(__name__)

allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
CORS(app, origins=allowed_origins, supports_credentials=True)

# ── Services ──────────────────────────────────────────────────────────────────
db = LocalDatabase()
scraper_service = ScraperService(db)
ai_processor = get_ai_processor()

scheduler_service = get_scheduler_service()
scheduler_service.set_scraper_service(scraper_service)
scheduler_service.start()

# Register clean shutdown — only fires when the process exits (not per-request)
atexit.register(scheduler_service.stop)

notion_db = None
try:
    notion_db = NotionDatabase()
    logger.info("Notion database initialised")
except Exception as exc:
    logger.warning("Notion not available: %s", exc)


# ── Helpers ───────────────────────────────────────────────────────────────────
def _validate_json(required: list[str]):
    data = request.get_json(silent=True)
    if not data:
        return None, jsonify({"error": "JSON body required"}), 400
    missing = [f for f in required if not data.get(f)]
    if missing:
        return None, jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400
    return data, None, None


# ── Opportunities ─────────────────────────────────────────────────────────────
@app.route("/api/opportunities", methods=["GET"])
def get_opportunities():
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 100, type=int), 500)
    opportunities = db.load_all_opportunities()
    total = len(opportunities)
    start = (page - 1) * per_page
    paginated = opportunities[start : start + per_page]
    return jsonify({"data": paginated, "total": total, "page": page, "per_page": per_page}), 200


@app.route("/api/opportunities/<opportunity_id>", methods=["GET"])
def get_opportunity(opportunity_id):
    for opp in db.load_all_opportunities():
        if opp.get("id") == opportunity_id:
            return jsonify(opp), 200
    return jsonify({"error": "Opportunity not found"}), 404


@app.route("/api/opportunities", methods=["POST"])
def create_opportunity():
    data, err_resp, err_code = _validate_json(["title", "organization"])
    if err_resp:
        return err_resp, err_code

    title = data.get("title", "").strip()
    organization = data.get("organization", "").strip()
    if len(title) > 300:
        return jsonify({"error": "Title too long (max 300 chars)"}), 400
    if len(organization) > 200:
        return jsonify({"error": "Organization too long (max 200 chars)"}), 400

    try:
        source_platform = SourcePlatform(data.get("source_platform", "Mock Data"))
    except ValueError:
        source_platform = SourcePlatform.MOCK

    try:
        priority = Priority(data.get("priority", "Medium"))
    except ValueError:
        priority = Priority.MEDIUM

    opp = Opportunity(
        title=title,
        organization=organization,
        description=data.get("description", ""),
        source_platform=source_platform,
        deadline=data.get("deadline"),
        url=data.get("url", ""),
        priority=priority,
    )

    opp_id = db.save_opportunity(opp)
    logger.info("Created opportunity: %s", opp.title)
    return jsonify({"id": opp_id, "message": "Opportunity created successfully"}), 201


@app.route("/api/search", methods=["GET"])
def search_opportunities():
    query = request.args.get("q", "").lower().strip()
    if not query:
        return jsonify(db.load_all_opportunities()), 200
    results = [
        o for o in db.load_all_opportunities()
        if query in o.get("title", "").lower()
        or query in o.get("organization", "").lower()
        or query in o.get("description", "").lower()
    ]
    return jsonify(results), 200


@app.route("/api/opportunities/filter", methods=["GET"])
def filter_opportunities():
    priority = request.args.get("priority")
    source = request.args.get("source")
    opportunities = db.load_all_opportunities()
    if priority:
        opportunities = [o for o in opportunities if o.get("priority") == priority]
    if source:
        opportunities = [o for o in opportunities if o.get("source_platform") == source]
    return jsonify(opportunities), 200


# ── Notion ────────────────────────────────────────────────────────────────────
@app.route("/api/notion/sync", methods=["POST"])
def sync_to_notion():
    if not notion_db:
        return jsonify({"error": "Notion database not configured"}), 503
    synced, failed = [], []
    for opp in db.load_as_objects():
        try:
            page_id = notion_db.add_opportunity(opp)
            synced.append({"id": opp.id, "title": opp.title, "notion_page_id": page_id})
        except Exception as exc:
            failed.append({"id": opp.id, "title": opp.title, "error": str(exc)})
    return jsonify({"message": f"Synced {len(synced)} opportunities", "synced": synced, "failed": failed}), 200


@app.route("/api/notion/status", methods=["GET"])
def notion_status():
    if not notion_db:
        return jsonify({"status": "disconnected", "message": "Notion not configured"}), 200
    try:
        notion_db.client.databases.retrieve(notion_db.database_id)
        return jsonify({"status": "connected", "database_id": notion_db.database_id}), 200
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


# ── Scraping ──────────────────────────────────────────────────────────────────
@app.route("/api/scrape", methods=["POST"])
def trigger_scrape():
    max_results = min(request.args.get("max_results", 50, type=int), 200)
    logger.info("Triggering full scrape (max %d per source)", max_results)
    results = scraper_service.scrape_all(max_results_per_source=max_results)
    return jsonify(results), 200


@app.route("/api/scrape/<source>", methods=["POST"])
def scrape_source(source):
    source_found = next((sp for sp in SourcePlatform if sp.value.lower() == source.lower()), None)
    if not source_found:
        return jsonify({
            "error": f"Source '{source}' not found",
            "available_sources": [s.value for s in SourcePlatform],
        }), 400
    max_results = min(request.args.get("max_results", 50, type=int), 200)
    logger.info("Scraping %s (max %d)", source_found.value, max_results)
    return jsonify(scraper_service.scrape_source(source_found, max_results=max_results)), 200


@app.route("/api/scrape/stats", methods=["GET"])
def scrape_stats():
    return jsonify(scraper_service.get_scrape_stats()), 200


# ── Schedules ─────────────────────────────────────────────────────────────────
@app.route("/api/schedules", methods=["GET"])
def get_schedules():
    return jsonify({"schedules": scheduler_service.get_schedules(), "status": scheduler_service.get_scheduler_status()}), 200


@app.route("/api/schedules/<name>", methods=["GET"])
def get_schedule(name):
    schedule = scheduler_service.get_schedule(name)
    if not schedule:
        return jsonify({"error": f"Schedule '{name}' not found"}), 404
    return jsonify(schedule), 200


@app.route("/api/schedules", methods=["POST"])
def create_schedule():
    data, err_resp, err_code = _validate_json(["name"])
    if err_resp:
        return err_resp, err_code
    name = data.pop("name").strip()
    result = scheduler_service.create_schedule(name, data)
    return jsonify(result), 201 if result["status"] == "success" else 400


@app.route("/api/schedules/<name>", methods=["PUT"])
def update_schedule(name):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400
    result = scheduler_service.update_schedule(name, data)
    return jsonify(result), 200 if result["status"] == "success" else 400


@app.route("/api/schedules/<name>", methods=["DELETE"])
def delete_schedule(name):
    result = scheduler_service.delete_schedule(name)
    return jsonify(result), 200 if result["status"] == "success" else 404


@app.route("/api/scheduler/status", methods=["GET"])
def scheduler_status():
    return jsonify(scheduler_service.get_scheduler_status()), 200


# ── AI Analysis ───────────────────────────────────────────────────────────────
@app.route("/api/ai/status", methods=["GET"])
def ai_status():
    return jsonify(ai_processor.get_status()), 200


@app.route("/api/analyze/<opportunity_id>", methods=["POST"])
def analyze_opportunity(opportunity_id):
    target = next((o for o in db.load_as_objects() if o.id == opportunity_id), None)
    if not target:
        return jsonify({"error": "Opportunity not found"}), 404
    analyzed = ai_processor.analyze_opportunity(target)
    db.save_opportunity(analyzed)
    logger.info("Analyzed: %s", analyzed.title)
    return jsonify({
        "status": "success",
        "opportunity": analyzed.to_dict(),
        "message": f"relevance={analyzed.relevance_score}, confidence={analyzed.confidence_score}",
    }), 200


@app.route("/api/analyze/batch/all", methods=["POST"])
def analyze_all_opportunities():
    unanalyzed = [o for o in db.load_as_objects() if o.processed_at is None]
    logger.info("Batch analyzing %d opportunities", len(unanalyzed))
    analyzed = ai_processor.batch_analyze(unanalyzed)
    for opp in analyzed:
        db.save_opportunity(opp)
    return jsonify({
        "status": "success",
        "total_analyzed": len(analyzed),
        "opportunities": [o.to_dict() for o in analyzed],
    }), 200


@app.route("/api/analyze/batch/by-source", methods=["POST"])
def analyze_by_source():
    data = request.get_json(silent=True)
    source = (data or {}).get("source")
    if not source:
        return jsonify({"error": "source field required"}), 400
    source_opps = [
        o for o in db.load_as_objects()
        if o.source_platform.value == source and o.processed_at is None
    ]
    logger.info("Batch analyzing %d from %s", len(source_opps), source)
    analyzed = ai_processor.batch_analyze(source_opps)
    for opp in analyzed:
        db.save_opportunity(opp)
    return jsonify({
        "status": "success",
        "source": source,
        "total_analyzed": len(analyzed),
        "opportunities": [o.to_dict() for o in analyzed],
    }), 200


# ── Health ────────────────────────────────────────────────────────────────────
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": "ok",
            "scheduler": "running" if scheduler_service.scheduler.running else "stopped",
            "ai": "configured" if ai_processor.available else "disabled",
            "notion": "connected" if notion_db else "disabled",
        },
    }), 200


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    port = int(os.getenv("PORT", 5000))
    app.run(debug=debug, host="0.0.0.0", port=port)
