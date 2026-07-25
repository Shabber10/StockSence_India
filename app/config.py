"""
config.py
Loads your Gemini API key from a local .env file (never hardcode it here).
"""

import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
API_KEY = os.getenv("RAPIDAPI_KEY")

BASE_URL = "https://indian-stock-exchange-api2.p.rapidapi.com"
HOST = "indian-stock-exchange-api2.p.rapidapi.com"

HEADERS = {
    "x-rapidapi-key": API_KEY or "",
    "x-rapidapi-host": HOST,
}

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY not found in environment variables."
    )

if not API_KEY:
    raise RuntimeError(
        "RAPIDAPI_KEY not found in environment variables."
    )

