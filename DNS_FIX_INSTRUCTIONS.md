# DNS Fix Instructions

## Quick Fix (Run in Terminal)

I've created a script to fix DNS issues. Run this command in your terminal:

```bash
cd "/Users/qhelanimoyo/Desktop/Projects/Campus Climb"
./fix_dns.sh
```

**Note**: This will ask for your password (sudo access required).

## Manual Fix Steps

If you prefer to fix DNS manually:

### 1. Flush DNS Cache
```bash
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
```

### 2. Set DNS Servers
```bash
# For Wi-Fi
sudo networksetup -setdnsservers Wi-Fi 8.8.8.8 8.8.4.4 1.1.1.1

# For Ethernet (if using)
sudo networksetup -setdnsservers "USB 10/100/1000 LAN" 8.8.8.8 8.8.4.4 1.1.1.1
```

### 3. Verify DNS Settings
```bash
networksetup -getdnsservers Wi-Fi
```

### 4. Test DNS Resolution
```bash
nslookup stackoverflow.com
nslookup api.graphql.jobs
```

## Alternative: Test on Production

If DNS issues persist locally, the fetchers should work fine on Vercel (production) where DNS is properly configured. You can:

1. Deploy to Vercel
2. Test the fetch endpoint there
3. Opportunities will be saved to your production database

## Current Issues

1. **Stack Overflow**: Returns 403 (blocking automated requests) - Updated headers may help
2. **GitHub Jobs**: Shut down in 2021 - Already disabled
3. **GraphQL Jobs**: Domain may not exist - Need to verify correct URL
4. **DNS Resolution**: Inconsistent in Python - Fixed with DNS server change

## After Fixing DNS

1. Restart the Flask server:
   ```bash
   pkill -f "python.*index.py"
   cd api && python3 index.py
   ```

2. Test the fetch:
   ```bash
   curl -X POST http://localhost:8000/api/cron/fetch-opportunities
   ```

3. Check results:
   ```bash
   curl http://localhost:8000/api/opportunities
   ```

