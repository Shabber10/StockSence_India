"""
server.py
Flask web server for StockSense India. Exposes stock data, historical trends,
and AI analysis endpoints, and serves the static HTML/CSS/JS frontend.
"""

import os
import json
import sys
from flask import Flask, jsonify, request, send_from_directory

# Resolve import paths to ensure backend files can be loaded
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_client import search_companies, get_stock
from utils import resolve_company, fmt_money, fmt_pct, safe_float
from ai_client import get_ai_analysis

# Initialize Flask with the static directory pointing to "app/static"
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="")

@app.route("/")
def index():
    """Serves the dashboard home page."""
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/status", methods=["GET"])
def api_get_status():
    """Checks the status of API keys."""
    gemini_present = bool(os.getenv("GEMINI_API_KEY"))
    return jsonify({
        "status_badges": {
            "gemini": "OK" if gemini_present else "Missing"
        }
    })

@app.route("/api/stock", methods=["GET"])
def api_get_stock():
    """
    Exposes stock detail lookup.
    Example: GET /api/stock?query=tcs
    Resolves spelling errors automatically.
    """
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify({"error": "Missing 'query' parameter"}), 400

    # Step 1: Query stock directly
    data = get_stock(query)
    corrected_name = None

    # Step 2: Spell correction fallback
    if not data or not data.get("companyName"):
        candidates = search_companies(query)
        match = resolve_company(query, candidates)
        if match:
            corrected_name = match.get("commonName")
            data = get_stock(corrected_name)

    if not data or not data.get("companyName"):
        return jsonify({"error": f"Could not find details for '{query}'"}), 404
    # Check key credentials statuses to report on front-end
    gemini_present = bool(os.getenv("GEMINI_API_KEY"))

    return jsonify({
        "data": data,
        "corrected_name": corrected_name,
        "status_badges": {
            "gemini": "OK" if gemini_present else "Missing"
        }
    })


@app.route("/api/ai", methods=["POST"])
def api_post_ai():
    """
    Exposes Gemini AI analysis generation.
    Post payload structure:
    {
      "stock_name": "Tata Consultancy Services",
      "stock_data_summary": "...",
      "performance_details": "..."
    }
    """
    payload = request.json or {}
    stock_name = payload.get("stock_name", "").strip()
    stock_data = payload.get("stock_data_summary", "").strip()
    performance_details = payload.get("performance_details", "").strip()

    if not stock_name:
        return jsonify({"error": "Missing 'stock_name' in JSON payload"}), 400

    ai_outlook = get_ai_analysis(stock_name, stock_data, performance_details)
    return jsonify({
        "outlook": ai_outlook
    })

def run_server(port=5000):
    """Launches the local Flask server."""
    print(f"[*] Starting StockSense India Web Server on http://127.0.0.1:{port}")
    
    import threading
    import webbrowser
    threading.Timer(1.2, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
    
    # Run multithreaded server for UI responsive loads
    app.run(host="127.0.0.1", port=port, debug=False, threaded=True)

if __name__ == "__main__":
    run_server()
