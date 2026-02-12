# AI-Based Opportunity Filtering

## Problem
The current keyword-based filtering system incorrectly classifies Reddit posts as opportunities when they contain keywords like "internship" or "workshop", even when they are actually questions, discussions, or requests for help. This results in false positives being displayed in the app, degrading user experience.

**Example of false positive:**
- Post: "How do I find an internship? Looking for advice"
- Current behavior: Classified as opportunity ❌
- Expected behavior: Filtered out (not an opportunity) ✅

## Solution
Replaced keyword-based filtering with AI-powered content classification using the existing Ollama LLM infrastructure. The AI analyzes the full context of each post to distinguish actual opportunities from questions, discussions, and other non-opportunity content.

## Changes

### New Files
- `api/ai_filter.py` - AI classification module with `classify_opportunity()` function
- `test_ai_filter.py` - Comprehensive test suite for AI filter functionality

### Modified Files
- `api/config.py` - Added AI filter configuration options:
  - `AI_FILTER_ENABLED` - Enable/disable AI filtering (default: true)
  - `AI_FILTER_MODEL` - Model selection (defaults to OLLAMA_MODEL)
  - `AI_FILTER_TIMEOUT` - Timeout for filter requests (default: 10 seconds)
  - `AI_FILTER_FALLBACK` - Use keyword filtering as fallback (default: true)

- `api/fetchers/rss_fetcher.py`:
  - Replaced keyword-based filtering in `RedditJobsFetcher` with AI classification
  - Added optional AI filtering to base `RSSFetcher` for all RSS sources
  - Extracted keyword filtering into reusable `keyword_based_filter_fallback()` function
  - Added comprehensive logging for filter decisions

## Features

✅ **Context-Aware Classification**: AI understands context, not just keywords  
✅ **Fallback Mechanism**: Automatically falls back to keyword filtering if AI unavailable  
✅ **Comprehensive Logging**: Tracks all filter decisions with confidence scores  
✅ **Configurable**: Can be enabled/disabled via environment variables  
✅ **Error Resilient**: Handles timeouts, connection errors, and parsing failures gracefully  

## Testing

All tests pass:
- ✅ Imports work correctly
- ✅ Prompt building functions properly
- ✅ Response parsing handles various formats
- ✅ Fallback mechanism works when AI disabled
- ✅ Keyword fallback filtering works correctly
- ✅ AI classification works when Ollama available

Run tests with:
```bash
python3 test_ai_filter.py
```

## Configuration

Add to your `.env` file (optional, defaults shown):
```env
AI_FILTER_ENABLED=true
AI_FILTER_MODEL=llama2  # or leave empty to use OLLAMA_MODEL
AI_FILTER_TIMEOUT=10
AI_FILTER_FALLBACK=true
```

## How It Works

1. **AI Classification**: When a post is fetched, the AI analyzes title + description
2. **Context Understanding**: AI determines if it's an actual opportunity or a question/discussion
3. **Structured Response**: Returns JSON with `is_opportunity`, `confidence`, and `reasoning`
4. **Fallback**: If AI unavailable, automatically uses keyword-based filtering
5. **Logging**: All decisions are logged for monitoring and improvement

## Impact

- **Improved Accuracy**: Reduces false positives by understanding context
- **Better User Experience**: Only actual opportunities are displayed
- **Maintainable**: Prompt-based approach allows easy refinement without code changes
- **Reliable**: Fallback ensures system continues working if AI unavailable

## Related Issues
Fixes the issue where keyword matching incorrectly classified questions and discussions as opportunities.

## Checklist
- [x] Code follows project style guidelines
- [x] Tests added/updated and passing
- [x] Documentation updated (if needed)
- [x] No breaking changes to existing functionality
- [x] Fallback mechanism tested and working
- [x] Logging implemented for monitoring
