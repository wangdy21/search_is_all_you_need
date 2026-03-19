import os
import sys

# Ensure project root is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

from backend.config import get_config
from backend.models.database import init_db
from backend.routes.search import search_bp
from backend.routes.analysis import analysis_bp
from backend.routes.download import download_bp
from backend.routes.history import history_bp
from backend.utils.logger import get_logger

logger = get_logger("app")


def create_app():
    """Create and configure Flask application (API-only mode)."""
    config = get_config()

    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.SECRET_KEY

    # CORS: allow all origins for API
    CORS(app)

    # Register API blueprints
    app.register_blueprint(search_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(download_bp)
    app.register_blueprint(history_bp)

    # API root endpoint
    @app.route("/")
    def index():
        return jsonify({
            "message": "search_is_all_you_need API server running",
            "status": "ok",
            "version": "1.0.0",
            "api_endpoints": {
                "search": "/api/search",
                "analysis": "/api/analysis",
                "download": "/api/download",
                "history": "/api/history"
            }
        })

    # Health check endpoint
    @app.route("/health")
    def health():
        return jsonify({"status": "healthy"})

    # Global error handler
    @app.errorhandler(Exception)
    def handle_error(e):
        logger.error(f"Unhandled error: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

    return app


# Initialize DB and create app
init_db()
app = create_app()

if __name__ == "__main__":
    config = get_config()
    logger.info(f"Starting server on port {config.FLASK_PORT}")
    app.run(host="0.0.0.0", port=config.FLASK_PORT, debug=config.DEBUG)
