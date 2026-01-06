"""
Configuration management for opportunity fetchers.
Loads configuration from environment variables.
"""
import os
from typing import List, Dict

class FetcherConfig:
    """Configuration for opportunity fetchers"""
    
    # API Keys (optional - fetchers will skip if not configured)
    JOOBLE_API_KEY = os.environ.get('JOOBLE_API_KEY', '')
    AUTHENTIC_JOBS_API_KEY = os.environ.get('AUTHENTIC_JOBS_API_KEY', '')
    MEETUP_API_KEY = os.environ.get('MEETUP_API_KEY', '')
    
    # RSS Feed URLs (comma-separated)
    RSS_FEEDS = os.environ.get('RSS_FEEDS', '').split(',') if os.environ.get('RSS_FEEDS') else []
    
    # Default RSS feeds (no auth needed)
    DEFAULT_RSS_FEEDS = [
        'https://jobs.github.com/positions.atom',
        'https://stackoverflow.com/jobs/feed',
    ]
    
    # Enabled fetchers (comma-separated list)
    ENABLED_FETCHERS_STR = os.environ.get('ENABLED_FETCHERS', '')
    ENABLED_FETCHERS = [f.strip() for f in ENABLED_FETCHERS_STR.split(',') if f.strip()] if ENABLED_FETCHERS_STR else []
    
    # Default enabled fetchers (all free, no auth needed)
    DEFAULT_ENABLED_FETCHERS = [
        'graphql_jobs',
        'github_jobs_rss',
        'stackoverflow_jobs_rss',
    ]
    
    # Fetch interval (hours)
    FETCH_INTERVAL_HOURS = int(os.environ.get('FETCH_INTERVAL_HOURS', '24'))
    
    # Rate limiting
    RATE_LIMIT_PER_SOURCE = int(os.environ.get('RATE_LIMIT_PER_SOURCE', '100'))
    
    @classmethod
    def get_enabled_fetchers(cls) -> List[str]:
        """Get list of enabled fetcher names"""
        if cls.ENABLED_FETCHERS:
            return cls.ENABLED_FETCHERS
        return cls.DEFAULT_ENABLED_FETCHERS
    
    @classmethod
    def get_rss_feeds(cls) -> List[str]:
        """Get list of RSS feed URLs"""
        feeds = list(cls.DEFAULT_RSS_FEEDS)
        if cls.RSS_FEEDS:
            feeds.extend([f.strip() for f in cls.RSS_FEEDS if f.strip()])
        return feeds
    
    @classmethod
    def is_fetcher_enabled(cls, fetcher_name: str) -> bool:
        """Check if a fetcher is enabled"""
        enabled = cls.get_enabled_fetchers()
        return fetcher_name in enabled or len(enabled) == 0  # Empty list means all enabled

