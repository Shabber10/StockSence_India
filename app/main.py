"""
main.py
StockSense India - terminal stock dashboard.
Run with:  python main.py
"""

import json

from api_client import search_companies, get_stock, get_historical
from utils import resolve_company, extract_price_series, pct_change, fmt_money, fmt_pct

LINE = "=" * 64


def find_stock(user_query):
    """
    Step 1: try the query directly against /stock (it already handles
             full names, short names and common names decently well).
    Step 2: if that fails, use /industry_search + fuzzy matching to
             correct typos, then retry /stock with the corrected name.
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
    ticker = (
        data.get("tickerId")
        or data.get("symbol")
        or data.get("nseSymbol")
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


def print_performance_section(stock_name):
    print("\n PERFORMANCE (from historical data)")

    # Past week -> derive from the 1-month series, last ~5 trading days
    month_hist = get_historical(stock_name, period="1m")
    month_series = extract_price_series(month_hist)

    week_result = pct_change(month_series, last_n=5)
    if week_result:
        price, change, pct = week_result
        print(f"   Past week : {fmt_money(price)}  ({fmt_pct(pct)})")
    else:
        print("   Past week : N/A")

    if month_series:
        price, change, pct = pct_change(month_series)
        print(f"   Past month: {fmt_money(price)}  ({fmt_pct(pct)})")
    else:
        print("   Past month: N/A")

    # Past year
    year_hist = get_historical(stock_name, period="1yr")
    year_series = extract_price_series(year_hist)
    if year_series:
        price, change, pct = pct_change(year_series)
        print(f"   Past year : {fmt_money(price)}  ({fmt_pct(pct)})")
    else:
        print("   Past year : N/A")


def print_corporate_actions(data):
    print("\n CORPORATE ANNOUNCEMENTS")
    actions = data.get("stockCorporateActionData")

    # This field can come back as a list or a dict depending on the stock;
    # handle both so the app doesn't crash.
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
        purpose = action.get("purpose") or action.get("subject") or "Action"
        date = action.get("exDate") or action.get("date") or "N/A"
        print(f"   - {purpose}  (Ex-date: {date})")


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
    print_performance_section(data.get("companyName") or user_query)
    print_corporate_actions(data)
    print_news(data)
    print(f"\n{LINE}\n")


def debug_dump(company):
    """
    Fetches the raw /stock response and saves it to debug_output.json
    so the exact field names this API returns can be inspected.
    Usage in the app: type 'debug tcs'
    """
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
    main()
