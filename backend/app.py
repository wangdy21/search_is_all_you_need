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
    """Create and configure Flask application."""
    config = get_config()

    # Determine static folder
    static_folder = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
    static_folder = os.path.abspath(static_folder)

    app = Flask(__name__, static_folder=static_folder, static_url_path="")
    app.config["SECRET_KEY"] = config.SECRET_KEY

    # CORS: allow Vite dev server in development
    CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"])

    # Register API blueprints
    app.register_blueprint(search_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(download_bp)
    app.register_blueprint(history_bp)

    # SPA static file serving (production)
    @app.route("/")
    def serve_index():
        if os.path.exists(os.path.join(static_folder, "index.html")):
            return send_from_directory(static_folder, "index.html")
        return jsonify({"message": "search_is_all_you_need API server running", "status": "ok"})

    @app.route("/<path:path>")
    def serve_static(path):
        if path.startswith("api/"):
            return jsonify({"error": "Not found"}), 404
        file_path = os.path.join(static_folder, path)
        if os.path.exists(file_path):
            return send_from_directory(static_folder, path)
        # SPA fallback
        index_path = os.path.join(static_folder, "index.html")
        if os.path.exists(index_path):
            return send_from_directory(static_folder, "index.html")
        return jsonify({"error": "Not found"}), 404

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
