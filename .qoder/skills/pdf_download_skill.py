import os
import sqlite3
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from backend.utils.logger import get_logger

logger = get_logger("pdf_download_skill")

# Download configuration
MAX_CONCURRENT_DOWNLOADS = int(os.getenv("MAX_CONCURRENT_DOWNLOADS", "5"))
CHUNK_SIZE = 512 * 1024  # 512KB chunks for better throughput
CONNECTION_TIMEOUT = 30  # Connection timeout
READ_TIMEOUT = 300  # Read timeout for large files

# Global download thread pool
_executor = ThreadPoolExecutor(max_workers=MAX_CONCURRENT_DOWNLOADS)

# Connection pool with retry strategy
_session = None
_session_lock = threading.Lock()

ARXIV_MIRRORS = [
    "https://arxiv.org/pdf/",
    "https://cn.arxiv.org/pdf/",
    "https://export.arxiv.org/pdf/",  # Export mirror
]

# Cache for best mirror (per session)
_best_mirror = None
_mirror_test_lock = threading.Lock()
_mirror_selected_time = 0


def _get_session():
    """Get or create a shared requests session with connection pooling."""
    global _session
    if _session is None:
        with _session_lock:
            if _session is None:
                _session = requests.Session()
                # Configure retry strategy
                retry_strategy = Retry(
                    total=3,
                    backoff_factor=0.5,
                    status_forcelist=[429, 500, 502, 503, 504],
                )
                adapter = HTTPAdapter(
                    pool_connections=10,
                    pool_maxsize=20,
                    max_retries=retry_strategy,
                )
                _session.mount("http://", adapter)
                _session.mount("https://", adapter)
                _session.headers.update({
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "application/pdf,*/*",
                    "Accept-Encoding": "gzip, deflate",
                    "Connection": "keep-alive",
                })
    return _session


def _test_mirror_speed(mirror_url, test_id="2301.00001"):
    """Test mirror response time."""
    try:
        url = f"{mirror_url}{test_id}.pdf"
        start = time.time()
        resp = _get_session().head(url, timeout=5, allow_redirects=True)
        if resp.status_code < 400:
            return time.time() - start
    except Exception:
        pass
    return float('inf')


def _get_best_mirror():
    """Find the fastest available mirror using parallel testing."""
    global _best_mirror, _mirror_selected_time
    if _best_mirror is not None and (time.time() - _mirror_selected_time) < 600:
        return _best_mirror
    
    with _mirror_test_lock:
        if _best_mirror is not None and (time.time() - _mirror_selected_time) < 600:
            return _best_mirror
        
        logger.info("Testing arXiv mirrors for best speed (parallel)...")
        results = []
        
        with ThreadPoolExecutor(max_workers=len(ARXIV_MIRRORS)) as test_executor:
            futures = {test_executor.submit(_test_mirror_speed, m): m for m in ARXIV_MIRRORS}
            for future in as_completed(futures, timeout=6):
                mirror = futures[future]
                try:
                    latency = future.result()
                    logger.info(f"Mirror {mirror}: {latency:.2f}s")
                    results.append((latency, mirror))
                except Exception:
                    logger.info(f"Mirror {mirror}: failed")
        
        if results:
            results.sort(key=lambda x: x[0])
            _best_mirror = results[0][1]
        else:
            _best_mirror = ARXIV_MIRRORS[0]
        
        _mirror_selected_time = time.time()
        logger.info(f"Selected best mirror: {_best_mirror}")
        return _best_mirror


def start_download(arxiv_id, title, db_path, save_dir):
    """
    Start a background PDF download for an arXiv paper.

    Args:
        arxiv_id: arXiv paper ID (e.g., "2301.00001").
        title: Paper title for record keeping.
        db_path: Path to SQLite database.
        save_dir: Directory to save downloaded PDFs.

    Returns:
        Download record ID.
    """
    os.makedirs(save_dir, exist_ok=True)
    
    # Check if file already exists (cache hit)
    save_path = os.path.join(save_dir, f"{arxiv_id.replace('/', '_')}.pdf")
    if os.path.exists(save_path) and validate_pdf(save_path):
        file_size = os.path.getsize(save_path)
        url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.execute(
            "INSERT INTO download_records (title, url, status, pdf_path, file_size) VALUES (?, ?, 'completed', ?, ?)",
            (title, url, save_path, file_size),
        )
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        logger.info(f"Cache hit: id={record_id}, arxiv_id={arxiv_id}")
        return record_id, "completed"
    
    url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.execute(
        "INSERT INTO download_records (title, url, status) VALUES (?, ?, 'pending')",
        (title, url),
    )
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()

    _executor.submit(_download_worker, record_id, arxiv_id, save_dir, str(db_path))
    logger.info(f"Download started: id={record_id}, arxiv_id={arxiv_id}")
    return record_id, "pending"


def _download_worker(record_id, arxiv_id, save_dir, db_path):
    """Background worker: download PDF with mirror fallback and progress tracking."""
    _update_status(db_path, record_id, "downloading", progress=0)
    save_path = os.path.join(save_dir, f"{arxiv_id.replace('/', '_')}.pdf")
    temp_path = save_path + ".tmp"
    
    # Get best mirror first, then fallback to others
    best_mirror = _get_best_mirror()
    mirrors_to_try = [best_mirror] + [m for m in ARXIV_MIRRORS if m != best_mirror]
    
    session = _get_session()

    for mirror in mirrors_to_try:
        url = f"{mirror}{arxiv_id}.pdf"
        try:
            logger.info(f"Downloading from {url}")
            resp = session.get(
                url,
                stream=True,
                timeout=(CONNECTION_TIMEOUT, READ_TIMEOUT),
            )
            resp.raise_for_status()
            
            # Get content length for progress tracking
            content_length = resp.headers.get('content-length')
            total_size = int(content_length) if content_length else 0

            downloaded = 0
            last_progress_update = 0
            last_update_time = time.time()
            
            with open(temp_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Update progress every 25% or every 2 seconds
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            now = time.time()
                            if (progress >= last_progress_update + 25 or now - last_update_time >= 2) and progress > last_progress_update:
                                _update_status(db_path, record_id, "downloading", progress=progress)
                                last_progress_update = progress
                                last_update_time = now

            # Validate and move to final path
            if validate_pdf(temp_path):
                os.replace(temp_path, save_path)
                _update_status(db_path, record_id, "completed", save_path, downloaded, progress=100)
                logger.info(f"Download completed: id={record_id}, size={downloaded}")
                return
            else:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                logger.warning(f"Invalid PDF from {url}")
                
        except requests.RequestException as e:
            logger.warning(f"Download failed from {url}: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            continue

    _update_status(db_path, record_id, "failed")
    logger.error(f"Download failed for all mirrors: id={record_id}")


def _update_status(db_path, record_id, status, pdf_path=None, file_size=0, progress=None):
    """Update download record status in database."""
    conn = sqlite3.connect(db_path)
    if pdf_path:
        conn.execute(
            "UPDATE download_records SET status=?, pdf_path=?, file_size=?, progress=? WHERE id=?",
            (status, pdf_path, file_size, progress or 100, record_id),
        )
    elif progress is not None:
        conn.execute(
            "UPDATE download_records SET status=?, progress=? WHERE id=?",
            (status, progress, record_id),
        )
    else:
        conn.execute(
            "UPDATE download_records SET status=? WHERE id=?",
            (status, record_id),
        )
    conn.commit()
    conn.close()


def validate_pdf(path):
    """Validate that a file is a PDF."""
    try:
        if not os.path.exists(path):
            return False
        if os.path.getsize(path) < 1024:
            return False
        with open(path, "rb") as f:
            header = f.read(5)
            return header == b"%PDF-"
    except Exception:
        return False


def get_download_status(record_id, db_path):
    """Query download status from database."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT id, title, url, pdf_path, status, file_size, progress, timestamp FROM download_records WHERE id=?",
        (record_id,),
    ).fetchone()
    conn.close()

    if row:
        result = dict(row)
        # Ensure progress field exists
        if result.get('progress') is None:
            result['progress'] = 100 if result['status'] == 'completed' else 0
        return result
    return None


def get_all_downloads(db_path):
    """Get all download records."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, title, url, pdf_path, status, file_size, progress, timestamp FROM download_records ORDER BY timestamp DESC"
    ).fetchall()
    conn.close()
    
    results = []
    for r in rows:
        item = dict(r)
        if item.get('progress') is None:
            item['progress'] = 100 if item['status'] == 'completed' else 0
        results.append(item)
    return results


def clear_mirror_cache():
    """Clear cached best mirror to force re-testing."""
    global _best_mirror, _mirror_selected_time
    with _mirror_test_lock:
        _best_mirror = None
        _mirror_selected_time = 0
    logger.info("Mirror cache cleared")


def extract_pdf_text(pdf_path, max_chars=30000):
    """
    Extract text content from a PDF file using PyMuPDF.

    Args:
        pdf_path: Path to the PDF file.
        max_chars: Maximum characters to extract.

    Returns:
        Extracted text string, or None on failure.
    """
    try:
        import fitz  # PyMuPDF

        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return None

        doc = fitz.open(pdf_path)
        text_parts = []
        total_chars = 0

        for page in doc:
            page_text = page.get_text()
            if total_chars + len(page_text) > max_chars:
                remaining = max_chars - total_chars
                if remaining > 0:
                    text_parts.append(page_text[:remaining])
                break
            text_parts.append(page_text)
            total_chars += len(page_text)

        doc.close()

        full_text = "\n".join(text_parts).strip()
        if not full_text:
            logger.warning(f"No text extracted from PDF: {pdf_path}")
            return None

        logger.info(f"Extracted {len(full_text)} chars from PDF: {pdf_path}")
        return full_text
    except Exception as e:
        logger.error(f"PDF text extraction failed: {e}")
        return None


def get_or_download_pdf(arxiv_id, db_path, save_dir):
    """
    Get the local path of a PDF, downloading it if necessary.
    Blocks until the download completes.

    Args:
        arxiv_id: arXiv paper ID.
        db_path: Path to SQLite database.
        save_dir: Directory to save downloaded PDFs.

    Returns:
        Local file path if available, or None.
    """
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"{arxiv_id.replace('/', '_')}.pdf")

    # Check if already downloaded and valid
    if os.path.exists(save_path) and validate_pdf(save_path):
        return save_path

    # Download synchronously
    logger.info(f"Downloading PDF for full analysis: {arxiv_id}")
    best_mirror = _get_best_mirror()
    mirrors_to_try = [best_mirror] + [m for m in ARXIV_MIRRORS if m != best_mirror]
    session = _get_session()
    temp_path = save_path + ".tmp"

    for mirror in mirrors_to_try:
        url = f"{mirror}{arxiv_id}.pdf"
        try:
            resp = session.get(url, stream=True, timeout=(CONNECTION_TIMEOUT, READ_TIMEOUT))
            resp.raise_for_status()
            with open(temp_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)
            if validate_pdf(temp_path):
                os.replace(temp_path, save_path)
                logger.info(f"PDF downloaded for analysis: {arxiv_id}")
                return save_path
            else:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        except requests.RequestException as e:
            logger.warning(f"Download failed from {url}: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            continue

    logger.error(f"Failed to download PDF for analysis: {arxiv_id}")
    return None
