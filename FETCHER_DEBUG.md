# Fetcher Debugging Guide

## Issues Found

### 1. DNS Resolution Failures
**Error**: `nodename nor servname provided, or not known`

**Cause**: DNS resolution is failing for external domains. This is a local network/DNS configuration issue.

**Solutions**:
- Check your DNS settings: `scutil --dns`
- Try using different DNS servers (8.8.8.8, 1.1.1.1)
- Check if you're behind a VPN or proxy
- Verify internet connectivity: `ping 8.8.8.8`

### 2. GitHub Jobs Shut Down
**Status**: GitHub Jobs API was shut down in May 2021

**Solution**: The GitHub Jobs fetcher has been disabled. Use alternative sources.

### 3. SSL Certificate Issues
**Error**: `SSL: CERTIFICATE_VERIFY_FAILED`

**Cause**: SSL certificate verification failing (may be due to network/proxy)

**Solution**: Fetchers now use `requests` library with proper SSL handling. If issues persist, check your network configuration.

## Working Fetchers

### Currently Enabled (Default)
- `stackoverflow_jobs_rss` - Stack Overflow Jobs RSS feed

### Available but Disabled (Due to DNS Issues)
- `graphql_jobs` - GraphQL Jobs API (requires DNS resolution)
- `github_jobs_rss` - GitHub Jobs (shut down)

### Available with API Keys (Free Registration)
- `jooble` - Requires JOOBLE_API_KEY
- `authentic_jobs` - Requires AUTHENTIC_JOBS_API_KEY  
- `meetup` - Requires MEETUP_API_KEY

## Testing Fetchers

### Test Individual Fetcher
```python
from api.fetchers.rss_fetcher import StackOverflowJobsFetcher
fetcher = StackOverflowJobsFetcher()
results = fetcher.fetch()
print(f"Fetched {len(results)} opportunities")
```

### Test Network Connectivity
```bash
# Test DNS resolution
nslookup jobs.github.com
nslookup stackoverflow.com
nslookup api.graphql.jobs

# Test HTTP connectivity
curl -I https://stackoverflow.com/jobs/feed
```

## Next Steps

1. **Fix DNS Issues**: Configure proper DNS servers or check network settings
2. **Test on Production**: Deploy to Vercel where DNS should work properly
3. **Add Alternative Sources**: Consider adding more RSS feeds or APIs
4. **Monitor Logs**: Check `/tmp/flask_server.log` for detailed error messages

## Alternative Data Sources

If DNS issues persist, consider:
- Using a proxy/VPN
- Testing on a different network
- Deploying to Vercel (production environment)
- Adding manual opportunity entry as fallback

