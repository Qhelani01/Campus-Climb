"""
RSS Feed Fetcher for opportunities.
Fetches from GitHub Jobs, Stack Overflow Jobs, Eventbrite, and other RSS feeds.
"""
import feedparser
import requests
from datetime import datetime
from typing import List, Dict, Optional
from api.opportunity_fetchers import OpportunityFetcher

class RSSFetcher(OpportunityFetcher):
    """Fetcher for RSS/Atom feeds"""
    
    def __init__(self, feed_url: str, source_name: str):
        super().__init__(source_name)
        self.feed_url = feed_url
    
    def fetch(self) -> List[Dict]:
        """Fetch opportunities from RSS feed"""
        try:
            # Parse RSS feed
            feed = feedparser.parse(self.feed_url)
            
            if feed.bozo:
                print(f"Warning: RSS feed parsing issues for {self.feed_url}: {feed.bozo_exception}")
            
            opportunities = []
            for entry in feed.entries:
                try:
                    opp = self.parse_entry(entry)
                    if opp:
                        opportunities.append(self.normalize(opp))
                except Exception as e:
                    print(f"Error parsing RSS entry: {e}")
                    continue
            
            self.fetch_count = len(opportunities)
            return opportunities
        except Exception as e:
            print(f"Error fetching RSS feed {self.feed_url}: {e}")
            self.error_count += 1
            return []
    
    def parse_entry(self, entry: Dict) -> Optional[Dict]:
        """Parse a single RSS entry"""
        # Extract basic info
        title = entry.get('title', '').strip()
        if not title:
            return None
        
        # Get description
        description = ''
        if 'summary' in entry:
            description = entry.summary
        elif 'description' in entry:
            description = entry.description
        elif 'content' in entry and len(entry.content) > 0:
            description = entry.content[0].get('value', '')
        
        # Clean HTML from description
        description = self.clean_html(description)
        
        # Get link
        link = entry.get('link', '')
        
        # Extract company (try various fields)
        company = self.extract_company(entry, title)
        
        # Extract location
        location = self.extract_location(entry, description)
        
        # Extract date
        deadline = None
        if 'published' in entry or 'updated' in entry:
            date_str = entry.get('published') or entry.get('updated')
            deadline = self.parse_date(date_str)
        
        # Generate source_id from link or title
        source_id = link.split('/')[-1] if link else title.lower().replace(' ', '-')
        
        return {
            'title': title,
            'company': company,
            'location': location or 'Remote',
            'type': self.determine_type(title, description, self.source_name),
            'category': self.categorize_by_keywords(title, description),
            'description': description or title,
            'application_url': link,
            'source_id': source_id,
            'source_url': link
        }
    
    def extract_company(self, entry: Dict, title: str) -> str:
        """Extract company name from entry"""
        # Try various fields
        if 'author' in entry:
            return entry.author
        elif 'company' in entry:
            return entry.company
        elif 'publisher' in entry:
            return entry.publisher
        else:
            # Try to extract from title (e.g., "Software Engineer at Google")
            if ' at ' in title:
                return title.split(' at ')[-1].strip()
            elif ' - ' in title:
                parts = title.split(' - ')
                if len(parts) > 1:
                    return parts[-1].strip()
            return 'Unknown Company'
    
    def extract_location(self, entry: Dict, description: str) -> Optional[str]:
        """Extract location from entry"""
        # Try location field
        if 'location' in entry:
            return entry.location
        
        # Try to extract from description
        # Common patterns: "Location: City, State" or "Based in City"
        import re
        location_patterns = [
            r'location[:\s]+([A-Z][a-z]+(?:\s*,\s*[A-Z]{2})?)',
            r'based in ([A-Z][a-z]+(?:\s*,\s*[A-Z]{2})?)',
            r'([A-Z][a-z]+,\s*[A-Z]{2})',
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def clean_html(self, text: str) -> str:
        """Remove HTML tags from text"""
        if not text:
            return ''
        
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(text, 'html.parser')
            return soup.get_text(separator=' ', strip=True)
        except:
            # Fallback: simple regex removal
            import re
            return re.sub(r'<[^>]+>', '', text)
    
    def normalize(self, raw_opportunity: Dict) -> Dict:
        """Normalize RSS opportunity data"""
        normalized = super().normalize(raw_opportunity)
        normalized['source'] = self.source_name
        normalized['auto_fetched'] = True
        return normalized


class GitHubJobsFetcher(RSSFetcher):
    """Fetcher for GitHub Jobs RSS feed"""
    
    def __init__(self):
        super().__init__(
            feed_url='https://jobs.github.com/positions.atom',
            source_name='github_jobs'
        )
    
    def extract_company(self, entry: Dict, title: str) -> str:
        """GitHub Jobs has company in author field"""
        return entry.get('author', {}).get('name', 'Unknown Company') if isinstance(entry.get('author'), dict) else entry.get('author', 'Unknown Company')


class StackOverflowJobsFetcher(RSSFetcher):
    """Fetcher for Stack Overflow Jobs RSS feed"""
    
    def __init__(self):
        super().__init__(
            feed_url='https://stackoverflow.com/jobs/feed',
            source_name='stackoverflow_jobs'
        )


class EventbriteFetcher(RSSFetcher):
    """Fetcher for Eventbrite RSS feeds"""
    
    def __init__(self, feed_url: str = None):
        # Eventbrite category feeds (example - can be customized)
        default_url = 'https://www.eventbrite.com/rss'
        super().__init__(
            feed_url=feed_url or default_url,
            source_name='eventbrite'
        )
    
    def determine_type(self, title: str, description: str, source: str) -> str:
        """Eventbrite events are typically workshops or conferences"""
        text = (title + ' ' + description).lower()
        if 'conference' in text:
            return 'conference'
        elif 'workshop' in text:
            return 'workshop'
        elif 'competition' in text or 'hackathon' in text:
            return 'competition'
        else:
            return 'workshop'

