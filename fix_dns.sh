#!/bin/bash
# DNS Fix Script for macOS
# Run this script to fix DNS resolution issues

echo "=== DNS Fix Script ==="
echo ""
echo "This script will:"
echo "1. Flush DNS cache"
echo "2. Set Google DNS servers (8.8.8.8, 8.8.4.4)"
echo "3. Restart network services"
echo ""
read -p "Press Enter to continue (or Ctrl+C to cancel)..."
echo ""

# Flush DNS cache
echo "Flushing DNS cache..."
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
echo "✓ DNS cache flushed"
echo ""

# Set DNS servers for Wi-Fi
echo "Setting DNS servers for Wi-Fi..."
sudo networksetup -setdnsservers Wi-Fi 8.8.8.8 8.8.4.4 1.1.1.1
echo "✓ DNS servers set to Google DNS (8.8.8.8, 8.8.4.4) and Cloudflare (1.1.1.1)"
echo ""

# Verify DNS settings
echo "Current DNS settings:"
networksetup -getdnsservers Wi-Fi
echo ""

# Test DNS resolution
echo "Testing DNS resolution..."
echo "Testing stackoverflow.com..."
nslookup stackoverflow.com 8.8.8.8 | head -3
echo ""

echo "=== DNS Fix Complete ==="
echo "Please restart your terminal or run:"
echo "  export DNS_SERVERS=8.8.8.8,8.8.4.4"
echo ""
echo "Then test the fetchers again."

