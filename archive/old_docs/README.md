# Multi-Agent AI Investment Analysis System

**Version 2.0** - Clean, Modular, Production-Ready

A Python-based system that automates stock research using Google's Gemini API, Yahoo Finance data, live news, and mathematical valuation models (DCF).

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up API Key
Create a `.env` file:
```
GEMINI_API_KEY=your_api_key_here
```
Get free API key: https://makersuite.google.com/app/apikey

### 3. Run Analysis
```bash
python analyze.py
```
Enter a ticker (e.g., `AAPL`, `MSFT`, `NFLX`)

---

## 📁 Project Structure

```
investing_automation/
├── analyze.py              # Main entry point
├── config.py               # Central configuration
│
├── agents/                 # AI agents package
│   ├── base_agent.py       # Core agent class
│   └── prompts.py          # Agent system prompts
│
├── data/                   # Data fetching package
│   ├── fetcher.py          # Main data orchestrator
│   ├── news_fetcher.py     # Live news (DuckDuckGo)
│   └── financial_calculator.py  # Math functions
│
├── valuation/              # Valuation models
│   └── dcf_calculator.py   # 2-Stage DCF model
│
└── utils/                  # Helper functions
    ├── formatters.py       # Number formatting
    └── display.py          # Terminal output
```

---

## 🎯 Features

### 4 Specialized AI Agents
1. **Value Hunter** (Warren Buffett style) - DCF intrinsic value analysis
2. **Growth Visionary** (Cathie Wood style) - Growth catalysts from live news
3. **The Skeptic** (Short-seller style) - Risk analysis and red flags
4. **CIO** (Final decision maker) - Synthesizes all perspectives → BUY/SELL/HOLD

### Data Sources
- **Financial Data**: Yahoo Finance (yfinance)
- **Live News**: DuckDuckGo Search (real-time market news)
- **Valuation**: 2-Stage DCF model with dynamic growth rates

### Key Calculations
- **Free Cash Flow**: Manual calculation for accuracy
- **CAGR**: Handles negative start values properly
- **PEG Ratio**: PE / (Revenue Growth % × 100)
- **DCF Intrinsic Value**: Dynamic growth rate based on revenue

---

## 🔧 Configuration

Edit `config.py` to customize:

```python
class Config:
    # Model Selection
    DEFAULT_MODEL = "gemini-2.5-flash"
    
    # Rate Limiting
    AGENT_DELAY = 15  # Seconds between agents
    
    # DCF Parameters
    DCF_DEFAULTS = {
        'discount_rate': 0.10,        # 10% WACC
        'terminal_growth_rate': 0.03, # 3% perpetual growth
        'growth_rate_cap': 0.15,      # Max 15% growth
        'min_growth_rate': 0.05,      # Min 5% floor
    }
    
    # News Settings
    MAX_NEWS_ARTICLES = 5
```

---

## 📊 How It Works

### Stage 1: Data Collection
Fetches financials from Yahoo Finance, gets live news from DuckDuckGo, calculates FCF, CAGR, PEG ratio

### Stage 2: DCF Valuation
Projects FCF for 5 years, calculates terminal value, uses dynamic growth rate based on revenue YoY, computes margin of safety

### Stage 3: Multi-Agent Analysis
Each agent analyzes from their perspective, 15-second delays between agents, CIO synthesizes all reports → final decision

---

## 💡 Usage Examples

### Basic Analysis
```bash
$ python analyze.py
Enter ticker: AAPL

📊 Fetching data for AAPL...
   📰 Found 5 recent news articles
✅ Data fetched successfully

DCF Intrinsic Value: $185.43
Current Price: $170.50
Margin of Safety: 8.8%
🟡 BUY - Moderate undervaluation
```

### Programmatic Use
```python
from data import DataFetcher
from valuation import ValuationEngine
from agents import BaseAgent, VALUE_HUNTER_PROMPT

# Fetch data
fetcher = DataFetcher("MSFT")
data = fetcher.fetch_all_data()

# Run DCF
engine = ValuationEngine("MSFT")
dcf = engine.calculate_dcf(fcf=data['fcf_current'], growth_rate=0.12)

# Run agent analysis
agent = BaseAgent("Value Hunter", "Analyst", VALUE_HUNTER_PROMPT)
report = agent.analyze(fetcher.format_for_llm())
```

---

## 🧪 Testing

```bash
python test_refactored.py
```

Expected: 4/4 tests passing

---

## 🐛 Recent Bug Fixes (v2.0.1)

1. **CAGR Calculation** - Now handles negative start values (NFLX: 1.6B → 9.4B = +80.4%)
2. **Dynamic DCF Growth** - Uses revenue YoY not static 5% (NFLX: $850 not $36)
3. **PEG Ratio** - Added manual calculation: PE / (Revenue Growth % × 100)

---

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| API Key Error | Create `.env` file with `GEMINI_API_KEY` |
| Rate Limit (429) | Wait 60s or increase `AGENT_DELAY` |
| Module Not Found | Run `pip install -r requirements.txt` |
| No News Found | Normal - continues with available data |

---

## ⚙️ Extending the System

### Add a New Agent
1. Add prompt to `agents/prompts.py`
2. Create agent in `analyze.py`
3. Add to workflow

### Add New Data Source
1. Create `data/new_source.py`
2. Import in `data/__init__.py`
3. Use in `data/fetcher.py`

---

## �� Tech Stack

- Python 3.13+
- google-generativeai (Gemini 2.5 Flash)
- yfinance (Yahoo Finance)
- duckduckgo-search (Live news)
- pandas / numpy

---

## ⚠️ Disclaimer

**Educational purposes only. NOT financial advice.**

AI models can make errors. DCF is sensitive to assumptions. Always do your own research.

---

## 🎉 Summary

Production-ready system with:
✅ Clean modular architecture
✅ Centralized configuration
✅ Live data + DCF valuation
✅ 4 AI agent perspectives
✅ All tests passing

**Start analyzing**: `python analyze.py` 🚀

---

*Built with ❤️ using Google Gemini AI*
