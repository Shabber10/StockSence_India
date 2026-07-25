import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from ai_client import init_client, get_ai_analysis

def test_init_client_success_or_graceful_fail():
    """Verify that init_client returns a Client or None without crashing."""
    client = init_client()
    assert client is None or hasattr(client, "models")


def test_get_ai_analysis_graceful_fail_no_key():
    """Verify that it returns error string gracefully when api key is missing."""
    import ai_client
    original_api_key = os.environ.get("GEMINI_API_KEY")
    
    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]
    ai_client._client = None

    result = get_ai_analysis("Test Stock", "Test Data", "Test Perf")
    assert "AI Analysis unavailable" in result

    # Restore
    if original_api_key:
        os.environ["GEMINI_API_KEY"] = original_api_key
    ai_client._client = None


