# Quick DNS Fix - Copy & Paste These Commands

## Step 1: Open Terminal
Open Terminal on your Mac.

## Step 2: Run These Commands (One at a Time)

Copy and paste each command, then press Enter. Enter your password when prompted.

```bash
# Flush DNS cache
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
```

```bash
# Set Google DNS servers
sudo networksetup -setdnsservers Wi-Fi 8.8.8.8 8.8.4.4 1.1.1.1
```

```bash
# Verify it worked
networksetup -getdnsservers Wi-Fi
```

You should see: `8.8.8.8`, `8.8.4.4`, `1.1.1.1`

## Step 3: Test DNS

```bash
python3 -c "import socket; print('stackoverflow.com:', socket.gethostbyname('stackoverflow.com'))"
```

Should print: `stackoverflow.com: 198.252.206.1` (or similar IP)

## Step 4: Restart Flask Server

```bash
cd "/Users/qhelanimoyo/Desktop/Projects/Campus Climb"
pkill -f "python.*index.py"
cd api && python3 index.py &
```

## Step 5: Test Fetch

```bash
sleep 3
curl -X POST http://localhost:8000/api/cron/fetch-opportunities
```

## What to Expect

- **DNS Fix**: Should resolve most domains correctly
- **Stack Overflow**: May still return 403 (they block bots)
- **Reddit Feeds**: Should work better (less blocking)
- **Other Sources**: Will work once DNS is properly configured

## Alternative: Test on Production

If local DNS issues persist, deploy to Vercel where DNS is properly configured and test there.

