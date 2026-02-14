import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.models.database import get_connection
from backend.services import cache_service
from backend.services.classification_service import classify
from backend.config import get_config
from backend.utils.logger import get_logger

logger = get_logger("search_service")

# Lazy-initialized search agent
_search_agent = None


def _get_agent():
    global _search_agent
    if _search_agent is None:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".qoder"))
        from agents.search_agent import SearchAgent
        _search_agent = SearchAgent()
    return _search_agent


def search(query, sources=None, filters=None):
    """
    Execute multi-source search with caching and classification.

    Args:
        query: Search keyword string.
        sources: List of source names. Defaults to config defaults.
        filters: Optional filter dict.

    Returns:
        {"results": [...], "total": int, "sources_status": {...}}
    """
    config = get_config()
    sources = sources or config.SEARCH_DEFAULTS.get("default_sources", ["duckduckgo", "arxiv"])
    filters = filters or {}

    # Check cache
    cache_key = cache_service.make_search_cache_key(query, sources, filters)
    cached = cache_service.get_search_cache(cache_key)
    if cached:
        logger.info(f"Cache hit for query='{query}'")
        return cached

    # Execute search
    agent = _get_agent()
    result = agent.search_all_sources(query, sources, filters)

    # Classify each result
    for item in result.get("results", []):
        item["category"] = classify(item.get("url", ""), item.get("source", ""))

    # Store in cache
    ttl = config.SEARCH_DEFAULTS.get("cache_expire_hours", 24)
    cache_service.set_search_cache(cache_key, result, ttl_hours=ttl)

    # Save search history
    _save_history(query, filters, result.get("total", 0))

    logger.info(f"Search completed: query='{query}', total={result.get('total', 0)}")
    return result


def _save_history(query, filters, result_count):
    """Save search query to history."""
    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO search_history (query, filters, result_count) VALUES (?, ?, ?)",
                (query, json.dumps(filters, ensure_ascii=False), result_count),
            )
    except Exception as e:
        logger.warning(f"Failed to save search history: {e}")


def get_search_history(limit=20):
    """Retrieve recent search history."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, query, filters, result_count, timestamp FROM search_history "
            "ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def clear_search_history():
    """Delete all search history."""
    with get_connection() as conn:
        conn.execute("DELETE FROM search_history")
    logger.info("Search history cleared")
