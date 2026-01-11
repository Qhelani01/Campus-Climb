"""
Scheduler and main fetch function for opportunities.
Coordinates all fetchers and saves results to database.
"""
from datetime import datetime
from typing import List, Dict
import json
import os

# Lazy imports to avoid circular dependencies
def get_deduplicator():
    import deduplicator
    return deduplicator.save_or_update_opportunity

def get_fetcher_config():
    import fetcher_config
    return fetcher_config.FetcherConfig

def get_fetchers():
    from fetchers.rss_fetcher import GitHubJobsFetcher, StackOverflowJobsFetcher, EventbriteFetcher
    from fetchers.api_fetchers import GraphQLJobsFetcher, JoobleFetcher, AuthenticJobsFetcher, MeetupFetcher
    return {
        'GitHubJobsFetcher': GitHubJobsFetcher,
        'StackOverflowJobsFetcher': StackOverflowJobsFetcher,
        'EventbriteFetcher': EventbriteFetcher,
        'GraphQLJobsFetcher': GraphQLJobsFetcher,
        'JoobleFetcher': JoobleFetcher,
        'AuthenticJobsFetcher': AuthenticJobsFetcher,
        'MeetupFetcher': MeetupFetcher
    }

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
    # #region agent log
    log_path = '/Users/qhelanimoyo/Desktop/Projects/Campus Climb/.cursor/debug.log'
    try:
        with open(log_path, 'a') as f:
            f.write(json.dumps({
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'A',
                'location': 'scheduler.py:58',
                'message': 'fetch_all_opportunities entry',
                'data': {},
                'timestamp': int(datetime.utcnow().timestamp() * 1000)
            }) + '\n')
    except Exception as log_err:
        print(f"DEBUG: Failed to write log entry: {log_err}")
        import traceback
        traceback.print_exc()
    # #endregion
    
    # Import here to avoid circular dependency
    FetcherConfig = get_fetcher_config()
    fetcher_classes = get_fetchers()
    
    # Import db and Opportunity from index to ensure we use the same instances
    # Since scheduler.py is in the api directory, we can import directly
    from index import db, Opportunity
    
    # Get the deduplicator function and wrap it to pass db and Opportunity
    from deduplicator import save_or_update_opportunity as _save_or_update_opportunity
    def save_or_update_opportunity(opp_dict):
        return _save_or_update_opportunity(opp_dict, db=db, Opportunity=Opportunity)
    
    # #region agent log
    try:
        enabled = FetcherConfig.get_enabled_fetchers()
        rss_feeds = FetcherConfig.get_rss_feeds()
        with open(log_path, 'a') as f:
            f.write(json.dumps({
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'A',
                'location': 'scheduler.py:70',
                'message': 'FetcherConfig loaded',
                'data': {'enabled_fetchers': enabled, 'rss_feeds_count': len(rss_feeds), 'rss_feeds': rss_feeds[:3]},
                'timestamp': int(datetime.utcnow().timestamp() * 1000)
            }) + '\n')
    except Exception as e:
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'A',
                    'location': 'scheduler.py:70',
                    'message': 'FetcherConfig load error',
                    'data': {'error': str(e)},
                    'timestamp': int(datetime.utcnow().timestamp() * 1000)
                }) + '\n')
        except: pass
    # #endregion
    
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
    # #region agent log
    try:
        gh_enabled = FetcherConfig.is_fetcher_enabled('github_jobs_rss')
        with open(log_path, 'a') as f:
            f.write(json.dumps({
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'A',
                'location': 'scheduler.py:83',
                'message': 'github_jobs_rss check',
                'data': {'enabled': gh_enabled},
                'timestamp': int(datetime.utcnow().timestamp() * 1000)
            }) + '\n')
    except: pass
    # #endregion
    if FetcherConfig.is_fetcher_enabled('github_jobs_rss'):
        fetchers.append(fetcher_classes['GitHubJobsFetcher']())
    
    # #region agent log
    try:
        so_enabled = FetcherConfig.is_fetcher_enabled('stackoverflow_jobs_rss')
        with open(log_path, 'a') as f:
            f.write(json.dumps({
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'A',
                'location': 'scheduler.py:86',
                'message': 'stackoverflow_jobs_rss check',
                'data': {'enabled': so_enabled},
                'timestamp': int(datetime.utcnow().timestamp() * 1000)
            }) + '\n')
    except: pass
    # #endregion
    if FetcherConfig.is_fetcher_enabled('stackoverflow_jobs_rss'):
        fetchers.append(fetcher_classes['StackOverflowJobsFetcher']())
    
    if FetcherConfig.is_fetcher_enabled('eventbrite_rss'):
        fetchers.append(fetcher_classes['EventbriteFetcher']())
    
    # API Fetchers
    # #region agent log
    try:
        gql_enabled = FetcherConfig.is_fetcher_enabled('graphql_jobs')
        with open(log_path, 'a') as f:
            f.write(json.dumps({
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'A',
                'location': 'scheduler.py:93',
                'message': 'graphql_jobs check',
                'data': {'enabled': gql_enabled},
                'timestamp': int(datetime.utcnow().timestamp() * 1000)
            }) + '\n')
    except: pass
    # #endregion
    if FetcherConfig.is_fetcher_enabled('graphql_jobs'):
        fetchers.append(fetcher_classes['GraphQLJobsFetcher']())
    
    if FetcherConfig.is_fetcher_enabled('jooble') and FetcherConfig.JOOBLE_API_KEY:
        fetchers.append(fetcher_classes['JoobleFetcher']())
    
    if FetcherConfig.is_fetcher_enabled('authentic_jobs') and FetcherConfig.AUTHENTIC_JOBS_API_KEY:
        fetchers.append(fetcher_classes['AuthenticJobsFetcher']())
    
    if FetcherConfig.is_fetcher_enabled('meetup') and FetcherConfig.MEETUP_API_KEY:
        fetchers.append(fetcher_classes['MeetupFetcher']())
    
    # Custom RSS feeds and Reddit feeds
    from fetchers.rss_fetcher import RedditJobsFetcher
    for feed_url in FetcherConfig.get_rss_feeds():
        if feed_url and feed_url not in FetcherConfig.DEFAULT_RSS_FEEDS:
            # Check if it's a Reddit feed
            if 'reddit.com' in feed_url:
                # Extract subreddit name from URL
                subreddit = feed_url.split('/r/')[1].split('/')[0] if '/r/' in feed_url else 'unknown'
                fetchers.append(RedditJobsFetcher(feed_url=feed_url, subreddit=subreddit))
            else:
                fetchers.append(fetcher_classes['EventbriteFetcher'](feed_url=feed_url))
    
    # Add Reddit feeds from default list
    for feed_url in FetcherConfig.get_rss_feeds():
        if 'reddit.com' in feed_url and '/r/' in feed_url:
            subreddit = feed_url.split('/r/')[1].split('/')[0]
            if not any(f.source_name == f'reddit_{subreddit}' for f in fetchers):
                fetchers.append(RedditJobsFetcher(feed_url=feed_url, subreddit=subreddit))
    
    # #region agent log
    try:
        with open(log_path, 'a') as f:
            f.write(json.dumps({
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'A',
                'location': 'scheduler.py:123',
                'message': 'Fetchers initialized',
                'data': {'fetcher_count': len(fetchers), 'fetcher_names': [f.source_name for f in fetchers]},
                'timestamp': int(datetime.utcnow().timestamp() * 1000)
            }) + '\n')
    except: pass
    # #endregion
    
    # Fetch from each source
    for fetcher in fetchers:
        source_name = fetcher.source_name
        try:
            print(f"Fetching from {source_name}...")
            
            # #region agent log
            try:
                with open(log_path, 'a') as f:
                    f.write(json.dumps({
                        'sessionId': 'debug-session',
                        'runId': 'run1',
                        'hypothesisId': 'B',
                        'location': 'scheduler.py:131',
                        'message': 'Before fetcher.fetch()',
                        'data': {'source_name': source_name, 'fetcher_type': type(fetcher).__name__},
                        'timestamp': int(datetime.utcnow().timestamp() * 1000)
                    }) + '\n')
            except: pass
            # #endregion
            
            # Fetch opportunities
            opportunities = fetcher.fetch()
            
            # #region agent log
            try:
                with open(log_path, 'a') as f:
                    f.write(json.dumps({
                        'sessionId': 'debug-session',
                        'runId': 'run1',
                        'hypothesisId': 'B',
                        'location': 'scheduler.py:137',
                        'message': 'After fetcher.fetch()',
                        'data': {'source_name': source_name, 'opportunities_count': len(opportunities), 'error_count': fetcher.error_count},
                        'timestamp': int(datetime.utcnow().timestamp() * 1000)
                    }) + '\n')
            except: pass
            # #endregion
            
            # Save to database
            new_count = 0
            updated_count = 0
            error_count = fetcher.error_count
            
            for idx, opp_dict in enumerate(opportunities):
                try:
                    # #region agent log
                    try:
                        with open(log_path, 'a') as f:
                            f.write(json.dumps({
                                'sessionId': 'debug-session',
                                'runId': 'run1',
                                'hypothesisId': 'C',
                                'location': 'scheduler.py:140',
                                'message': 'Before save_or_update_opportunity',
                                'data': {'source_name': source_name, 'opp_idx': idx, 'opp_title': opp_dict.get('title', '')[:50], 'has_source': bool(opp_dict.get('source')), 'has_source_id': bool(opp_dict.get('source_id'))},
                                'timestamp': int(datetime.utcnow().timestamp() * 1000)
                            }) + '\n')
                    except: pass
                    # #endregion
                    
                    opportunity, is_new = save_or_update_opportunity(opp_dict)
                    
                    # #region agent log
                    try:
                        with open(log_path, 'a') as f:
                            f.write(json.dumps({
                                'sessionId': 'debug-session',
                                'runId': 'run1',
                                'hypothesisId': 'C',
                                'location': 'scheduler.py:150',
                                'message': 'After save_or_update_opportunity',
                                'data': {'source_name': source_name, 'opp_idx': idx, 'is_new': is_new, 'opp_id': opportunity.id if opportunity else None},
                                'timestamp': int(datetime.utcnow().timestamp() * 1000)
                            }) + '\n')
                    except: pass
                    # #endregion
                    
                    if is_new:
                        new_count += 1
                    else:
                        updated_count += 1
                except Exception as e:
                    # #region agent log
                    try:
                        with open(log_path, 'a') as f:
                            f.write(json.dumps({
                                'sessionId': 'debug-session',
                                'runId': 'run1',
                                'hypothesisId': 'C',
                                'location': 'scheduler.py:165',
                                'message': 'Error saving opportunity',
                                'data': {'source_name': source_name, 'opp_idx': idx, 'error': str(e), 'error_type': type(e).__name__},
                                'timestamp': int(datetime.utcnow().timestamp() * 1000)
                            }) + '\n')
                    except: pass
                    # #endregion
                    print(f"Error saving opportunity from {source_name}: {e}")
                    import traceback
                    traceback.print_exc()
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
            # #region agent log
            try:
                with open(log_path, 'a') as f:
                    f.write(json.dumps({
                        'sessionId': 'debug-session',
                        'runId': 'run1',
                        'hypothesisId': 'E',
                        'location': 'scheduler.py:174',
                        'message': 'Exception in fetcher loop',
                        'data': {'source_name': source_name, 'error': str(e), 'error_type': type(e).__name__},
                        'timestamp': int(datetime.utcnow().timestamp() * 1000)
                    }) + '\n')
            except: pass
            # #endregion
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
    
    # #region agent log
    try:
        with open(log_path, 'a') as f:
            f.write(json.dumps({
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'A',
                'location': 'scheduler.py:187',
                'message': 'fetch_all_opportunities exit',
                'data': {'total_fetched': results['total_fetched'], 'total_new': results['total_new'], 'total_updated': results['total_updated'], 'total_errors': results['total_errors']},
                'timestamp': int(datetime.utcnow().timestamp() * 1000)
            }) + '\n')
    except: pass
    # #endregion
    
    return results


def get_fetch_logs(limit: int = 50) -> List[Dict]:
    """Get recent fetch logs"""
    return fetch_logger.get_logs(limit)

