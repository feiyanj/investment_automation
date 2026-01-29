# Investment Analysis System V3.0

**Professional AI-powered stock analysis using 6 specialized agents**

**Last Updated**: January 29, 2026 | **Version**: 3.0.1

---

## 🎯 Quick Start

```bash
# Basic analysis
python analyze_complete.py AAPL

# Save full report to file
python analyze_complete.py AAPL --save --format txt

# Display full 30-50K word analysis
python analyze_complete.py AAPL --full

# Use different AI model
python analyze_complete.py AAPL --model gemini-3-flash-preview

# Compare multiple stocks
python analyze_complete.py AAPL MSFT GOOGL --compare --save
```

---

## 📊 What You Get

### 5 Specialized AI Agents Analyze:

1. **Business Understanding** - Company model, moat, competitive position
2. **Value Analysis** - Financial quality (8 metrics), intrinsic value, margin of safety
3. **Growth Analysis** - Growth quality, market opportunity, 5-year scenarios
4. **Risk Assessment** - Red flags, business risks, downside scenarios
5. **CIO Synthesis** - Final investment decision with conviction level

### Output Includes:

- ✅ **Recommendation**: STRONG BUY / BUY / HOLD / REDUCE / SELL
- ✅ **Conviction**: 1-10 rating
- ✅ **Position Size**: 0-8% of portfolio
- ✅ **Quality Score**: Financial health (0-10)
- ✅ **Risk Rating**: LOW / MODERATE / HIGH / EXTREME
- ✅ **Intrinsic Value**: Fair value estimate
- ✅ **Expected Returns**: Bull/Base/Bear scenarios
- ✅ **Entry/Stop/Target**: Price levels

---

## 🤖 AI Model Selection

| Model | Speed | Quality | Quota | Best For |
|-------|-------|---------|-------|----------|
| **gemini-2.5-flash** | Fast | High | 250/day | ✅ Default (Recommended) |
| **gemini-2.5-flash-lite** | Fastest | Good | 1500/day | Batch processing |
| **gemini-3-flash-preview** | Fast | Experimental | 1500/day | Testing new features |

```bash
# Default model
python analyze_complete.py AAPL

# High-volume batch processing
python analyze_complete.py AAPL MSFT GOOGL --model gemini-2.5-flash-lite --compare

# Experimental newest model
python analyze_complete.py AAPL --model gemini-3-flash-preview
```

---

## 📖 Usage Examples

### Example 1: Quick Analysis
```bash
python analyze_complete.py AAPL
# Shows: Summary metrics + final recommendation
```

### Example 2: Full Detailed Report
```bash
python analyze_complete.py AAPL --full
# Shows: Complete 30-50K word analysis from all 5 agents
```

### Example 3: Save for Later
```bash
python analyze_complete.py AAPL --save --format txt
# Creates: output/AAPL_20260129_143022.txt
```

### Example 4: Compare Multiple Stocks
```bash
python analyze_complete.py AAPL MSFT GOOGL AMZN --compare --save
# Generates comparison table + individual reports
```

### Example 5: Batch Screen Sector
```bash
python analyze_complete.py AAPL MSFT GOOGL AMZN META NVDA TSLA \
    --compare --model gemini-2.5-flash-lite --save
# Fast screening of 7 stocks with higher quota model
```

---

## 🔧 Installation

### Prerequisites
- Python 3.8+
- Google AI API key (Gemini models)

### Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up API key
export GOOGLE_AI_API_KEY="your-api-key-here"

# 3. Test installation
python analyze_complete.py AAPL
```

### Requirements
```
yfinance>=0.2.28
google-generativeai>=0.3.0
pandas>=2.0.0
python-dotenv>=1.0.0
```

---

## 📁 Project Structure

```
investing_automation/
├── analyze_complete.py      # Main CLI entry point
├── config.py                 # Configuration & model settings
├── requirements.txt          # Python dependencies
├── test_e2e.py              # End-to-end testing
│
├── agents/                   # AI Agent modules
│   ├── business_analyst.py
│   ├── value_hunter.py
│   ├── growth_analyzer.py
│   ├── risk_examiner.py
│   └── cio_synthesizer.py
│
├── data/                     # Data fetching
│   └── fetcher_v3.py
│
├── utils/                    # Utilities
│   ├── display.py           # Terminal formatting
│   └── formatters.py        # Output formatting
│
├── valuation/               # Valuation calculations
│   └── dcf_calculator.py
│
└── output/                  # Saved reports (created automatically)
```

---

## 🎓 How It Works

### Stage 1: Data Collection
- Fetches 5 years of financial statements
- Gets current market data and company info
- Retrieves recent news and events

### Stage 2: Business Understanding
- Analyzes business model and competitive position
- Identifies moat strength and key advantages
- Extracts important catalysts and events

### Stage 3: Value Analysis
- Evaluates financial quality (8 metrics)
- Calculates intrinsic value (DCF + multiples)
- Determines margin of safety

### Stage 4: Growth Analysis
- Assesses historical growth quality
- Analyzes market opportunity (TAM/SAM)
- Models bull/base/bear scenarios

### Stage 5: Risk Assessment
- Identifies red flags (10 checks)
- Evaluates business model risks
- Calculates downside scenarios

### Stage 6: CIO Synthesis
- Integrates all agent perspectives
- Generates final recommendation
- Determines conviction and position size

---

## 📊 Output Formats

### Terminal Display (Default)
```bash
python analyze_complete.py AAPL
```
Shows colored summary with key metrics.

### Full Report Display
```bash
python analyze_complete.py AAPL --full
```
Displays complete 30-50K word analysis in terminal.

### JSON Export
```bash
python analyze_complete.py AAPL --save --format json
```
Creates machine-readable JSON file.

### Text Report
```bash
python analyze_complete.py AAPL --save --format txt
```
Creates human-readable text report with full analysis.

---

## 💡 Pro Tips

### Tip 1: Always Save Important Analyses
```bash
python analyze_complete.py AAPL --save --format txt
```
Saved files always include complete analysis.

### Tip 2: Use Flash Lite for Screening
```bash
# Morning: Screen 20 stocks quickly
python analyze_complete.py AAPL MSFT GOOGL ... \
    --model gemini-2.5-flash-lite --compare --save

# Afternoon: Deep dive on top picks
python analyze_complete.py TOP_PICK --full --save
```

### Tip 3: Pipe to Less for Reading
```bash
python analyze_complete.py AAPL --full | less
```
Scroll through analysis interactively.

### Tip 4: Compare Model Outputs
```bash
python analyze_complete.py AAPL --model gemini-2.5-flash > flash.txt
python analyze_complete.py AAPL --model gemini-3-flash-preview > preview.txt
diff flash.txt preview.txt
```

### Tip 5: Create Watchlist Script
```bash
#!/bin/bash
# watchlist.sh
for ticker in AAPL MSFT GOOGL AMZN META; do
    python analyze_complete.py "$ticker" --save --format txt
    sleep 60  # Avoid rate limits
done
```

---

## ⚙️ Configuration

### Change Default Model
Edit `config.py`:
```python
class Config:
    DEFAULT_MODEL = "gemini-2.5-flash-lite"  # Change here
```

### Add Your Own Model
Edit `config.py`:
```python
AVAILABLE_MODELS = {
    "1": {"name": "gemini-2.5-flash", ...},
    "2": {"name": "gemini-2.5-flash-lite", ...},
    "3": {"name": "gemini-3-flash-preview", ...},
    "4": {"name": "your-model-name", ...}  # Add here
}
```

---

## 🧪 Testing

```bash
# Run end-to-end test
python test_e2e.py

# Expected output:
# ✅ Data fetching works
# ✅ All 5 agents execute successfully
# ✅ Final recommendation generated
# ✅ All extractions successful
```

---

## ⚠️ Rate Limits

### Understanding Quotas

| Model | RPM | RPD | Stocks/Day |
|-------|-----|-----|------------|
| flash | 10 | 250 | ~40 |
| flash-lite | 15 | 1500 | ~250 |
| flash-preview | 15 | 1500 | ~250 |

**Each stock uses ~6 API calls** (one per agent).

### Avoiding Limits

1. **Use Flash Lite for batch**: Higher quota (1500 vs 250)
2. **Space out analyses**: Wait 30-60 seconds between stocks
3. **Spread across day**: Don't analyze 40 stocks at once
4. **Check quota**: Rate limits reset at midnight Pacific

---

## 🆘 Troubleshooting

### "Rate limit exceeded"
**Solution**: Switch to flash-lite or wait for reset
```bash
python analyze_complete.py AAPL --model gemini-2.5-flash-lite
```

### "Model not found"
**Solution**: Check available models in config.py
```bash
grep AVAILABLE_MODELS config.py
```

### "No API key found"
**Solution**: Set environment variable
```bash
export GOOGLE_AI_API_KEY="your-key-here"
```

### "Extraction returned None"
**Solution**: This is now fixed in v3.0.1! All models extract correctly.

### Want to see full reports?
**Solution**: Use `--full` flag or `--save`
```bash
python analyze_complete.py AAPL --full
```

---

## 📚 Command Reference

### Basic Commands
```bash
python analyze_complete.py TICKER              # Basic analysis
python analyze_complete.py TICKER --full       # Show full reports
python analyze_complete.py TICKER --save       # Save to file
python analyze_complete.py T1 T2 --compare     # Compare stocks
```

### Model Selection
```bash
--model gemini-2.5-flash                       # Default (recommended)
--model gemini-2.5-flash-lite                  # Fast, high quota
--model gemini-3-flash-preview                 # Experimental
```

### Output Options
```bash
--format json                                  # JSON output (default)
--format txt                                   # Text report
--full                                         # Display full analysis
--save                                         # Save to file
```

### Examples
```bash
# Most common: Save detailed report
python analyze_complete.py AAPL --save --format txt

# Quick screen many stocks
python analyze_complete.py AAPL MSFT GOOGL --compare --model gemini-2.5-flash-lite

# Deep dive with full display
python analyze_complete.py AAPL --full --save

# Experimental model test
python analyze_complete.py AAPL --model gemini-3-flash-preview --full
```

---

## 🎯 What's New in V3.0.1

### ✅ Multi-Format Extraction (NEW)
All agents now extract correctly from both plain text and markdown table formats.
- Works with all 3 models (flash, flash-lite, flash-preview)
- Backward compatible with existing analyses

### ✅ Full Report Display (NEW)
See complete 30-50K word analysis with `--full` flag.

### ✅ Model Selection (NEW)
Choose AI model via `--model` flag.

### ✅ Enhanced Extraction
- Value Hunter: Extracts quality scores, recommendations, intrinsic values
- Growth Analyzer: Extracts all growth metrics from any format
- Risk Examiner: Extracts all 10 risk metrics reliably
- CIO Synthesizer: Extracts final decisions correctly

---

## 📈 Example Output

```
Investment Analysis: AAPL
Started: 2026-01-29 14:30:22

🤖 Using model: gemini-2.5-flash

Stage 1/6: Data Collection
✅ Data collected: 5 years of financials

Stage 2/6: Business Understanding  
✅ Business analysis: 4523 chars

Stage 3/6: Value Analysis
✅ Value analysis: 12057 chars
Quality Score: 8/10
Moat: Strong
Recommendation: HOLD
Intrinsic Value: $215.30
Current Price: $225.50
Margin of Safety: -4.5%

Stage 4/6: Growth Analysis
✅ Growth analysis: 8234 chars
Growth Quality: 7/10
Expected 5Y Return: 12.5%
Recommendation: GROWTH BUY

Stage 5/6: Risk Analysis
✅ Risk analysis: 7891 chars
Risk Rating: MODERATE RISK
Max Position: 8%
Bear Case: -25.5%

Stage 6/6: CIO Final Decision
✅ CIO synthesis: 5678 chars

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FINAL INVESTMENT DECISION

Recommendation: HOLD
Conviction: 6/10
Position Size: 5-7%

Composite Score: 72/100
CIO Fair Value: $220.00
Upside to Fair Value: 2.3%
Expected 3Y Return: 11.2%

Entry Range: $200-210
Stop Loss: $185
Target Price: $245

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Analysis complete!
```

---

## 📞 Support & Contributing

### Issues?
- Check troubleshooting section above
- Verify API key is set correctly
- Ensure dependencies are installed
- Test with default model first

### Want to Contribute?
- Add new AI models in config.py
- Enhance agent prompts
- Improve extraction patterns
- Add new metrics or calculations

---

## 📄 License

MIT License - Free to use for personal and commercial purposes.

---

## 🙏 Credits

Built with:
- **Google Gemini API** - AI analysis
- **yfinance** - Financial data
- **Python** - Core language

---

**Version**: 3.0.1  
**Last Updated**: January 29, 2026  
**Status**: Production Ready ✅

---

## Quick Reference Card

| I want to... | Command |
|-------------|---------|
| Basic analysis | `python analyze_complete.py AAPL` |
| See full reports | `python analyze_complete.py AAPL --full` |
| Save to file | `python analyze_complete.py AAPL --save --format txt` |
| Compare stocks | `python analyze_complete.py AAPL MSFT --compare` |
| Use fast model | `python analyze_complete.py AAPL --model gemini-2.5-flash-lite` |
| Test preview | `python analyze_complete.py AAPL --model gemini-3-flash-preview` |
| Batch screen | `python analyze_complete.py A B C D --compare --save` |

**Most Common**: `python analyze_complete.py AAPL --save --format txt`

---

**Ready to analyze? Try: `python analyze_complete.py AAPL`** 🚀
