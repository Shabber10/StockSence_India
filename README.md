<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=250&section=header&text=StockSense%20India&fontSize=55&animation=fadeIn&fontAlignY=38&desc=Financial%20Analytics%20Dashboard%20%7C%20AI%20Recommendations%20%7C%20Live%20Quotes&descAlignY=56&descAlign=50"/>

  [![Live Demo – Render](https://img.shields.io/badge/Live%20Demo-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://stocksence-india.onrender.com/)
</div>

# 📈 StockSense India

**StockSense India** is a modern, responsive financial web dashboard designed to deliver real-time stock analytics, news headlines, corporate announcements, and AI-powered recommendations (BUY/SELL/HOLD) for all 2,360+ listed companies on the National Stock Exchange (NSE) of India.

The project features a **Python Flask backend** integrated with a keyless **Yahoo Finance resolver** and the **Gemini API** for automated financial analysis, paired with a stunning frontend styled using curated vanilla CSS glassmorphism.

---

## 🌐 Live Demo

| Platform | Link |
|----------|------|
| 🟢 **Render** | [stocksence-india.onrender.com](https://stocksence-india.onrender.com/) |

---

## ✨ Features

- **🔍 Complete Autocomplete Search** — Search all 2,360+ listed companies with auto-correct spelling tolerance (e.g. typing `"relicance"` will match `"Reliance Industries Ltd"`).
- **⚡ Sub-Second Live Market Data** — Fetches live price quotes, percentage updates, and 52-week ranges directly from Yahoo Finance API.
- **🛡️ Resilient Dual-Host Backend** — Dual-host connection retry fallback (`query2` / `query1`) to bypass rate throttles or gateway latencies.
- **🤖 Aligned AI Recommendation Badges** — Displays glassmorphic badges (**🟢 BUY**, **🔴 SELL**, **🟡 HOLD**) aligned strictly with price actions:
  - **SELL**: Daily drop greater than **-1.0%**.
  - **BUY**: Daily gain greater than **+1.0%**.
  - **HOLD**: Flat trading day (between **-1.0%** and **+1.0%**).
- **📰 Integrated Financial News & Events** — Displays recent news headlines and upcoming corporate board meetings for the active stock.
- **🎹 Keyboard Navigation & Accessibility** — Arrow keys to scroll selection list, Enter to search, and Escape to hide the suggestion panel.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, Vanilla JavaScript (ES6+), Custom CSS (Variables, Glassmorphism, Micro-animations) |
| **Icons & Fonts** | Google Fonts – [Outfit](https://fonts.google.com/specimen/Outfit) |
| **Backend** | [Python 3.11+](https://www.python.org/) & [Flask](https://flask.palletsprojects.com/) |
| **APIs** | Yahoo Finance (Market Data), Google Gemini API (Financial Analysis) |

---

## 🚀 Getting Started

### 🛠️ Local Setup
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
   Create a `.env` file in the root folder and add your Gemini API key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. **Launch the Server**:
   ```bash
   python app/main.py
   ```
   *This launches the server on `http://127.0.0.1:5000` and automatically opens it in your default web browser.*

---

## 🌐 Cloud Deployment

### Render Deployment Steps:
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

## 📂 Project Structure

```text
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

---

<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=120&section=footer"/>
</div>

<div align="center">
  Made with 💙 by <strong>Shabber Hussain</strong>
</div>
