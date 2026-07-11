"""
utils.py
Spelling-correction (fuzzy match) and helper functions for formatting
and calculating price changes from historical data.
"""

from thefuzz import process


def resolve_company(query, candidates):
    """
    Given what the user typed and a list of candidate dicts from
    /industry_search, return the best-matching candidate (handles
    typos like 'tsc' -> 'TCS', 'relaince' -> 'Reliance').
    """
    if not candidates:
        return None

    names = [c.get("commonName", "") for c in candidates if c.get("commonName")]
    if not names:
        return None

    best_name, score = process.extractOne(query, names)
    if score < 45:  # too dissimilar, don't guess wildly
        return None

    for c in candidates:
        if c.get("commonName") == best_name:
            return c
    return None


def extract_price_series(historical_json):
    """
    Pulls the plain 'Price' series out of the /historical_data response.
    Returns a list of (date_str, float_price) tuples, oldest first.
    """
    if not historical_json or "datasets" not in historical_json:
        return []

    for dataset in historical_json["datasets"]:
        if dataset.get("metric") == "Price":
            series = []
            for point in dataset.get("values", []):
                try:
                    date_str, price = point[0], float(point[1])
                    series.append((date_str, price))
                except (IndexError, ValueError, TypeError):
                    continue
            return series
    return []


def pct_change(series, last_n=None):
    """
    Given a price series [(date, price), ...], compute the % change
    from the first to the last point. If last_n is given, only look
    at the last N points (e.g. last 5 trading days ~= 1 week).
    """
    if not series or len(series) < 2:
        return None

    window = series[-last_n:] if last_n else series
    if len(window) < 2:
        return None

    start_price = window[0][1]
    end_price = window[-1][1]
    if start_price == 0:
        return None

    change = end_price - start_price
    pct = (change / start_price) * 100
    return end_price, change, pct


def safe_float(value):
    """
    Converts strings like '1,234.56', '+1.25%', ' 2069.00 ' into floats.
    Returns None if it can't be converted.
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        cleaned = str(value).strip().replace(",", "").replace("%", "").replace("Rs.", "")
        if cleaned in ("", "-", "N/A"):
            return None
        return float(cleaned)
    except (ValueError, TypeError):
        return None


def fmt_money(value):
    num = safe_float(value)
    if num is None:
        return "N/A"
    return f"Rs.{num:,.2f}"


def fmt_pct(value):
    num = safe_float(value)
    if num is None:
        return "N/A"
    sign = "+" if num >= 0 else ""
    return f"{sign}{num:.2f}%"
