import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FuturesTimeoutError
from urllib.parse import quote_plus

# Ensure project root is in path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import arxiv
import requests
from bs4 import BeautifulSoup
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
        """Search using Bing as backend (DuckDuckGo inaccessible in some regions)."""
        self.rate_limiter.acquire("duckduckgo", timeout=10)
        results = []

        try:
            search_url = f"https://cn.bing.com/search?q={quote_plus(query)}&count={self.max_results}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }

            resp = requests.get(search_url, headers=headers, timeout=15)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "html.parser")
            for item in soup.select("li.b_algo"):
                h2 = item.select_one("h2 a")
                if not h2:
                    continue

                title = h2.get_text(strip=True)
                url = h2.get("href", "")
                snippet_elem = item.select_one("p")
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet[:500] if snippet else "",
                    "source": "duckduckgo",
                    "authors": "",
                    "published": "",
                    "extra": {},
                })

            logger.info(f"Web search via Bing returned {len(results)} results")
        except Exception as e:
            logger.error(f"Web search error: {e}")
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
        """Search academic papers via Semantic Scholar API."""
        self.rate_limiter.acquire("scholar", timeout=15)
        results = []

        try:
            # Use Semantic Scholar API (free, no auth required for basic search)
            api_url = "https://api.semanticscholar.org/graph/v1/paper/search"
            params = {
                "query": query,
                "limit": min(self.max_results, 10),
                "fields": "title,url,abstract,authors,year,citationCount,venue,externalIds",
            }
            headers = {
                "Accept": "application/json",
                "User-Agent": "SearchIsAllYouNeed/1.0",
            }
            
            # Retry with backoff for rate limits
            import time
            max_retries = 2
            for attempt in range(max_retries + 1):
                resp = requests.get(api_url, params=params, headers=headers, timeout=15)
                if resp.status_code == 429:
                    if attempt < max_retries:
                        wait_time = 2 ** attempt  # 1, 2 seconds
                        logger.info(f"Semantic Scholar rate limited, retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception("Rate limit exceeded after retries")
                resp.raise_for_status()
                break
            
            data = resp.json()
            
            for paper in data.get("data", []):
                authors = paper.get("authors", [])
                author_names = ", ".join(a.get("name", "") for a in authors[:5])
                
                # Get best URL (prefer DOI or arXiv)
                external_ids = paper.get("externalIds", {}) or {}
                url = paper.get("url", "")
                if external_ids.get("DOI"):
                    url = f"https://doi.org/{external_ids['DOI']}"
                elif external_ids.get("ArXiv"):
                    url = f"https://arxiv.org/abs/{external_ids['ArXiv']}"
                
                results.append({
                    "title": paper.get("title", ""),
                    "url": url,
                    "snippet": (paper.get("abstract", "") or "")[:500],
                    "source": "scholar",
                    "authors": author_names,
                    "published": str(paper.get("year", "")),
                    "extra": {
                        "venue": paper.get("venue", ""),
                        "citation_count": paper.get("citationCount", 0),
                    },
                })
            
            logger.info(f"Semantic Scholar returned {len(results)} results")
        except Exception as e:
            logger.warning(f"Semantic Scholar search failed: {e}")
            raise

        return results

    def _search_zhihu(self, query, filters):
        """Search Zhihu content via Bing site: search."""
        self.rate_limiter.acquire("zhihu", timeout=15)
        results = []

        try:
            # Use Bing China for better accessibility
            search_url = f"https://cn.bing.com/search?q=site%3Azhihu.com+{quote_plus(query)}&count=10"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            
            resp = requests.get(search_url, headers=headers, timeout=15)
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, "html.parser")
            for item in soup.select("li.b_algo"):
                h2 = item.select_one("h2 a")
                if not h2:
                    continue
                url = h2.get("href", "")
                if "zhihu.com" not in url:
                    continue
                
                title = h2.get_text(strip=True)
                snippet_elem = item.select_one("p")
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet[:500] if snippet else "",
                    "source": "zhihu",
                    "authors": "",
                    "published": "",
                    "extra": {},
                })
                
            logger.info(f"Zhihu search via Bing returned {len(results)} results")
        except Exception as e:
            logger.error(f"Zhihu search error: {e}")
            raise

        return results
