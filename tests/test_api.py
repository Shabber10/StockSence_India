"""
Basic smoke tests. Run with: python -m pytest tests/
(Requires a valid GEMINI_API_KEY in .env)
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from api_client import get_stock, search_companies  # noqa: E402


def test_search_returns_list():
    results = search_companies("tata")
    assert isinstance(results, list)


def test_get_stock_known_company():
    data = get_stock("Reliance")
    if data is None:
        # network/API might be unavailable in CI - don't hard fail
        return
    assert "companyName" in data


if __name__ == "__main__":
    test_search_returns_list()
    test_get_stock_known_company()
    print("Smoke tests passed (or skipped gracefully).")
