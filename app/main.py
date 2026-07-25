"""
main.py
StockSense India - entry point. Launches Flask web server by default, or runs a terminal dashboard with --cli.
"""

import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from api_client import search_companies, get_stock
from utils import resolve_company, fmt_money, fmt_pct
from ai_client import get_ai_analysis

LINE = "=" * 64


def find_stock(user_query):
    """
    Step 1: try the query directly against /stock
    Step 2: if that fails, use spelling correction to find match.
    """
    data = get_stock(user_query)
    if data and data.get("companyName"):
        return data

    print(f"  (no exact match for '{user_query}', trying spelling correction...)")
    candidates = search_companies(user_query)
    match = resolve_company(user_query, candidates)
    if not match:
        return None

    corrected_name = match.get("commonName")
    print(f"  Did you mean: {corrected_name}? Fetching that...")
    return get_stock(corrected_name)


def print_price_section(data):
    profile = data.get("companyProfile") or {}
    ticker = (
        data.get("tickerId")
        or data.get("symbol")
        or data.get("nseSymbol")
        or profile.get("exchangeCodeNse")
        or profile.get("exchangeCodeBse")
        or data.get("exchangeCodeNsi")
        or "N/A"
    )
    print(f"\n{LINE}")
    print(f" {data.get('companyName', 'N/A')}  [{ticker}]")
    print(f" Industry: {data.get('industry', 'N/A')}")
    print(LINE)

    current_price = data.get("currentPrice") or {}
    print(" LIVE PRICE")
    print(f"   NSE : {fmt_money(current_price.get('NSE'))}")
    print(f"   BSE : {fmt_money(current_price.get('BSE'))}")
    print(f"   Change today: {fmt_pct(data.get('percentChange'))}")

    print("\n 52-WEEK RANGE")
    print(f"   High: {fmt_money(data.get('yearHigh'))}   Low: {fmt_money(data.get('yearLow'))}")


def print_corporate_actions(data):
    print("\n CORPORATE ANNOUNCEMENTS")
    actions = data.get("stockCorporateActionData")

    items = []
    if isinstance(actions, list):
        items = actions
    elif isinstance(actions, dict):
        for v in actions.values():
            if isinstance(v, list):
                items.extend(v)

    if not items:
        print("   No corporate actions listed right now.")
        return

    for action in items[:6]:
        purpose = (
            action.get("remarks")
            or action.get("purpose")
            or action.get("subject")
            or "Action"
        )
        if isinstance(purpose, str) and not purpose.strip():
            purpose = "Action/Meeting"
        date = (
            action.get("xdDate")
            or action.get("agmDate")
            or action.get("boardMeetDate")
            or action.get("exDate")
            or action.get("date")
            or "N/A"
        )
        print(f"   - {purpose}  (Date: {date})")


def print_news(data):
    print("\n LATEST NEWS / UPDATES")
    news = data.get("recentNews")

    items = news if isinstance(news, list) else []
    if not items:
        print("   No recent news available.")
        return

    for item in items[:6]:
        title = item.get("title") or item.get("headline") or "Untitled"
        date = item.get("date") or item.get("publishedAt") or ""
        date_str = f" ({date})" if date else ""
        print(f"   * {title}{date_str}")


def show_dashboard(user_query):
    print(f"\nSearching for '{user_query}'...")
    data = find_stock(user_query)

    if not data:
        print(f"\nCouldn't find a stock matching '{user_query}'. Try a different spelling.")
        return

    print_price_section(data)
    print_corporate_actions(data)
    print_news(data)

    # Gather data for AI analysis
    company_name = data.get("companyName") or user_query
    current_price = data.get("currentPrice") or {}

    raw_actions = []
    actions = data.get("stockCorporateActionData")
    if isinstance(actions, list):
        raw_actions = actions[:3]
    elif isinstance(actions, dict):
        for v in actions.values():
            if isinstance(v, list):
                raw_actions.extend(v[:2])

    news_titles = [str(item.get("title") or item.get("headline") or "Untitled") for item in (data.get("recentNews") or [])[:3]]

    ai_input_data = (
        f"NSE Current Price: {fmt_money(current_price.get('NSE'))}\n"
        f"BSE Current Price: {fmt_money(current_price.get('BSE'))}\n"
        f"Today's Change: {fmt_pct(data.get('percentChange'))}\n"
        f"52-Week High: {fmt_money(data.get('yearHigh'))}\n"
        f"52-Week Low: {fmt_money(data.get('yearLow'))}\n"
        f"Corporate Announcements: {json.dumps(raw_actions)}\n"
        f"News Headlines: {', '.join(news_titles)}"
    )

    print("\n AI ANALYSIS & OUTLOOK (Gemini via Vertex AI)")
    print("   Generating AI insights...")
    ai_outlook = get_ai_analysis(company_name, ai_input_data)
    print(f"\n{ai_outlook}")

    print(f"\n{LINE}\n")


def debug_dump(company):
    data = get_stock(company)
    if not data:
        print("No data returned - nothing to dump.")
        return
    with open("debug_output.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved raw response to debug_output.json ({len(data)} top-level keys).")
    print("Top-level keys:", list(data.keys()))


def main():
    print(LINE)
    print(" STOCKSENSE INDIA - Terminal Stock Dashboard")
    print(" Type a company name (e.g. 'tcs', 'relaince', 'infy') or 'exit'")
    print(LINE)

    while True:
        query = input("\nSearch company: ").strip()
        if not query:
            continue
        if query.lower() in ("exit", "quit"):
            print("Goodbye!")
            break
        if query.lower().startswith("debug "):
            debug_dump(query[6:].strip())
            continue
        show_dashboard(query)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        main()
    else:
        try:
            from server import run_server
            run_server()
        except ImportError:
            # Fallback in case of import path anomalies
            import os
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from server import run_server
            run_server()
