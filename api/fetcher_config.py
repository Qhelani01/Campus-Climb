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
    # Note: GitHub Jobs was shut down, Stack Overflow blocks bots
    # Using Reddit feeds which are more accessible
    # Focus on subreddits that have actual job postings (not "for hire" posts)
    DEFAULT_RSS_FEEDS = [
        'https://stackoverflow.com/jobs/feed',  # May be blocked, but worth trying
        'https://www.reddit.com/r/jobbit/.rss',   # Reddit job board (more job postings)
        'https://www.reddit.com/r/remotejs/.rss', # Remote JS jobs
        'https://www.reddit.com/r/jobopenings/.rss',  # Job openings subreddit
        'https://www.reddit.com/r/internships/.rss',  # Internships subreddit
        # Note: /r/forhire is excluded as it has too many "for hire" posts mixed with actual opportunities
    ]
    
    # Enabled fetchers (comma-separated list)
    ENABLED_FETCHERS_STR = os.environ.get('ENABLED_FETCHERS', '')
    ENABLED_FETCHERS = [f.strip() for f in ENABLED_FETCHERS_STR.split(',') if f.strip()] if ENABLED_FETCHERS_STR else []
    
    # Default enabled fetchers (all free, no auth needed)
    # Note: GitHub Jobs was shut down, Stack Overflow blocks bots
    # Reddit feeds are more accessible
    DEFAULT_ENABLED_FETCHERS = [
        'stackoverflow_jobs_rss',  # Try it, but may be blocked
        # 'graphql_jobs',  # Domain doesn't exist
        # 'github_jobs_rss',  # GitHub Jobs was shut down
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

