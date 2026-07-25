# StockSense India 📈✨

**Prepared by:**
* SHABBER
* VENKATA DHEERAJ
* SURENDRA

StockSense India is a modern, responsive **Glassmorphic Financial Web Dashboard** that provides real-time stock analytics, news headlines, corporate announcements, and AI-powered recommendations (BUY/SELL/HOLD) for all listed companies on the National Stock Exchange (NSE) of India.

The project features a **Python Flask backend** integrated with a keyless **Yahoo Finance resolver** and the **Gemini API** for automated financial analysis, paired with a stunning frontend styled using curated vanilla CSS glassmorphism.

---

## 🌟 Key Features

1. **Complete NSE Database Search (2,360+ Stocks)**:
   - Search autocomplete dropdown containing every single equity listed on the NSE, downloaded directly from the official exchange archives.
   - Typo tolerance and fuzzy matching support (e.g. typing `"relicance"` will match `"Reliance Industries Ltd"`).

2. **Real-time Live Stock Data (Keyless & Sub-second)**:
   - Fetches authentic market quotes, daily price shifts, and 52-week High/Low metrics directly from Yahoo Finance query API.
   - Dual-host query retry fallback (`query2` / `query1`) to bypass rate throttles or gateway latencies.
   - Live-updating 52-week range slider.

3. **AI Financial Outlook Bullets**:
   - Generates professional 4-bullet point outlook summaries combining price action, corporate announcements, and market sentiment.
   - Falls back to a local rule-based analysis generator if offline or out of API quota.

4. **Aligned Recommendation Badges**:
   - Displays color-coded glassmorphic badges (**🟢 BUY**, **🔴 SELL**, **🟡 HOLD**) strictly aligned with price trends:
     - **SELL**: Daily drop greater than **-1.0%**.
     - **BUY**: Daily gain greater than **+1.0%**.
     - **HOLD**: Flat trading day (between **-1.0%** and **+1.0%**).

5. **Keyboard Navigation & Fully Responsive**:
   - Full keyboard navigation support (Up/Down arrow keys to highlight, Enter to search, Escape to dismiss the dropdown list).
   - Fully optimized layout adapting from wide desktop monitors to mobile phones.

---

## 🛠️ Tech Stack
- **Backend**: Python 3.11+, Flask, `requests`, `python-dotenv`
- **Frontend**: Vanilla HTML5, CSS3 (Custom Glassmorphism properties), JavaScript (ES6)
- **APIs**: Yahoo Finance (Market Data), Google Gemini API (Financial Analysis)

---

## 🚀 Local Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Shabber10/StockSence_India.git
   cd StockSence_India
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create a `.env` file in the root folder (next to this `README.md` file) and add your Gemini API key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. **Launch the Dashboard**:
   ```bash
   python app/main.py
   ```
   *This will launch the local Flask server on `http://127.0.0.1:5000` and automatically open it in your default web browser.*

---

## 🌐 Deployment Guide

### Option 1: Render / Railway (Recommended - 2 Minutes)
Since the project relies on a Python backend to resolve search queries and talk to the Yahoo Finance/Gemini APIs, the simplest way is to deploy it as a single Python Web Service.

#### Render Deployment Steps:
1. Sign in to [Render](https://render.com) and click **New > Web Service**.
2. Connect your GitHub repository.
3. Configure the following service settings:
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -w 4 -b 0.0.0.0:$PORT app.server:app`
4. Under **Advanced**, add the environment variable:
   - `GEMINI_API_KEY` = `(your key)`
5. Click **Deploy Web Service** and your dashboard will be live!

---

### Option 2: Netlify (Frontend) + Render (Backend API)
Netlify is a static asset hosting platform and cannot run the Python Flask server directly. If you want to host the frontend on Netlify, you can split the deployment:

1. **Deploy the Python Backend on Render** (following Option 1 above).
2. **Update the API Endpoint in `app.js`**:
   - Change the fetch requests in `app.js` to point to your live Render backend URL (e.g. `https://your-backend.onrender.com/api/stock`).
3. **Deploy the Static Frontend on Netlify**:
   - Drag and drop the `app/static` directory directly onto Netlify.
   - All static files (`index.html`, `style.css`, `app.js`, `nse_companies.json`) will be served globally!

---

## 📂 Project Structure

```
StockSence_India/
├── app/
│   ├── static/             # Frontend assets
│   │   ├── index.html      # Glassmorphic dashboard template
│   │   ├── style.css       # Responsive styling properties
│   │   ├── app.js          # Autocomplete search & API fetch orchestration
│   │   └── nse_companies.json # Complete dataset of 2,361 equities
│   ├── config.py           # Loads API configurations
│   ├── api_client.py       # Yahoo Finance live quote resolver
│   ├── ai_client.py        # Gemini API & local analysis fallbacks
│   ├── utils.py            # Autocorrect & search string resolvers
│   ├── server.py           # Flask server API endpoints
│   └── main.py             # Server launcher & background threads
├── data/
│   └── api_cache.json      # Offline request cache
├── tests/                  # Pytest verification suites
├── .env.example
├── requirements.txt
└── README.md
```
