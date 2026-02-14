import os
import json
from pathlib import Path

from dotenv import load_dotenv

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
QODER_DIR = PROJECT_ROOT / ".qoder"

# Load .env file
load_dotenv(PROJECT_ROOT / ".env")


class Config:
    """Application configuration, merging .env and .qoder/config.json."""

    _instance = None

    def __init__(self):
        # Load qoder config.json
        config_path = QODER_DIR / "config.json"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                self._qoder_config = json.load(f)
        else:
            self._qoder_config = {}

        # Flask
        self.SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
        self.FLASK_ENV = os.getenv("FLASK_ENV", "development")
        self.FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
        self.DEBUG = self.FLASK_ENV == "development"

        # Database
        self.DATABASE_PATH = PROJECT_ROOT / os.getenv("DATABASE_PATH", "data/search.db")

        # 智谱AI
        self.ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "")

        # DeepSeek
        self.DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

        # HTTP Proxy
        self.HTTP_PROXY = os.getenv("HTTP_PROXY", "") or os.getenv("HTTPS_PROXY", "")

        # Download
        self.DOWNLOAD_DIR = PROJECT_ROOT / os.getenv("DOWNLOAD_DIR", "data/downloads")

        # Rate limits from config.json
        self.RATE_LIMITS = self._qoder_config.get("rate_limits", {})

        # Search defaults
        self.SEARCH_DEFAULTS = self._qoder_config.get("search_defaults", {
            "max_results_per_source": 15,
            "timeout_seconds": 30,
            "cache_expire_hours": 24,
            "default_sources": ["duckduckgo", "arxiv"],
        })

        # Download settings
        self.DOWNLOAD_SETTINGS = self._qoder_config.get("download_settings", {
            "max_concurrent_downloads": 3,
            "arxiv_mirrors": ["https://arxiv.org/pdf/", "https://cn.arxiv.org/pdf/"],
        })

        # Analysis settings
        self.ANALYSIS_SETTINGS = self._qoder_config.get("analysis_settings", {
            "model": "glm-4-flash",
            "max_content_length": 4000,
            "temperature": 0.7,
            "cache_expire_days": 7,
        })

        # Ensure data directories exist
        self.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


def get_config():
    """Get singleton Config instance."""
    if Config._instance is None:
        Config._instance = Config()
    return Config._instance
