from flask import Blueprint, request, jsonify

from backend.services import analysis_service
from backend.utils.logger import get_logger

logger = get_logger("routes.analysis")
analysis_bp = Blueprint("analysis", __name__)


@analysis_bp.route("/api/analysis/summarize", methods=["POST"])
def summarize():
    """Generate content summary and key points."""
    data = request.get_json(silent=True) or {}

    content = (data.get("content") or "").strip()
    if not content:
        return jsonify({"error": "content is required"}), 400

    try:
        result = analysis_service.summarize(content)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Summarize error: {e}", exc_info=True)
        return jsonify({"error": "Summarize failed", "detail": str(e)}), 500


@analysis_bp.route("/api/analysis/translate", methods=["POST"])
def translate():
    """Translate content to target language."""
    data = request.get_json(silent=True) or {}

    content = (data.get("content") or "").strip()
    if not content:
        return jsonify({"error": "content is required"}), 400

    target_lang = data.get("target_lang", "zh")

    try:
        result = analysis_service.translate(content, target_lang)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Translate error: {e}", exc_info=True)
        return jsonify({"error": "Translation failed", "detail": str(e)}), 500


@analysis_bp.route("/api/translate", methods=["POST"])
def translate_simple():
    """Simple translate endpoint for batch export."""
    data = request.get_json(silent=True) or {}

    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "text is required"}), 400

    target_lang = data.get("target_lang", "zh")

    try:
        result = analysis_service.translate(text, target_lang)
        return jsonify({
            "translated": result.get("translated_text", text),
            "source_lang": result.get("source_lang", ""),
        }), 200
    except Exception as e:
        logger.error(f"Simple translate error: {e}", exc_info=True)
        return jsonify({"error": "Translation failed", "translated": text}), 200


@analysis_bp.route("/api/analysis/paper", methods=["POST"])
def analyze_paper():
    """Deep analysis of academic paper."""
    data = request.get_json(silent=True) or {}

    paper_data = {
        "title": data.get("title", ""),
        "abstract": data.get("abstract", ""),
        "snippet": data.get("snippet", ""),
    }

    if not paper_data["title"] and not paper_data["abstract"] and not paper_data["snippet"]:
        return jsonify({"error": "title or abstract/snippet is required"}), 400

    try:
        result = analysis_service.analyze_paper(paper_data)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Paper analysis error: {e}", exc_info=True)
        return jsonify({"error": "Paper analysis failed", "detail": str(e)}), 500


@analysis_bp.route("/api/analysis/paper-full", methods=["POST"])
def analyze_paper_full():
    """Deep analysis of full paper PDF content."""
    data = request.get_json(silent=True) or {}

    arxiv_id = (data.get("arxiv_id") or "").strip()
    title = data.get("title", "untitled")

    if not arxiv_id:
        return jsonify({"error": "arxiv_id is required"}), 400

    try:
        result = analysis_service.analyze_paper_full(arxiv_id, title)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Full paper analysis error: {e}", exc_info=True)
        return jsonify({"error": "Full paper analysis failed", "detail": str(e)}), 500
