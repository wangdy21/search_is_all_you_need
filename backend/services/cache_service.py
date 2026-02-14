import json
import hashlib
from datetime import datetime, timedelta

from backend.models.database import get_connection
from backend.utils.logger import get_logger

logger = get_logger("cache_service")


def _hash(text):
    """Generate MD5 hash for cache key."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def make_search_cache_key(query, sources, filters):
    """Generate cache key from search parameters."""
    raw = json.dumps({"q": query, "s": sorted(sources), "f": filters}, sort_keys=True)
    return _hash(raw)


def make_analysis_cache_key(content, analysis_type):
    """Generate cache key from analysis parameters."""
    truncated = content[:2000]
    return _hash(f"{truncated}:{analysis_type}")


# --- Search Cache ---

def get_search_cache(query_hash):
    """Get cached search results if not expired."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT results FROM search_cache WHERE query_hash = ? AND expire_at > ?",
            (query_hash, datetime.utcnow().isoformat()),
        ).fetchone()
        if row:
            logger.debug(f"Search cache hit: {query_hash[:8]}...")
            return json.loads(row["results"])
    return None


def set_search_cache(query_hash, results, ttl_hours=24):
    """Store search results in cache."""
    expire_at = (datetime.utcnow() + timedelta(hours=ttl_hours)).isoformat()
    results_json = json.dumps(results, ensure_ascii=False)
    with get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO search_cache (query_hash, results, expire_at) VALUES (?, ?, ?)",
            (query_hash, results_json, expire_at),
        )
    logger.debug(f"Search cache set: {query_hash[:8]}..., ttl={ttl_hours}h")


# --- Analysis Cache ---

def get_analysis_cache(content_hash, analysis_type):
    """Get cached analysis result."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT result, timestamp FROM analysis_cache WHERE content_hash = ? AND analysis_type = ?",
            (content_hash, analysis_type),
        ).fetchone()
        if row:
            # Check 7-day expiry
            cached_time = datetime.fromisoformat(row["timestamp"])
            if datetime.utcnow() - cached_time < timedelta(days=7):
                logger.debug(f"Analysis cache hit: {content_hash[:8]}... type={analysis_type}")
                return json.loads(row["result"])
            # Expired, clean up
            conn.execute(
                "DELETE FROM analysis_cache WHERE content_hash = ? AND analysis_type = ?",
                (content_hash, analysis_type),
            )
    return None


def set_analysis_cache(content_hash, analysis_type, result):
    """Store analysis result in cache."""
    result_json = json.dumps(result, ensure_ascii=False)
    with get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO analysis_cache (content_hash, analysis_type, result) VALUES (?, ?, ?)",
            (content_hash, analysis_type, result_json),
        )
    logger.debug(f"Analysis cache set: {content_hash[:8]}... type={analysis_type}")


# --- Cache Cleanup ---

def cleanup_expired_cache():
    """Remove expired entries from all cache tables."""
    with get_connection() as conn:
        now = datetime.utcnow().isoformat()
        deleted_search = conn.execute(
            "DELETE FROM search_cache WHERE expire_at <= ?", (now,)
        ).rowcount
        cutoff = (datetime.utcnow() - timedelta(days=7)).isoformat()
        deleted_analysis = conn.execute(
            "DELETE FROM analysis_cache WHERE timestamp <= ?", (cutoff,)
        ).rowcount
    if deleted_search or deleted_analysis:
        logger.info(f"Cache cleanup: search={deleted_search}, analysis={deleted_analysis}")
