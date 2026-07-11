"""
api_client.py
All network calls to the Indian Stock Exchange API (RapidAPI) live here.
"""

import requests
from config import BASE_URL, HEADERS

TIMEOUT = 12


def search_companies(query):
    """
    Uses /industry_search to find companies matching a (possibly misspelled)
    name. Returns a list of dicts like:
    {"commonName": "Tata Consultancy Services", "exchangeCodeNsi": "TCS", ...}
    """
    try:
        r = requests.get(
            f"{BASE_URL}/industry_search",
            headers=HEADERS,
            params={"query": query},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, list) else []
    except requests.RequestException as e:
        print(f"[!] Search request failed: {e}")
        return []


def get_stock(name):
    """
    Uses /stock to get full details for a company: current price on
    BSE/NSE, year high/low, corporate actions, recent news, etc.
    'name' can be a full name, short name, or ticker.
    """
    try:
        r = requests.get(
            f"{BASE_URL}/stock",
            headers=HEADERS,
            params={"name": name},
            timeout=TIMEOUT,
        )
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        print(f"[!] Could not fetch stock data: {e}")
        return None


def get_historical(stock_name, period="1yr", filter_="price"):
    """
    Uses /historical_data to get a price time series.
    period: one of 1m, 6m, 1yr, 3yr, 5yr, 10yr, max
    """
    try:
        r = requests.get(
            f"{BASE_URL}/historical_data",
            headers=HEADERS,
            params={"stock_name": stock_name, "period": period, "filter": filter_},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        print(f"[!] Could not fetch historical data ({period}): {e}")
        return None
