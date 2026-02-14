from urllib.parse import urlparse

from backend.utils.logger import get_logger

logger = get_logger("classification_service")

# URL pattern rules for classification
_RULES = {
    "academic": {
        "domains": ["arxiv.org", "scholar.google.com", "pubmed.ncbi.nlm.nih.gov",
                     "ieee.org", "acm.org", "springer.com", "nature.com",
                     "sciencedirect.com", "doi.org"],
    },
    "qa": {
        "domains": ["zhihu.com", "stackoverflow.com", "stackexchange.com",
                     "quora.com", "segmentfault.com"],
    },
    "blog": {
        "domains": ["medium.com", "csdn.net", "blog.csdn.net", "juejin.cn",
                     "dev.to", "hashnode.com", "cnblogs.com", "jianshu.com",
                     "wordpress.com", "blogspot.com", "substack.com"],
    },
    "forum": {
        "domains": ["reddit.com", "v2ex.com", "news.ycombinator.com",
                     "discourse.org", "tieba.baidu.com"],
    },
}


def classify(url, source=None):
    """
    Classify a URL into a content category.

    Args:
        url: The resource URL.
        source: The search source name (e.g. "arxiv", "zhihu").

    Returns:
        Category string: "academic", "qa", "blog", "forum", or "webpage".
    """
    # Source-based classification takes priority
    source_map = {
        "arxiv": "academic",
        "scholar": "academic",
        "zhihu": "qa",
    }
    if source and source in source_map:
        return source_map[source]

    # URL-based classification
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower().lstrip("www.")
        path = parsed.path.lower()
    except Exception:
        return "webpage"

    for category, rules in _RULES.items():
        for rule_domain in rules["domains"]:
            if domain == rule_domain or domain.endswith("." + rule_domain):
                return category

    return "webpage"
