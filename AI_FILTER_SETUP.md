# AI Filter Setup Guide

## Current Status

The AI-based opportunity filtering has been implemented, but **Ollama is not currently running**. This means the system is falling back to improved keyword-based filtering.

## Two Options to Fix the Filtering Issue

### Option 1: Use AI Filtering (Recommended - Best Accuracy)

The AI filter provides much better accuracy than keyword matching. To enable it:

1. **Install Ollama** (if not already installed):
   ```bash
   # macOS
   brew install ollama
   
   # Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Windows: Download from https://ollama.ai
   ```

2. **Start Ollama Server**:
   ```bash
   ollama serve
   ```

3. **Download a Model** (if not already downloaded):
   ```bash
   ollama pull llama2
   # or
   ollama pull mistral  # Faster alternative
   ```

4. **Verify Ollama is Running**:
   ```bash
   curl http://localhost:11434/api/tags
   ```

5. **Refresh Opportunities**: The AI filter will automatically be used on the next fetch.

### Option 2: Use Improved Keyword Filter (Current - Better than Before)

The keyword fallback has been significantly improved to:
- ✅ Filter out questions (how, what, where, when, why)
- ✅ Require strong hiring indicators
- ✅ Filter out requests for help/advice
- ✅ Be much stricter overall

**However**, it's still not as accurate as AI filtering.

## Why You're Still Seeing False Positives

If you're still seeing questions as opportunities, it's likely because:

1. **Old opportunities in database**: Opportunities fetched before the filter was improved are still in the database
2. **Need to re-fetch**: You need to run a fresh fetch to apply the new filtering

## How to Re-fetch Opportunities

### Option A: Through the Admin UI
1. Log in as admin
2. Go to Admin Dashboard
3. Click "Fetch Opportunities" or similar button

### Option B: Through Terminal
```bash
cd "/Users/qhelanimoyo/Desktop/Projects/Campus Climb"
python3 test_fetch.py
```

### Option C: Through API
```bash
curl -X POST http://localhost:8000/api/admin/fetch-opportunities \
  -H "Cookie: session=your-session-cookie"
```

## Testing the Filter

Run the test suite to verify filtering:
```bash
python3 test_ai_filter.py
```

Test specific examples:
```bash
python3 -c "
from api.fetchers.rss_fetcher import keyword_based_filter_fallback

# Test a question (should be False)
result = keyword_based_filter_fallback(
    'How do I find an internship?',
    'Looking for advice',
    'reddit_internships'
)
print(f'Question filtered: {result}')  # Should be False

# Test actual opportunity (should be True)
result = keyword_based_filter_fallback(
    '[Hiring] Software Engineer',
    'We are hiring. Apply now!',
    'reddit_jobs'
)
print(f'Opportunity detected: {result}')  # Should be True
"
```

## Configuration

The AI filter can be configured via environment variables:

```env
# Enable/disable AI filtering (default: true)
AI_FILTER_ENABLED=true

# Model to use (defaults to OLLAMA_MODEL)
AI_FILTER_MODEL=llama2

# Timeout in seconds (default: 10)
AI_FILTER_TIMEOUT=10

# Use keyword fallback if AI unavailable (default: true)
AI_FILTER_FALLBACK=true
```

## Monitoring

Check the logs to see which filter is being used:
- Look for "AI FILTER:" messages in console output
- "method=ai" means AI filtering was used
- "method=fallback" or "method=keyword" means keyword filtering was used

## Next Steps

1. **Immediate**: Re-fetch opportunities to apply the improved keyword filter
2. **Best Solution**: Set up Ollama for AI filtering (much better accuracy)
3. **Monitor**: Check logs to see filtering decisions and adjust if needed
