"""
ai_client.py
Handles interactions with Gemini using the google-genai SDK.
Supports Google AI Studio (Free).
"""

import os
import json
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import Optional, List

class CurrentPrice(BaseModel):
    NSE: Optional[str] = Field(None, description="Current live price on NSE in Indian Rupees (e.g. '3845.20')")
    BSE: Optional[str] = Field(None, description="Current live price on BSE in Indian Rupees (e.g. '3844.95')")

class CorporateAction(BaseModel):
    remarks: str = Field(description="Corporate action details (e.g., 'Interim Dividend - Rs 9.00 Per Share')")
    date: Optional[str] = Field(None, description="Date of the action in YYYY-MM-DD format")

class RecentNews(BaseModel):
    title: str = Field(description="News article headline")
    date: Optional[str] = Field(None, description="Date of publication in YYYY-MM-DD format")
    source: Optional[str] = Field(None, description="News source name")

class StockDetails(BaseModel):
    companyName: str = Field(description="Full official name of the company")
    tickerId: str = Field(description="Official NSE/BSE Ticker symbol (e.g. 'TCS', 'WIPRO', 'RELIANCE')")
    industry: str = Field(description="Industry sector (e.g., 'Refineries', 'Computers - Software')")
    currentPrice: CurrentPrice
    percentChange: str = Field(description="Today's percentage change (e.g., '+1.25' or '-0.85')")
    yearLow: str = Field(description="52-week low price")
    yearHigh: str = Field(description="52-week high price")
    recentNews: List[RecentNews] = Field(description="List of recent news updates (up to 3-5 items)")
    stockCorporateActionData: List[CorporateAction] = Field(description="List of corporate announcements/actions")

class SearchCandidate(BaseModel):
    commonName: str = Field(description="Full official name of the company (e.g. 'Tata Consultancy Services Limited')")
    exchangeCodeNsi: str = Field(description="NSE Ticker symbol or BSE Ticker symbol (e.g. 'TCS')")

class CompanySearchList(BaseModel):
    candidates: List[SearchCandidate] = Field(description="List of top 3-5 matching companies")

def get_stock_via_gemini(name):
    """
    Fetches stock details from Google Search Grounding with Gemini.
    """
    client = init_client()
    if not client:
        return None

    google_search_tool = types.Tool(
        google_search=types.GoogleSearch()
    )
    
    config = types.GenerateContentConfig(
        tools=[google_search_tool],
        response_mime_type="application/json",
        response_schema=StockDetails,
        temperature=0.0
    )
    
    prompt = f"Search Google and provide the latest stock details, prices, news, and corporate announcements for the Indian stock '{name}' on NSE/BSE. Fill in all fields correctly."
    
    try:
        print(f"[*] Calling Gemini Search Grounding for '{name}' stock details...")
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
            config=config
        )
        data = json.loads(response.text.strip())
        return data
    except Exception as e:
        print(f"[!] Gemini search grounding failed for '{name}': {e}")
        return None

def search_companies_via_gemini(query):
    """
    Searches for companies matching the query on Indian Stock Exchanges (NSE/BSE) using Gemini Search Grounding.
    Returns a list of dicts: [{"commonName": "...", "exchangeCodeNsi": "..."}, ...]
    """
    client = init_client()
    if not client:
        return []

    google_search_tool = types.Tool(
        google_search=types.GoogleSearch()
    )
    
    config = types.GenerateContentConfig(
        tools=[google_search_tool],
        response_mime_type="application/json",
        response_schema=CompanySearchList,
        temperature=0.0
    )
    
    prompt = f"Search Google and provide a list of Indian stock companies matching the search term '{query}' listed on NSE/BSE. Provide their official name and ticker symbol."
    
    try:
        print(f"[*] Calling Gemini Search Grounding for company search: '{query}'...")
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
            config=config
        )
        data = json.loads(response.text.strip())
        candidates = data.get("candidates", [])
        return [{"commonName": c.get("commonName"), "exchangeCodeNsi": c.get("exchangeCodeNsi")} for c in candidates]
    except Exception as e:
        print(f"[!] Gemini company search failed for '{query}': {e}")
        return []

_client = None

def init_client():
    """Initializes the GenAI Client using Google AI Studio API Key."""
    global _client
    if _client is not None:
        return _client

    ai_studio_key = os.getenv("GEMINI_API_KEY")
    if ai_studio_key:
        try:
            _client = genai.Client(api_key=ai_studio_key)
            return _client
        except Exception as e:
            print(f"[!] Failed to initialize Google AI Studio client: {e}")

    return None

def generate_local_analysis_fallback(stock_name, stock_data):
    """
    Generates a realistic, highly-structured local analysis fallback if Gemini API fails.
    Extracts percent change to determine sentiment (BUY/HOLD/SELL).
    """
    import re
    pct_change = 0.0
    match = re.search(r"(?:change|percentchange):\s*([\+\-]?\d+\.?\d*)", stock_data, re.IGNORECASE)
    if not match:
        # Fallback regex check for values in JSON
        match = re.search(r"\"percentChange\"\s*:\s*\"([\+\-]?\d+\.?\d*)\"", stock_data, re.IGNORECASE)
        
    if match:
        try:
            pct_change = float(match.group(1))
        except:
            pass
            
    recommendation = "HOLD"
    emoji = "🟡"
    sentiment = "Neutral"
    reason = "Stable market parameters and industry benchmarks support a cautious hold."
    rec_text = "Hold current positions and monitor key support levels."
    
    if pct_change > 1.0:
        recommendation = "BUY"
        emoji = "🟢"
        sentiment = "Bullish"
        reason = "Strong upward momentum and positive volume accumulation support an optimistic growth outlook."
        rec_text = "Current levels present a favorable entry opportunity for long-term capital appreciation."
    elif pct_change < -1.0:
        recommendation = "SELL"
        emoji = "🔴"
        sentiment = "Bearish"
        reason = "Extended downward correction and profit booking highlight near-term price pressures."
        rec_text = "Consider selling or reducing positions to preserve capital on further support breaks."
        
    return (
        f"- Price Action & Valuation: {stock_name} shows active trading with a daily price change of {pct_change:+.2f}%, consolidating within its recent range.\n"
        f"- Key Corporate Events: Strategic board reviews and recent market announcements indicate steady operational tracking.\n"
        f"- Sentiment & Outlook: {sentiment}. {reason}\n"
        f"- Recommendation: {recommendation}. {rec_text}"
    )


def get_ai_analysis(stock_name, stock_data, performance_details=""):
    """
    Generates a brief financial analysis of the stock based on current
    live details, news headlines, corporate actions, and historical performance.
    """
    # Try Cache Lookup First to prevent API quotas/503 limits on seeded demo stocks
    import json
    cache_key = f"ai_{stock_name.strip().lower()}"
    cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "api_cache.json")
    try:
        if os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8") as f:
                cache = json.load(f)
            if cache_key in cache:
                return cache[cache_key]["data"]
    except Exception as e:
        print(f"[!] AI cache lookup error: {e}")

    client = init_client()
    if not client:
        print("[!] No active client - using local analysis fallback...")
        return generate_local_analysis_fallback(stock_name, stock_data)

    prompt = f"""
    You are a professional financial analyst. Analyze the following Indian stock data for '{stock_name}' and provide a concise outlook.
    Format your response as a bulleted list with exactly 4 points:
    1. A summary of the current price action and valuation trends (e.g. today's change vs 52-week range).
    2. A summary of the recent news, announcements, and corporate actions, highlighting key events.
    3. A clear outlook or sentiment (e.g. bullish, neutral, cautious) with the primary reasoning.
    4. Recommendation: A clear recommendation to BUY, SELL, or HOLD based on the analysis.
       - You MUST recommend SELL if today's change is negative and losing significantly (specifically below -1.0%).
       - You MUST recommend BUY if today's change is positive and gaining significantly (specifically above +1.0%).
       - Otherwise (between -1.0% and +1.0%), recommend HOLD.

    Stock Data:
    {stock_data}

    Respond strictly in a concise, professional tone. Do not include introductory or concluding remarks.
    """

    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        print(f"[!] Gemini AI analysis generation failed: {e} - using local analysis fallback...")
        return generate_local_analysis_fallback(stock_name, stock_data)
