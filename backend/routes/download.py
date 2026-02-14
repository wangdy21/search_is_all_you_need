import sys
import os
from flask import Blueprint, request, jsonify, send_file

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.config import get_config
from backend.utils.logger import get_logger

logger = get_logger("routes.download")
download_bp = Blueprint("download", __name__)


@download_bp.route("/api/download/arxiv", methods=["POST"])
def download_arxiv():
    """Start arXiv PDF download."""
    data = request.get_json(silent=True) or {}

    arxiv_id = (data.get("arxiv_id") or "").strip()
    title = data.get("title", "untitled")

    if not arxiv_id:
        return jsonify({"error": "arxiv_id is required"}), 400

    try:
        from dotenv import load_dotenv
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".qoder"))
        from skills.pdf_download_skill import start_download

        config = get_config()
        record_id = start_download(
            arxiv_id, title,
            str(config.DATABASE_PATH),
            str(config.DOWNLOAD_DIR),
        )
        return jsonify({"download_id": record_id, "status": "pending"}), 200
    except Exception as e:
        logger.error(f"Download start error: {e}", exc_info=True)
        return jsonify({"error": "Download failed to start", "detail": str(e)}), 500


@download_bp.route("/api/download/status/<int:download_id>", methods=["GET"])
def download_status(download_id):
    """Query download status."""
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".qoder"))
        from skills.pdf_download_skill import get_download_status

        config = get_config()
        status = get_download_status(download_id, str(config.DATABASE_PATH))
        if status:
            return jsonify(status), 200
        return jsonify({"error": "Download not found"}), 404
    except Exception as e:
        logger.error(f"Status query error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@download_bp.route("/api/download/file/<int:download_id>", methods=["GET"])
def download_file(download_id):
    """Serve downloaded PDF file."""
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".qoder"))
        from skills.pdf_download_skill import get_download_status

        config = get_config()
        status = get_download_status(download_id, str(config.DATABASE_PATH))

        if not status:
            return jsonify({"error": "Download not found"}), 404
        if status["status"] != "completed":
            return jsonify({"error": "Download not completed", "status": status["status"]}), 400

        pdf_path = status.get("pdf_path")
        if not pdf_path or not os.path.exists(pdf_path):
            return jsonify({"error": "PDF file not found on disk"}), 404

        return send_file(pdf_path, mimetype="application/pdf", as_attachment=True,
                         download_name=os.path.basename(pdf_path))
    except Exception as e:
        logger.error(f"File serve error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@download_bp.route("/api/download/history", methods=["GET"])
def download_history():
    """Get all download records."""
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".qoder"))
        from skills.pdf_download_skill import get_all_downloads

        config = get_config()
        downloads = get_all_downloads(str(config.DATABASE_PATH))
        return jsonify({"downloads": downloads}), 200
    except Exception as e:
        logger.error(f"Download history error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
