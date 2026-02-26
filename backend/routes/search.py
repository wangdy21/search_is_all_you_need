from flask import Blueprint, request, jsonify

from backend.services import search_service
from backend.utils.logger import get_logger

logger = get_logger("routes.search")
search_bp = Blueprint("search", __name__)

VALID_TIME_RANGES = {"week", "month", "year", "3years", None}
MAX_QUERIES = 5


@search_bp.route("/api/search", methods=["POST"])
def do_search():
    """Multi-source search endpoint supporting multiple keywords."""
    data = request.get_json(silent=True) or {}

    # Support both 'queries' (array) and 'query' (string) for backwards compatibility
    queries = data.get("queries")
    if queries is None:
        single_query = (data.get("query") or "").strip()
        queries = [single_query] if single_query else []
    
    # Validate and clean queries
    queries = [q.strip() for q in queries if isinstance(q, str) and q.strip()]
    if not queries:
        return jsonify({"error": "At least one query is required"}), 400
    if len(queries) > MAX_QUERIES:
        return jsonify({"error": f"Maximum {MAX_QUERIES} queries allowed"}), 400

    sources = data.get("sources") or None
    filters = data.get("filters") or {}

    # Validate time_range
    time_range = filters.get("time_range")
    if time_range not in VALID_TIME_RANGES:
        return jsonify({"error": f"Invalid time_range: {time_range}"}), 400

    try:
        result = search_service.search_multiple(queries, sources, filters)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        return jsonify({"error": "Search failed", "detail": str(e)}), 500
