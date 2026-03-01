import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.services import cache_service
from backend.config import get_config
from backend.utils.logger import get_logger

logger = get_logger("analysis_service")

# Lazy-initialized analysis agent
_analysis_agent = None


def _get_agent():
    global _analysis_agent
    if _analysis_agent is None:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".qoder"))
        from agents.analysis_agent import AnalysisAgent
        _analysis_agent = AnalysisAgent()
    return _analysis_agent


def summarize(content):
    """
    Generate content summary with caching.

    Returns:
        {"summary": str, "key_points": [str], "error": str|None}
    """
    cache_key = cache_service.make_analysis_cache_key(content, "summary")
    cached = cache_service.get_analysis_cache(cache_key, "summary")
    if cached:
        return cached

    agent = _get_agent()
    result = agent.generate_summary(content)

    if not result.get("error"):
        cache_service.set_analysis_cache(cache_key, "summary", result)

    return result


def translate(content, target_lang="zh"):
    """
    Translate content with caching.

    Returns:
        {"translated_text": str, "source_lang": str, "error": str|None}
    """
    cache_key = cache_service.make_analysis_cache_key(content, f"translate_{target_lang}")
    cached = cache_service.get_analysis_cache(cache_key, f"translate_{target_lang}")
    if cached:
        return cached

    agent = _get_agent()
    result = agent.translate_content(content, target_lang)

    if not result.get("error"):
        cache_service.set_analysis_cache(cache_key, f"translate_{target_lang}", result)

    return result


def analyze_paper(paper_data):
    """
    Analyze academic paper with caching.

    Args:
        paper_data: dict with title, abstract/snippet.

    Returns:
        {"abstract_summary": str, "method": str, "innovation": str,
         "results": str, "conclusion": str, "error": str|None}
    """
    content_for_key = f"{paper_data.get('title', '')}:{paper_data.get('abstract', paper_data.get('snippet', ''))}"
    cache_key = cache_service.make_analysis_cache_key(content_for_key, "paper_analysis")
    cached = cache_service.get_analysis_cache(cache_key, "paper_analysis")
    if cached:
        return cached

    agent = _get_agent()
    result = agent.analyze_paper(paper_data)

    if not result.get("error"):
        cache_service.set_analysis_cache(cache_key, "paper_analysis", result)

    return result


def analyze_paper_full(arxiv_id, title):
    """
    Deep analysis of a full paper by downloading and extracting its PDF.

    Args:
        arxiv_id: arXiv paper ID.
        title: Paper title.

    Returns:
        {"abstract_summary": str, "method": str, "innovation": str,
         "results": str, "conclusion": str, "error": str|None}
    """
    # Check cache first
    cache_key = cache_service.make_analysis_cache_key(f"full:{arxiv_id}", "paper_full_analysis")
    cached = cache_service.get_analysis_cache(cache_key, "paper_full_analysis")
    if cached:
        return cached

    config = get_config()

    # Download PDF if needed
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".qoder"))
    from skills.pdf_download_skill import get_or_download_pdf, extract_pdf_text

    pdf_path = get_or_download_pdf(arxiv_id, str(config.DATABASE_PATH), str(config.DOWNLOAD_DIR))
    if not pdf_path:
        return {
            "abstract_summary": "", "method": "", "innovation": "",
            "results": "", "conclusion": "",
            "error": "Failed to download PDF",
        }

    # Extract text from PDF
    full_text = extract_pdf_text(pdf_path)
    if not full_text:
        return {
            "abstract_summary": "", "method": "", "innovation": "",
            "results": "", "conclusion": "",
            "error": "Failed to extract text from PDF",
        }

    # Analyze with LLM
    agent = _get_agent()
    result = agent.analyze_paper_full(title, full_text)

    if not result.get("error"):
        cache_service.set_analysis_cache(cache_key, "paper_full_analysis", result)

    return result
