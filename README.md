# StockSense India - prepared by 
-SHABBER 
-VENKATA DHEERAJ
-SURENDRA

Terminal-based Indian stock dashboard: search a company (typos auto-corrected),
see live NSE/BSE price, today's % change, 52-week high/low, week/month/year
performance, corporate announcements, and recent news.

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Make sure a `.env` file exists in this root folder (next to this README)
   containing your RapidAPI key:
   ```
   RAPIDAPI_KEY=your_key_here
   ```
   (A working `.env` is already included, but rotate the key on your
   RapidAPI dashboard since it has been shared in chat.)

3. Run it:
   ```
   python app/main.py
   ```

## Usage

```
Search company: tsc
  (no exact match for 'tsc', trying spelling correction...)
  Did you mean: Tata Consultancy Services? Fetching that...
```

Type `exit` to quit.

## Project layout

```
StockSence India/
├── app/
│   ├── config.py       # loads RAPIDAPI_KEY from .env
│   ├── api_client.py   # calls /stock, /industry_search, /historical_data
│   ├── utils.py         # fuzzy name matching + price-change math
│   └── main.py          # terminal loop / dashboard
├── data/                 # (unused placeholder for now)
├── tests/
│   └── test_api.py
├── .env                  # your RapidAPI key (keep private, gitignored)
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```
