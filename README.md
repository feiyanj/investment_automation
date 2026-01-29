# Investment Analysis System V3.0

**Professional AI-powered stock analysis using 6 specialized agents**

Version 3.0.1 | Last Updated: January 29, 2026 | Status: Production Ready ✅

---

## 🚀 Quick Start

```bash
# Basic analysis
python analyze_complete.py AAPL

# Full detailed report (30-50K words)
python analyze_complete.py AAPL --full

# Save to file
python analyze_complete.py AAPL --save --format txt

# Compare multiple stocks
python analyze_complete.py AAPL MSFT GOOGL --compare
```

---

## 📊 What It Does

### 5 AI Agents Analyze Every Stock:

1. **Business Analyst** - Business model, moat, competitive position
2. **Value Hunter** - Financial quality (8 metrics), intrinsic value
3. **Growth Analyzer** - Growth quality, market opportunity, scenarios
4. **Risk Examiner** - Red flags, risks, downside analysis
5. **CIO Synthesizer** - Final investment decision & conviction

### Key Outputs:

- **Recommendation**: STRONG BUY / BUY / HOLD / REDUCE / SELL
- **Conviction**: 1-10 rating
- **Position Size**: 0-8% of portfolio
- **Quality Score**: 0-10 financial health rating
- **Risk Rating**: LOW / MODERATE / HIGH / EXTREME
- **Intrinsic Value**: Fair value estimate
- **Expected Returns**: Bull/Base/Bear scenarios (1Y/3Y/5Y)
- **Price Targets**: Entry/Stop/Target levels

---

## 🔧 Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set API key
export GOOGLE_AI_API_KEY="your-api-key-here"

# 3. Run
python analyze_complete.py AAPL
```

**Requirements**: Python 3.8+, Google AI API key ([Get one here](https://makersuite.google.com/app/apikey))

---

## 🤖 AI Models

| Model | Speed | Quality | Quota/Day | Best For |
|-------|-------|---------|-----------|----------|
| **gemini-2.5-flash** | Fast | High | 250 | ✅ Default - Most analyses |
| **gemini-2.5-flash-lite** | Fastest | Good | 1500 | Batch processing (10+ stocks) |
| **gemini-3-flash-preview** | Fast | Experimental | 1500 | Testing new features |

```bash
# Use specific model
python analyze_complete.py AAPL --model gemini-2.5-flash-lite

# Batch screen with high-quota model
python analyze_complete.py AAPL MSFT GOOGL AMZN \
    --compare --model gemini-2.5-flash-lite
```

**Note**: Each stock uses ~6 API calls (one per agent).

---

## 📖 Usage Examples

### 1. Quick Analysis
```bash
python analyze_complete.py AAPL
# → Terminal summary with key metrics
```

### 2. Full Report (30-50K words)
```bash
python analyze_complete.py AAPL --full
# → Complete analysis from all 5 agents
```

### 3. Save Report
```bash
python analyze_complete.py AAPL --save --format txt
# → Creates: output/AAPL_20260129_143022.txt
```

### 4. Compare Stocks
```bash
python analyze_complete.py AAPL MSFT GOOGL AMZN --compare --save
# → Comparison table + individual reports
```

### 5. Batch Screen
```bash
# Screen sector with fast model
python analyze_complete.py AAPL MSFT GOOGL AMZN META NVDA TSLA \
    --compare --model gemini-2.5-flash-lite --save
```

### 6. Different Formats
```bash
# JSON (for programmatic use)
python analyze_complete.py AAPL --save --format json

# Text (for reading)
python analyze_complete.py AAPL --save --format txt
```

---

## 📁 Project Structure

```
investment_analysis/
├── analyze_complete.py      # Main CLI
├── config.py                 # Settings & models
├── test_e2e.py              # Testing suite
├── requirements.txt          # Dependencies
│
├── agents/                   # 5 AI agents
│   ├── business_analyst.py
│   ├── value_hunter.py
│   ├── growth_analyzer.py
│   ├── risk_examiner.py
│   └── cio_synthesizer.py
│
├── data/                     # Data fetching
├── utils/                    # Utilities
├── valuation/                # DCF calculations
└── output/                   # Saved reports
```

---

## 💡 Pro Tips

**1. Always save important analyses**
```bash
python analyze_complete.py AAPL --save --format txt
```

**2. Screen first, then deep dive**
```bash
# Morning: Screen 10 stocks with fast model
python analyze_complete.py A B C D E F G H I J \
    --compare --model gemini-2.5-flash-lite

# Afternoon: Deep dive top 3 with default model
python analyze_complete.py TOP_PICK --full --save
```

**3. Read long reports interactively**
```bash
python analyze_complete.py AAPL --full | less
```

**4. Create watchlist automation**
```bash
#!/bin/bash
for ticker in AAPL MSFT GOOGL AMZN META; do
    python analyze_complete.py "$ticker" --save --format txt
    sleep 60  # Avoid rate limits
done
```

---

## ⚠️ Rate Limits

| Model | Requests/Min | Requests/Day | Stocks/Day |
|-------|--------------|--------------|------------|
| flash | 10 | 250 | ~40 |
| flash-lite | 15 | 1500 | ~250 |
| flash-preview | 15 | 1500 | ~250 |

**Tips to avoid limits:**
- Use `gemini-2.5-flash-lite` for batch processing
- Wait 30-60 seconds between analyses
- Spread analyses across the day
- Limits reset at midnight Pacific time

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Rate limit exceeded | Use `--model gemini-2.5-flash-lite` or wait for reset |
| No API key found | `export GOOGLE_AI_API_KEY="your-key"` |
| Model not found | Check available models in `config.py` |
| Want full reports? | Use `--full` flag or `--save --format txt` |

---

## 📚 Command Reference

### Basic Commands
```bash
python analyze_complete.py TICKER              # Basic analysis
python analyze_complete.py TICKER --full       # Full 30-50K word report
python analyze_complete.py TICKER --save       # Save to file
python analyze_complete.py T1 T2 --compare     # Compare stocks
```

### Flags
```bash
--model MODEL         # gemini-2.5-flash (default) | flash-lite | 3-flash-preview
--format FORMAT       # json (default) | txt
--full                # Display complete analysis
--save                # Save to output/ directory
--compare             # Show comparison table (multi-stock)
```

### Most Common Commands
```bash
# Standard analysis with save
python analyze_complete.py AAPL --save --format txt

# Quick screen
python analyze_complete.py AAPL MSFT GOOGL --compare --model gemini-2.5-flash-lite

# Deep dive
python analyze_complete.py AAPL --full --save
```

---

## 🎯 What's New in V3.0.1

✅ **Multi-format extraction** - Works with all 3 models (plain text + markdown tables)  
✅ **Full report display** - `--full` flag shows complete 30-50K word analysis  
✅ **Model selection** - Choose any model via `--model` flag  
✅ **Enhanced reliability** - All agents extract correctly from any output format

---

## 🧪 Testing

```bash
# Quick test (1 stock)
python test_e2e.py --quick

# Full test suite (30-40 min, uses API quota)
python test_e2e.py
```

---

## ⚙️ Configuration

### Change Default Model
Edit `config.py`:
```python
class Config:
    DEFAULT_MODEL = "gemini-2.5-flash-lite"  # Change here
```

### Add Custom Model
Edit `config.py`:
```python
AVAILABLE_MODELS = {
    "4": {"name": "your-model", "rpm": 10, "rpd": 250}
}
```

---

## 📈 Example Output

```
Investment Analysis: AAPL
🤖 Using model: gemini-2.5-flash

Stage 1/6: Data Collection ✅
Stage 2/6: Business Understanding ✅
Stage 3/6: Value Analysis ✅
  Quality Score: 8/10
  Intrinsic Value: $215.30
  Current Price: $225.50
  Margin of Safety: -4.5%

Stage 4/6: Growth Analysis ✅
  Growth Quality: 7/10
  Expected 5Y Return: 12.5%

Stage 5/6: Risk Analysis ✅
  Risk Rating: MODERATE
  Max Position: 8%
  Bear Case: -25.5%

Stage 6/6: CIO Final Decision ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FINAL INVESTMENT DECISION

Recommendation: HOLD
Conviction: 6/10
Position Size: 5-7%

CIO Fair Value: $220.00
Expected 3Y Return: 11.2%

Entry Range: $200-210
Target Price: $245
Stop Loss: $185
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 📄 License

MIT License - Free for personal and commercial use.

---

## 🙏 Built With

- **Google Gemini API** - AI analysis
- **yfinance** - Financial data  
- **Python 3.8+** - Core language

---

## 🎯 Quick Reference

| I Want To... | Command |
|--------------|---------|
| Basic analysis | `python analyze_complete.py AAPL` |
| Full report | `python analyze_complete.py AAPL --full` |
| Save analysis | `python analyze_complete.py AAPL --save --format txt` |
| Compare stocks | `python analyze_complete.py AAPL MSFT --compare` |
| Fast model | `python analyze_complete.py AAPL --model gemini-2.5-flash-lite` |
| Batch screen | `python analyze_complete.py A B C D --compare --save` |

**Most Common**: `python analyze_complete.py AAPL --save --format txt`

---

**Ready? Try:** `python analyze_complete.py AAPL` 🚀
