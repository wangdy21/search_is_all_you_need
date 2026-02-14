import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FuturesTimeoutError

# Ensure project root is in path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import arxiv
from duckduckgo_search import DDGS

from backend.services.rate_limiter import RateLimiter
from backend.config import get_config
from backend.utils.logger import get_logger

logger = get_logger("search_agent")


class SearchAgent:
    """Orchestrates multi-source concurrent search."""

    def __init__(self):
        config = get_config()
        self.rate_limiter = RateLimiter(config.RATE_LIMITS)
        self.max_results = config.SEARCH_DEFAULTS.get("max_results_per_source", 15)
        self.timeout = config.SEARCH_DEFAULTS.get("timeout_seconds", 30)
        self.proxy = config.HTTP_PROXY if config.HTTP_PROXY else None
        if self.proxy:
            logger.info(f"Using proxy: {self.proxy}")

    def search_all_sources(self, query, sources, filters=None):
        """
        Concurrently search multiple sources.

        Args:
            query: Search keyword string.
            sources: List of source names, e.g. ["duckduckgo", "arxiv"].
            filters: Optional filters dict.

        Returns:
            {
                "results": [...],
                "total": int,
                "sources_status": {"source_name": "success"|"failed"|"skipped"}
            }
        """
        filters = filters or {}
        all_results = []
        sources_status = {}

        source_methods = {
            "duckduckgo": self._search_duckduckgo,
            "arxiv": self._search_arxiv,
            "scholar": self._search_scholar,
            "zhihu": self._search_zhihu,
        }

        # Filter to valid sources
        tasks = {}
        for src in sources:
            if src in source_methods:
                tasks[src] = source_methods[src]
            else:
                sources_status[src] = "skipped"

        if not tasks:
            return {"results": [], "total": 0, "sources_status": sources_status}

        with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
            futures = {
                executor.submit(method, query, filters): src
                for src, method in tasks.items()
            }

            completed_sources = set()
            try:
                for future in as_completed(futures, timeout=self.timeout):
                    src = futures[future]
                    completed_sources.add(src)
                    try:
                        results = future.result()
                        all_results.extend(results)
                        sources_status[src] = "success"
                        logger.info(f"Source '{src}' returned {len(results)} results")
                    except Exception as e:
                        sources_status[src] = "failed"
                        logger.error(f"Source '{src}' failed: {e}")
            except FuturesTimeoutError:
                # Mark uncompleted sources as timeout
                for future, src in futures.items():
                    if src not in completed_sources:
                        sources_status[src] = "timeout"
                        logger.warning(f"Source '{src}' timed out")
                        future.cancel()

        # Deduplicate by URL
        seen_urls = set()
        unique_results = []
        for item in all_results:
            url = item.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(item)

        return {
            "results": unique_results,
            "total": len(unique_results),
            "sources_status": sources_status,
        }

    def _search_duckduckgo(self, query, filters):
        """Search using DuckDuckGo."""
        self.rate_limiter.acquire("duckduckgo", timeout=10)
        results = []

        try:
            with DDGS(timeout=30, proxy=self.proxy) as ddgs:
                raw = ddgs.text(query, max_results=self.max_results)
                for item in raw:
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("href", ""),
                        "snippet": item.get("body", ""),
                        "source": "duckduckgo",
                        "authors": "",
                        "published": "",
                        "extra": {},
                    })
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            raise

        return results

    def _search_arxiv(self, query, filters):
        """Search arXiv for academic papers."""
        self.rate_limiter.acquire("arxiv", timeout=15)
        results = []

        try:
            # Use smaller page_size and add delay to avoid 429 rate limiting
            client = arxiv.Client(page_size=self.max_results, delay_seconds=1.0, num_retries=2)
            search = arxiv.Search(
                query=query,
                max_results=self.max_results,
                sort_by=arxiv.SortCriterion.Relevance,
            )
            for paper in client.results(search):
                arxiv_id = paper.entry_id.split("/abs/")[-1]
                results.append({
                    "title": paper.title,
                    "url": paper.entry_id,
                    "snippet": paper.summary[:500] if paper.summary else "",
                    "source": "arxiv",
                    "authors": ", ".join(a.name for a in paper.authors[:5]),
                    "published": paper.published.isoformat() if paper.published else "",
                    "extra": {
                        "arxiv_id": arxiv_id,
                        "pdf_url": paper.pdf_url,
                        "categories": [c for c in (paper.categories or [])],
                    },
                })
        except Exception as e:
            logger.error(f"arXiv search error: {e}")
            raise

        return results

    def _search_scholar(self, query, filters):
        """Search Google Scholar (optional, may be blocked)."""
        self.rate_limiter.acquire("scholar", timeout=15)
        results = []

        try:
            from scholarly import scholarly as scholarly_lib

            search_query = scholarly_lib.search_pubs(query)
            count = 0
            for pub in search_query:
                if count >= min(self.max_results, 10):
                    break
                bib = pub.get("bib", {})
                results.append({
                    "title": bib.get("title", ""),
                    "url": pub.get("pub_url", "") or pub.get("eprint_url", ""),
                    "snippet": bib.get("abstract", "")[:500],
                    "source": "scholar",
                    "authors": bib.get("author", ""),
                    "published": bib.get("pub_year", ""),
                    "extra": {
                        "venue": bib.get("venue", ""),
                        "citation_count": pub.get("num_citations", 0),
                    },
                })
                count += 1
        except Exception as e:
            logger.warning(f"Google Scholar search failed (may be blocked): {e}")
            raise

        return results

    def _search_zhihu(self, query, filters):
        """Search Zhihu content via DuckDuckGo site: search."""
        self.rate_limiter.acquire("zhihu", timeout=15)
        results = []

        try:
            zhihu_query = f"site:zhihu.com {query}"
            with DDGS(timeout=30, proxy=self.proxy) as ddgs:
                raw = ddgs.text(zhihu_query, max_results=min(self.max_results, 10))
                for item in raw:
                    url = item.get("href", "")
                    if "zhihu.com" not in url:
                        continue
                    results.append({
                        "title": item.get("title", ""),
                        "url": url,
                        "snippet": item.get("body", ""),
                        "source": "zhihu",
                        "authors": "",
                        "published": "",
                        "extra": {},
                    })
        except Exception as e:
            logger.error(f"Zhihu search error: {e}")
            raise

        return results
