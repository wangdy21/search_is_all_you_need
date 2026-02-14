import os
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor

import requests

from backend.utils.logger import get_logger

logger = get_logger("pdf_download_skill")

# Global download thread pool
_executor = ThreadPoolExecutor(max_workers=3)

ARXIV_MIRRORS = [
    "https://arxiv.org/pdf/",
    "https://cn.arxiv.org/pdf/",
]


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
    return record_id


def _download_worker(record_id, arxiv_id, save_dir, db_path):
    """Background worker: download PDF with mirror fallback."""
    _update_status(db_path, record_id, "downloading")
    save_path = os.path.join(save_dir, f"{arxiv_id.replace('/', '_')}.pdf")

    for mirror in ARXIV_MIRRORS:
        url = f"{mirror}{arxiv_id}.pdf"
        try:
            logger.info(f"Downloading from {url}")
            resp = requests.get(
                url,
                stream=True,
                timeout=300,
                headers={"User-Agent": "Mozilla/5.0 (compatible; SearchBot/1.0)"},
            )
            resp.raise_for_status()

            total = 0
            with open(save_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
                    total += len(chunk)

            if validate_pdf(save_path):
                _update_status(db_path, record_id, "completed", save_path, total)
                logger.info(f"Download completed: id={record_id}, size={total}")
                return
            else:
                os.remove(save_path)
                logger.warning(f"Invalid PDF from {url}")
        except requests.RequestException as e:
            logger.warning(f"Download failed from {url}: {e}")
            if os.path.exists(save_path):
                os.remove(save_path)
            continue

    _update_status(db_path, record_id, "failed")
    logger.error(f"Download failed for all mirrors: id={record_id}")


def _update_status(db_path, record_id, status, pdf_path=None, file_size=0):
    """Update download record status in database."""
    conn = sqlite3.connect(db_path)
    if pdf_path:
        conn.execute(
            "UPDATE download_records SET status=?, pdf_path=?, file_size=? WHERE id=?",
            (status, pdf_path, file_size, record_id),
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
        "SELECT id, title, url, pdf_path, status, file_size, timestamp FROM download_records WHERE id=?",
        (record_id,),
    ).fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def get_all_downloads(db_path):
    """Get all download records."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, title, url, pdf_path, status, file_size, timestamp FROM download_records ORDER BY timestamp DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
