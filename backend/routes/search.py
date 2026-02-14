from flask import Blueprint, request, jsonify

from backend.services import search_service
from backend.utils.logger import get_logger

logger = get_logger("routes.search")
search_bp = Blueprint("search", __name__)


@search_bp.route("/api/search", methods=["POST"])
def do_search():
    """Multi-source search endpoint."""
    data = request.get_json(silent=True) or {}

    query = (data.get("query") or "").strip()
    if not query:
        return jsonify({"error": "query is required"}), 400

    sources = data.get("sources") or None
    filters = data.get("filters") or {}

    try:
        result = search_service.search(query, sources, filters)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        return jsonify({"error": "Search failed", "detail": str(e)}), 500
