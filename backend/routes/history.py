from flask import Blueprint, request, jsonify

from backend.services.search_service import get_search_history, clear_search_history
from backend.utils.logger import get_logger

logger = get_logger("routes.history")
history_bp = Blueprint("history", __name__)


@history_bp.route("/api/history", methods=["GET"])
def get_history():
    """Get search history."""
    limit = request.args.get("limit", 20, type=int)
    limit = min(max(limit, 1), 100)

    try:
        history = get_search_history(limit)
        return jsonify({"history": history}), 200
    except Exception as e:
        logger.error(f"History query error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@history_bp.route("/api/history", methods=["DELETE"])
def clear_history():
    """Clear all search history."""
    try:
        clear_search_history()
        return jsonify({"success": True}), 200
    except Exception as e:
        logger.error(f"History clear error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
