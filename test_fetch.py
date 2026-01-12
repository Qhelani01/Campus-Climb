#!/usr/bin/env python3
"""
Test script to manually fetch opportunities.
This can be run directly without needing admin access in the UI.
"""
import sys
import os

# Change to api directory
os.chdir(os.path.join(os.path.dirname(__file__), 'api'))
sys.path.insert(0, os.path.dirname(__file__))

from index import app, db
from scheduler import fetch_all_opportunities

def test_fetch():
    """Test fetching opportunities"""
    print("=" * 60)
    print("Testing Opportunity Fetch System")
    print("=" * 60)
    
    with app.app_context():
        try:
            # Test database connection
            print("\n1. Testing database connection...")
            db.session.execute(db.text('SELECT 1'))
            print("   ✓ Database connection successful")
            
            # Check if opportunities table exists
            print("\n2. Checking opportunities table...")
            from index import Opportunity
            count = Opportunity.query.count()
            print(f"   ✓ Found {count} existing opportunities in database")
            
            # Test individual fetchers
            print("\n3. Testing individual fetchers...")
            from fetchers.rss_fetcher import GitHubJobsFetcher, StackOverflowJobsFetcher
            from fetchers.api_fetchers import GraphQLJobsFetcher
            
            # Test GitHub Jobs RSS
            print("\n   Testing GitHub Jobs RSS...")
            try:
                github_fetcher = GitHubJobsFetcher()
                github_opps = github_fetcher.fetch()
                print(f"   ✓ GitHub Jobs: Fetched {len(github_opps)} opportunities")
                if github_opps:
                    print(f"      Example: {github_opps[0].get('title', 'N/A')[:50]}...")
            except Exception as e:
                print(f"   ✗ GitHub Jobs failed: {e}")
            
            # Test Stack Overflow Jobs RSS
            print("\n   Testing Stack Overflow Jobs RSS...")
            try:
                so_fetcher = StackOverflowJobsFetcher()
                so_opps = so_fetcher.fetch()
                print(f"   ✓ Stack Overflow: Fetched {len(so_opps)} opportunities")
                if so_opps:
                    print(f"      Example: {so_opps[0].get('title', 'N/A')[:50]}...")
            except Exception as e:
                print(f"   ✗ Stack Overflow failed: {e}")
            
            # Test GraphQL Jobs API
            print("\n   Testing GraphQL Jobs API...")
            try:
                graphql_fetcher = GraphQLJobsFetcher()
                graphql_opps = graphql_fetcher.fetch()
                print(f"   ✓ GraphQL Jobs: Fetched {len(graphql_opps)} opportunities")
                if graphql_opps:
                    print(f"      Example: {graphql_opps[0].get('title', 'N/A')[:50]}...")
            except Exception as e:
                print(f"   ✗ GraphQL Jobs failed: {e}")
            
            # Full fetch test
            print("\n4. Running full fetch (this will save to database)...")
            print("   This may take a minute...")
            results = fetch_all_opportunities()
            
            print("\n   Fetch Results:")
            print(f"   - Total fetched: {results.get('total_fetched', 0)}")
            print(f"   - New opportunities: {results.get('total_new', 0)}")
            print(f"   - Updated opportunities: {results.get('total_updated', 0)}")
            print(f"   - Errors: {results.get('total_errors', 0)}")
            
            if results.get('sources'):
                print("\n   By Source:")
                for source, stats in results['sources'].items():
                    print(f"   - {source}: {stats.get('fetched', 0)} fetched, "
                          f"{stats.get('new', 0)} new, {stats.get('updated', 0)} updated")
            
            # Check final count
            final_count = Opportunity.query.filter(
                (Opportunity.is_deleted == False) | (Opportunity.is_deleted.is_(None))
            ).count()
            print(f"\n   ✓ Total opportunities in database: {final_count}")
            
            print("\n" + "=" * 60)
            print("Test completed successfully!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n✗ Error during test: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == '__main__':
    success = test_fetch()
    sys.exit(0 if success else 1)

