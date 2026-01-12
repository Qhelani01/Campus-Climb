# Fix DNS - Step by Step Instructions

## Quick Fix (Copy and paste these commands in your Terminal)

Open Terminal and run these commands one by one:

### Step 1: Flush DNS Cache
```bash
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
```
*(Enter your password when prompted)*

### Step 2: Set DNS Servers
```bash
sudo networksetup -setdnsservers Wi-Fi 8.8.8.8 8.8.4.4 1.1.1.1
```
*(Enter your password when prompted)*

### Step 3: Verify DNS Settings
```bash
networksetup -getdnsservers Wi-Fi
```
You should see: `8.8.8.8`, `8.8.4.4`, `1.1.1.1`

### Step 4: Test DNS Resolution
```bash
python3 -c "import socket; print('stackoverflow.com:', socket.gethostbyname('stackoverflow.com'))"
```

### Step 5: Restart Flask Server
```bash
cd "/Users/qhelanimoyo/Desktop/Projects/Campus Climb"
pkill -f "python.*index.py"
cd api && python3 index.py &
```

### Step 6: Test Fetch
```bash
sleep 3
curl -X POST http://localhost:8000/api/cron/fetch-opportunities
```

---

## OR: Use the Automated Script

Simply run:
```bash
cd "/Users/qhelanimoyo/Desktop/Projects/Campus Climb"
./fix_dns.sh
```

Then restart your Flask server and test again.

