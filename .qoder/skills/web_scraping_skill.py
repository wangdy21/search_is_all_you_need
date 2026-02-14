import random
import requests
from bs4 import BeautifulSoup

from backend.utils.logger import get_logger

logger = get_logger("web_scraping_skill")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]


def _get_headers():
    """Get request headers with random User-Agent."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }


def fetch_page(url, timeout=10):
    """
    Fetch a web page and return its HTML content.

    Args:
        url: URL to fetch.
        timeout: Request timeout in seconds.

    Returns:
        HTML string, or None on failure.
    """
    try:
        resp = requests.get(url, headers=_get_headers(), timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding
        return resp.text
    except requests.RequestException as e:
        logger.warning(f"Failed to fetch {url}: {e}")
        return None


def parse_zhihu_content(html):
    """
    Parse Zhihu question/answer page content.

    Returns:
        dict with title, answers (list of {content, author}), or None.
    """
    if not html:
        return None

    try:
        soup = BeautifulSoup(html, "lxml")

        # Question title
        title_tag = soup.find("h1", class_="QuestionHeader-title")
        if not title_tag:
            title_tag = soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else ""

        # Answer excerpts
        answers = []
        answer_items = soup.find_all("div", class_="RichContent-inner", limit=3)
        for item in answer_items:
            text = item.get_text(strip=True)[:500]
            answers.append({"content": text, "author": ""})

        # Try to extract authors
        author_tags = soup.find_all("a", class_="UserLink-link", limit=3)
        for i, tag in enumerate(author_tags):
            if i < len(answers):
                answers[i]["author"] = tag.get_text(strip=True)

        return {"title": title, "answers": answers}
    except Exception as e:
        logger.warning(f"Failed to parse Zhihu content: {e}")
        return None


def extract_metadata(html):
    """
    Extract OpenGraph metadata from HTML page.

    Returns:
        dict with title, description, author, published_time.
    """
    if not html:
        return {}

    try:
        soup = BeautifulSoup(html, "lxml")
        meta = {}

        og_mappings = {
            "og:title": "title",
            "og:description": "description",
            "article:author": "author",
            "article:published_time": "published_time",
        }

        for og_prop, key in og_mappings.items():
            tag = soup.find("meta", property=og_prop)
            if tag and tag.get("content"):
                meta[key] = tag["content"]

        # Fallback: use <title> tag
        if "title" not in meta:
            title_tag = soup.find("title")
            if title_tag:
                meta["title"] = title_tag.get_text(strip=True)

        # Fallback: use meta description
        if "description" not in meta:
            desc_tag = soup.find("meta", attrs={"name": "description"})
            if desc_tag and desc_tag.get("content"):
                meta["description"] = desc_tag["content"]

        return meta
    except Exception as e:
        logger.warning(f"Failed to extract metadata: {e}")
        return {}
