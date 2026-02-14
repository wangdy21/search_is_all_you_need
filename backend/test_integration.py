"""Integration test script for search_is_all_you_need."""
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["FLASK_ENV"] = "development"

from backend.app import app


def test_all():
    passed = 0
    failed = 0

    with app.test_client() as c:
        # Test 1: Root serves frontend HTML
        r = c.get("/")
        ok = r.status_code == 200 and len(r.data) > 100
        m = re.search(rb"<title>(.*?)</title>", r.data)
        title = m.group(1).decode() if m else "N/A"
        print(f"[{'PASS' if ok else 'FAIL'}] GET / -> {r.status_code}, title={title}")
        passed += ok
        failed += (not ok)

        # Test 2: arXiv search
        r = c.post("/api/search", json={"query": "deep learning", "sources": ["arxiv"]})
        data = r.get_json()
        total = data.get("total", 0)
        ok = r.status_code == 200 and total > 0
        print(f"[{'PASS' if ok else 'FAIL'}] POST /api/search -> {r.status_code}, total={total}")
        if ok:
            item = data["results"][0]
            print(f"  First: [{item.get('category')}] {item.get('title', '')[:55]}")
            print(f"  PDF: {item.get('extra', {}).get('pdf_url', 'N/A')[:60]}")
        passed += ok
        failed += (not ok)

        # Test 3: History has entry
        r = c.get("/api/history")
        data = r.get_json()
        count = len(data.get("history", []))
        ok = r.status_code == 200 and count > 0
        print(f"[{'PASS' if ok else 'FAIL'}] GET /api/history -> {r.status_code}, entries={count}")
        passed += ok
        failed += (not ok)

        # Test 4: Param validation
        r = c.post("/api/search", json={})
        ok = r.status_code == 400
        print(f"[{'PASS' if ok else 'FAIL'}] Validation: search empty -> {r.status_code}")
        passed += ok
        failed += (not ok)

        r = c.post("/api/analysis/summarize", json={})
        ok = r.status_code == 400
        print(f"[{'PASS' if ok else 'FAIL'}] Validation: summarize empty -> {r.status_code}")
        passed += ok
        failed += (not ok)

        r = c.post("/api/download/arxiv", json={})
        ok = r.status_code == 400
        print(f"[{'PASS' if ok else 'FAIL'}] Validation: download empty -> {r.status_code}")
        passed += ok
        failed += (not ok)

        # Test 5: Download status 404
        r = c.get("/api/download/status/999")
        ok = r.status_code == 404
        print(f"[{'PASS' if ok else 'FAIL'}] GET /api/download/status/999 -> {r.status_code}")
        passed += ok
        failed += (not ok)

        # Test 6: Download history
        r = c.get("/api/download/history")
        ok = r.status_code == 200
        print(f"[{'PASS' if ok else 'FAIL'}] GET /api/download/history -> {r.status_code}")
        passed += ok
        failed += (not ok)

        # Test 7: Clear history
        r = c.delete("/api/history")
        ok = r.status_code == 200
        print(f"[{'PASS' if ok else 'FAIL'}] DELETE /api/history -> {r.status_code}")
        passed += ok
        failed += (not ok)

        r = c.get("/api/history")
        data = r.get_json()
        ok = len(data.get("history", [])) == 0
        print(f"[{'PASS' if ok else 'FAIL'}] History cleared -> entries={len(data.get('history', []))}")
        passed += ok
        failed += (not ok)

    print(f"\n{'='*40}")
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = test_all()
    sys.exit(0 if success else 1)
