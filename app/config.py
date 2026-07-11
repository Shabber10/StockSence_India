"""
config.py
Loads your RapidAPI key from a local .env file (never hardcode it here).
"""

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("RAPIDAPI_KEY")

BASE_URL = "https://indian-stock-exchange-api2.p.rapidapi.com"
HOST = "indian-stock-exchange-api2.p.rapidapi.com"

HEADERS = {
    "x-rapidapi-key": API_KEY or "",
    "x-rapidapi-host": HOST,
}

if not API_KEY:
    raise RuntimeError(
        "RAPIDAPI_KEY not found.\n"
        "Create a file named '.env' in this folder with this line:\n"
        "RAPIDAPI_KEY=your_key_here"
    )
