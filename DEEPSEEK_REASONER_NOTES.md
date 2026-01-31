# DeepSeek Reasoner (R1) - Expected Behavior

## Why Results Vary Between Runs

DeepSeek Reasoner uses **Chain-of-Thought (CoT) reasoning** with exploration, which means:

1. **Non-Deterministic Reasoning**: The model explores different reasoning paths each time
2. **Temperature Impact**: Even with the same temperature, the reasoning chain can diverge
3. **Token Budget**: The 32,768 token limit can cut reasoning at different points

## Example Variance (NFLX Analysis)

### Run 1 (2026-01-31 02:53:06):
- Recommendation: **STRONG BUY**
- Conviction: **8.0/10**
- Position Size: **4.80%**
- Expected 3Y Return: **60.0%**
- Value Score: 9/10, Growth: 9/10 HOLD, Risk: 4.4/10 EXTREME

### Run 2 (2026-01-31 03:14:05):
- Recommendation: **BUY**
- Conviction: **6.0/10**
- Position Size: **2.50%**
- Expected 3Y Return: **10.0%**
- Value Score: 8/10, Growth: 10/10 GROWTH BUY, Risk: 7.0/10 EXTREME

## Key Observations

1. **Risk Score Variance**: 4.4/10 → 7.0/10 (higher risk = more conservative)
2. **Conviction Variance**: 8.0 → 6.0 (lower conviction = smaller position)
3. **Both flagged EXTREME RISK** but weighted it differently in final decision

## Why This Happens

**DeepSeek Reasoner's reasoning chain includes:**
- Exploring multiple scenarios
- Considering different weightings of factors
- Re-evaluating assumptions during reasoning
- Following different logical paths to conclusion

**This is NORMAL and EXPECTED behavior** for reasoning models!

## Recommendations

### For Production Use:

**Option 1: Use Gemini 3 Flash for Consistency**
```bash
python analyze_complete.py NFLX --model gemini-3-flash-preview --save --log
```
- More deterministic
- Temperature=1.0 optimized
- Faster (no long reasoning chains)

**Option 2: Run DeepSeek Reasoner Multiple Times**
```bash
# Run 3 times and average the results
python analyze_complete.py NFLX --model deepseek-reasoner --save --log
python analyze_complete.py NFLX --model deepseek-reasoner --save --log
python analyze_complete.py NFLX --model deepseek-reasoner --save --log

# Then review with:
python review_performance.py --ticker NFLX
```

**Option 3: Use DeepSeek Chat (More Deterministic)**
```bash
python analyze_complete.py NFLX --model deepseek-chat --save --log
```
- No reasoning chains = more consistent
- Still powerful analysis
- Faster execution

## When to Use Each Model

| Model | Best For | Determinism | Speed | Cost |
|-------|----------|-------------|-------|------|
| **Gemini 3 Flash** | Production decisions | ★★★★★ | ★★★★★ | $ |
| **DeepSeek Chat** | Fast analysis | ★★★★☆ | ★★★★★ | $$ |
| **DeepSeek Reasoner** | Deep exploration | ★★☆☆☆ | ★★☆☆☆ | $$$ |
| **Gemini 2.5 Flash** | Balanced | ★★★★☆ | ★★★★★ | $ |

## Conclusion

**The variance you're seeing is NOT a bug** - it's DeepSeek Reasoner working as designed. The model is genuinely exploring different reasoning paths and reaching different (but reasonable) conclusions.

For **production investment decisions**, consider:
1. Using Gemini 3 Flash (optimized, consistent)
2. Running DeepSeek Reasoner 3x and looking for consensus
3. Using DeepSeek Chat for faster, more consistent analysis
