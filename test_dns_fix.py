#!/usr/bin/env python3
"""
Test script to verify DNS fix worked
"""
import socket
import sys
import os

# Add api to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

def test_dns_resolution():
    """Test DNS resolution for common domains"""
    print("=" * 60)
    print("Testing DNS Resolution")
    print("=" * 60)
    
    test_domains = [
        'stackoverflow.com',
        'google.com',
        'github.com',
        'api.graphql.jobs',
    ]
    
    results = {}
    for domain in test_domains:
        try:
            ip = socket.gethostbyname(domain)
            results[domain] = {'status': 'OK', 'ip': ip}
            print(f"✓ {domain}: {ip}")
        except socket.gaierror as e:
            results[domain] = {'status': 'FAILED', 'error': str(e)}
            print(f"✗ {domain}: {e}")
    
    print("\n" + "=" * 60)
    success_count = sum(1 for r in results.values() if r['status'] == 'OK')
    print(f"Results: {success_count}/{len(test_domains)} domains resolved")
    print("=" * 60)
    
    return success_count == len(test_domains)

def test_fetcher():
    """Test a fetcher to see if it can fetch data"""
    print("\n" + "=" * 60)
    print("Testing Stack Overflow Fetcher")
    print("=" * 60)
    
    try:
        from fetchers.rss_fetcher import StackOverflowJobsFetcher
        fetcher = StackOverflowJobsFetcher()
        results = fetcher.fetch()
        
        print(f"Fetched {len(results)} opportunities")
        if results:
            print("\nFirst opportunity:")
            opp = results[0]
            print(f"  Title: {opp.get('title', 'N/A')[:60]}")
            print(f"  Company: {opp.get('company', 'N/A')}")
            print(f"  Source: {opp.get('source', 'N/A')}")
        else:
            print("No opportunities fetched (may be blocked or empty)")
        
        return len(results) > 0
    except Exception as e:
        print(f"Error testing fetcher: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    dns_ok = test_dns_resolution()
    fetcher_ok = test_fetcher()
    
    print("\n" + "=" * 60)
    if dns_ok and fetcher_ok:
        print("✓ All tests passed! DNS is working correctly.")
    elif dns_ok:
        print("⚠ DNS is working, but fetchers are not returning data.")
        print("  This may be due to sites blocking automated requests.")
    else:
        print("✗ DNS resolution is still failing.")
        print("  Please run the DNS fix script: ./fix_dns.sh")
    print("=" * 60)

