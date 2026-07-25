"""
utils.py
Spelling-correction (fuzzy match) and helper functions for formatting
and calculating price changes from historical data.
"""

from thefuzz import process, fuzz


def resolve_company(query, candidates):
    """
    Given what the user typed and a list of candidate dicts, return the best-matching
    candidate. Cleans stop-words (like 'bank', 'limited') to prevent wrong matches.
    """
    if not candidates:
        return None

    query_clean = query.strip().lower()
    
    # 1. Direct exact or substring match on ticker
    for c in candidates:
        ticker = c.get("exchangeCodeNsi", "").strip().lower()
        if ticker and (query_clean == ticker or ticker in query_clean):
            return c

    # 2. Match after cleaning common stop words
    stop_words = ["limited", "ltd", "industries", "services", "consultancy", "bank", "co", "corp", "corporation"]
    
    def clean_name(n):
        words = n.lower().split()
        filtered = [w for w in words if w not in stop_words]
        return " ".join(filtered) if filtered else n.lower()

    query_words = clean_name(query_clean)
    
    best_candidate = None
    best_score = 0
    
    for c in candidates:
        c_name = c.get("commonName", "")
        if not c_name:
            continue
        
        c_name_clean = clean_name(c_name)
        
        # Check if the query is a substring of the cleaned name or vice versa
        if query_words and (query_words in c_name_clean or c_name_clean in query_words):
            return c
            
        # Calculate ratio of remaining keywords
        score = fuzz.ratio(query_words, c_name_clean)
        if score > best_score:
            best_score = score
            best_candidate = c
            
    if best_score >= 60:
        return best_candidate
        
    return None



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
