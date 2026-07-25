import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from utils import safe_float, resolve_company

def test_safe_float():
    assert safe_float("1,234.56") == 1234.56
    assert safe_float("Rs. 2069.00") == 2069.0
    assert safe_float("-1.25%") == -1.25
    assert safe_float("N/A") is None
    assert safe_float("-") is None
    assert safe_float(None) is None


def test_resolve_company():
    candidates = [
        {"commonName": "Tata Consultancy Services Limited", "exchangeCodeNsi": "TCS"},
        {"commonName": "Reliance Industries Limited", "exchangeCodeNsi": "RELIANCE"}
    ]
    # Typo search
    match = resolve_company("tata", candidates)
    assert match is not None
    assert match["exchangeCodeNsi"] == "TCS"
    
    # Far-off search
    assert resolve_company("xyz", candidates) is None
