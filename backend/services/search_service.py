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

# Lazy-initialized agents
_search_agent = None
_analysis_agent = None

# Default relevance threshold (0-100)
DEFAULT_RELEVANCE_THRESHOLD = 40


def _get_search_agent():
    global _search_agent
    if _search_agent is None:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".qoder"))
        from agents.search_agent import SearchAgent
        _search_agent = SearchAgent()
    return _search_agent


def _get_analysis_agent():
    global _analysis_agent
    if _analysis_agent is None:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".qoder"))
        from agents.analysis_agent import AnalysisAgent
        _analysis_agent = AnalysisAgent()
    return _analysis_agent


def _apply_semantic_filter(query, results, threshold=DEFAULT_RELEVANCE_THRESHOLD):
    """
    Apply AI-driven semantic relevance filtering to search results.

    Args:
        query: Original search query.
        results: List of search result dicts.
        threshold: Minimum relevance score (0-100) to keep a result.

    Returns:
        Filtered list of results sorted by relevance score.
    """
    if not results:
        return results

    config = get_config()
    # Allow disabling semantic filter via config
    if not config.SEARCH_DEFAULTS.get("enable_semantic_filter", True):
        return results

    try:
        agent = _get_analysis_agent()
        scored_results = agent.evaluate_relevance_batch(query, results)

        # Filter by threshold and sort by relevance
        filtered = [r for r in scored_results if r.get("relevance_score", 0) >= threshold]
        filtered.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

        logger.info(
            f"Semantic filter: {len(results)} -> {len(filtered)} results "
            f"(threshold={threshold})"
        )

        return filtered

    except Exception as e:
        logger.warning(f"Semantic filter failed, returning unfiltered results: {e}")
        return results


def search(query, sources=None, filters=None):
    """
    Execute multi-source search with caching, classification and semantic filtering.

    Args:
        query: Search keyword string.
        sources: List of source names. Defaults to config defaults.
        filters: Optional filter dict. May include 'semantic_filter' (bool) and
                 'relevance_threshold' (int 0-100).

    Returns:
        {"results": [...], "total": int, "sources_status": {...}}
    """
    config = get_config()
    sources = sources or config.SEARCH_DEFAULTS.get("default_sources", ["duckduckgo", "arxiv"])
    filters = filters or {}

    # Extract semantic filter settings from filters
    enable_semantic = filters.get("semantic_filter", True)
    relevance_threshold = filters.get("relevance_threshold", DEFAULT_RELEVANCE_THRESHOLD)

    # Check cache (includes semantic filter in key)
    cache_key = cache_service.make_search_cache_key(query, sources, filters)
    cached = cache_service.get_search_cache(cache_key)
    if cached:
        logger.info(f"Cache hit for query='{query}'")
        return cached

    # Execute search
    agent = _get_search_agent()
    result = agent.search_all_sources(query, sources, filters)

    # Classify each result
    for item in result.get("results", []):
        item["category"] = classify(item.get("url", ""), item.get("source", ""))

    # Apply semantic filtering if enabled
    if enable_semantic and result.get("results"):
        result["results"] = _apply_semantic_filter(
            query, result["results"], threshold=relevance_threshold
        )
        result["total"] = len(result["results"])

    # Store in cache
    ttl = config.SEARCH_DEFAULTS.get("cache_expire_hours", 24)
    cache_service.set_search_cache(cache_key, result, ttl_hours=ttl)

    # Save search history
    _save_history(query, filters, result.get("total", 0))

    logger.info(f"Search completed: query='{query}', total={result.get('total', 0)}")
    return result


def search_multiple(queries, sources=None, filters=None):
    """
    Execute search for multiple keywords independently and merge results.

    Args:
        queries: List of search keyword strings.
        sources: List of source names. Defaults to config defaults.
        filters: Optional filter dict.

    Returns:
        {"results": [...], "total": int, "sources_status": {...}}
    """
    config = get_config()
    sources = sources or config.SEARCH_DEFAULTS.get("default_sources", ["duckduckgo", "arxiv"])
    filters = filters or {}
    sources_set = set(sources)

    all_results = []
    merged_status = {}

    for query in queries:
        result = search(query, sources, filters)
        
        # Filter results by selected sources
        for item in result.get("results", []):
            item_source = item.get("source", "")
            if item_source in sources_set:
                all_results.append(item)
        
        # Merge sources_status (keep worst status per source)
        for src, status in result.get("sources_status", {}).items():
            if src not in merged_status:
                merged_status[src] = status
            elif merged_status[src] == "success" and status != "success":
                merged_status[src] = status

    # Deduplicate by URL
    seen_urls = set()
    unique_results = []
    for item in all_results:
        url = item.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(item)

    logger.info(f"Multi-query search: queries={queries}, merged_total={len(unique_results)}")
    
    return {
        "results": unique_results,
        "total": len(unique_results),
        "sources_status": merged_status,
    }


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
