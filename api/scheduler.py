"""
Scheduler and main fetch function for opportunities.
Coordinates all fetchers and saves results to database.
"""
from datetime import datetime
from typing import List, Dict
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.index import db
from api.deduplicator import save_or_update_opportunity
from api.fetcher_config import FetcherConfig
from api.fetchers.rss_fetcher import GitHubJobsFetcher, StackOverflowJobsFetcher, EventbriteFetcher
from api.fetchers.api_fetchers import GraphQLJobsFetcher, JoobleFetcher, AuthenticJobsFetcher, MeetupFetcher

class FetchLogger:
    """Simple logger for fetch operations"""
    
    def __init__(self):
        self.logs = []
    
    def log(self, source: str, fetched: int, new: int, updated: int, errors: int):
        """Log fetch results"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'source': source,
            'fetched': fetched,
            'new': new,
            'updated': updated,
            'errors': errors
        }
        self.logs.append(log_entry)
        print(f"[{log_entry['timestamp']}] {source}: Fetched={fetched}, New={new}, Updated={updated}, Errors={errors}")
    
    def get_logs(self, limit: int = 50) -> List[Dict]:
        """Get recent logs"""
        return self.logs[-limit:] if len(self.logs) > limit else self.logs


# Global logger instance
fetch_logger = FetchLogger()


def fetch_all_opportunities() -> Dict:
    """
    Fetch opportunities from all enabled sources.
    
    Returns:
        Dictionary with fetch results summary
    """
    results = {
        'timestamp': datetime.utcnow().isoformat(),
        'sources': {},
        'total_fetched': 0,
        'total_new': 0,
        'total_updated': 0,
        'total_errors': 0
    }
    
    # Initialize fetchers
    fetchers = []
    
    # RSS Feed Fetchers (always available)
    if FetcherConfig.is_fetcher_enabled('github_jobs_rss'):
        fetchers.append(GitHubJobsFetcher())
    
    if FetcherConfig.is_fetcher_enabled('stackoverflow_jobs_rss'):
        fetchers.append(StackOverflowJobsFetcher())
    
    if FetcherConfig.is_fetcher_enabled('eventbrite_rss'):
        fetchers.append(EventbriteFetcher())
    
    # API Fetchers
    if FetcherConfig.is_fetcher_enabled('graphql_jobs'):
        fetchers.append(GraphQLJobsFetcher())
    
    if FetcherConfig.is_fetcher_enabled('jooble') and FetcherConfig.JOOBLE_API_KEY:
        fetchers.append(JoobleFetcher())
    
    if FetcherConfig.is_fetcher_enabled('authentic_jobs') and FetcherConfig.AUTHENTIC_JOBS_API_KEY:
        fetchers.append(AuthenticJobsFetcher())
    
    if FetcherConfig.is_fetcher_enabled('meetup') and FetcherConfig.MEETUP_API_KEY:
        fetchers.append(MeetupFetcher())
    
    # Custom RSS feeds
    for feed_url in FetcherConfig.get_rss_feeds():
        if feed_url and feed_url not in FetcherConfig.DEFAULT_RSS_FEEDS:
            fetchers.append(EventbriteFetcher(feed_url=feed_url))
    
    # Fetch from each source
    for fetcher in fetchers:
        source_name = fetcher.source_name
        try:
            print(f"Fetching from {source_name}...")
            
            # Fetch opportunities
            opportunities = fetcher.fetch()
            
            # Save to database
            new_count = 0
            updated_count = 0
            error_count = fetcher.error_count
            
            for opp_dict in opportunities:
                try:
                    opportunity, is_new = save_or_update_opportunity(opp_dict)
                    if is_new:
                        new_count += 1
                    else:
                        updated_count += 1
                except Exception as e:
                    print(f"Error saving opportunity from {source_name}: {e}")
                    error_count += 1
                    continue
            
            # Log results
            fetched_count = len(opportunities)
            fetch_logger.log(
                source=source_name,
                fetched=fetched_count,
                new=new_count,
                updated=updated_count,
                errors=error_count
            )
            
            # Update summary
            results['sources'][source_name] = {
                'fetched': fetched_count,
                'new': new_count,
                'updated': updated_count,
                'errors': error_count
            }
            results['total_fetched'] += fetched_count
            results['total_new'] += new_count
            results['total_updated'] += updated_count
            results['total_errors'] += error_count
            
        except Exception as e:
            print(f"Error fetching from {source_name}: {e}")
            import traceback
            traceback.print_exc()
            results['sources'][source_name] = {
                'fetched': 0,
                'new': 0,
                'updated': 0,
                'errors': 1,
                'error_message': str(e)
            }
            results['total_errors'] += 1
    
    return results


def get_fetch_logs(limit: int = 50) -> List[Dict]:
    """Get recent fetch logs"""
    return fetch_logger.get_logs(limit)

