"""
API-based fetchers for opportunities.
Includes GraphQL Jobs, Jooble, Authentic Jobs, and Meetup APIs.
"""
import sys
import os
# Add project root to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import requests
import json
from datetime import datetime
from typing import List, Dict, Optional
from api.opportunity_fetchers import OpportunityFetcher

class GraphQLJobsFetcher(OpportunityFetcher):
    """Fetcher for GraphQL Jobs API (free, no auth required)"""
    
    def __init__(self):
        super().__init__('graphql_jobs')
        self.api_url = 'https://api.graphql.jobs'
    
    def fetch(self) -> List[Dict]:
        """Fetch opportunities from GraphQL Jobs API"""
        try:
            # GraphQL query
            query = """
            {
                jobs {
                    id
                    title
                    company {
                        name
                    }
                    locationNames
                    description
                    applyUrl
                    postedAt
                    tags {
                        name
                    }
                }
            }
            """
            
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.post(
                self.api_url,
                json={'query': query},
                headers=headers,
                timeout=30,
                verify=True
            )
            response.raise_for_status()
            
            data = response.json()
            if 'errors' in data:
                print(f"GraphQL API errors: {data['errors']}")
                return []
            
            jobs = data.get('data', {}).get('jobs', [])
            opportunities = []
            
            for job in jobs:
                try:
                    opp = self.parse_job(job)
                    if opp:
                        opportunities.append(self.normalize(opp))
                except Exception as e:
                    print(f"Error parsing GraphQL job: {e}")
                    continue
            
            self.fetch_count = len(opportunities)
            print(f"Successfully fetched {len(opportunities)} opportunities from {self.source_name}")
            return opportunities
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching from GraphQL Jobs API: {e}")
            self.error_count += 1
            return []
        except Exception as e:
            print(f"Error fetching from GraphQL Jobs API: {e}")
            import traceback
            traceback.print_exc()
            self.error_count += 1
            return []
    
    def parse_job(self, job: Dict) -> Optional[Dict]:
        """Parse a GraphQL Jobs API response"""
        company = job.get('company', {})
        company_name = company.get('name', 'Unknown Company') if isinstance(company, dict) else str(company)
        
        locations = job.get('locationNames', [])
        location = ', '.join(locations) if locations else 'Remote'
        
        tags = job.get('tags', [])
        category = tags[0].get('name', 'Technology') if tags and isinstance(tags[0], dict) else 'Technology'
        
        return {
            'title': job.get('title', ''),
            'company': company_name,
            'location': location,
            'type': 'job',
            'category': category,
            'description': job.get('description', ''),
            'application_url': job.get('applyUrl', ''),
            'source_id': job.get('id', ''),
            'source_url': job.get('applyUrl', '')
        }
    
    def normalize(self, raw_opportunity: Dict) -> Dict:
        """Normalize GraphQL Jobs opportunity"""
        normalized = super().normalize(raw_opportunity)
        normalized['source'] = self.source_name
        normalized['auto_fetched'] = True
        return normalized


class JoobleFetcher(OpportunityFetcher):
    """Fetcher for Jooble API (free, requires API key)"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__('jooble')
        self.api_key = api_key or os.environ.get('JOOBLE_API_KEY')
        self.api_url = 'https://jooble.org/api/'
    
    def fetch(self) -> List[Dict]:
        """Fetch opportunities from Jooble API"""
        if not self.api_key:
            print("Jooble API key not configured. Skipping Jooble fetcher.")
            return []
        
        try:
            # Search for jobs (can be customized with keywords, location, etc.)
            headers = {
                'Content-Type': 'application/json'
            }
            
            payload = {
                'keywords': 'internship OR job OR opportunity',
                'location': 'United States',
                'radius': '25',
                'page': 1,
                'searchMode': 1
            }
            
            response = requests.post(
                f"{self.api_url}{self.api_key}",
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            jobs = data.get('jobs', [])
            opportunities = []
            
            for job in jobs:
                try:
                    opp = self.parse_job(job)
                    if opp:
                        opportunities.append(self.normalize(opp))
                except Exception as e:
                    print(f"Error parsing Jooble job: {e}")
                    continue
            
            self.fetch_count = len(opportunities)
            return opportunities
        except Exception as e:
            print(f"Error fetching from Jooble API: {e}")
            self.error_count += 1
            return []
    
    def parse_job(self, job: Dict) -> Optional[Dict]:
        """Parse a Jooble API response"""
        return {
            'title': job.get('title', ''),
            'company': job.get('company', 'Unknown Company'),
            'location': job.get('location', 'Unknown Location'),
            'type': self.determine_type(job.get('title', ''), job.get('snippet', ''), 'jooble'),
            'category': self.categorize_by_keywords(job.get('title', ''), job.get('snippet', '')),
            'description': job.get('snippet', ''),
            'application_url': job.get('link', ''),
            'source_id': job.get('id', ''),
            'source_url': job.get('link', '')
        }
    
    def normalize(self, raw_opportunity: Dict) -> Dict:
        """Normalize Jooble opportunity"""
        normalized = super().normalize(raw_opportunity)
        normalized['source'] = self.source_name
        normalized['auto_fetched'] = True
        return normalized


class AuthenticJobsFetcher(OpportunityFetcher):
    """Fetcher for Authentic Jobs API (free, requires API key)"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__('authentic_jobs')
        self.api_key = api_key or os.environ.get('AUTHENTIC_JOBS_API_KEY')
        self.api_url = 'https://authenticjobs.com/api/'
    
    def fetch(self) -> List[Dict]:
        """Fetch opportunities from Authentic Jobs API"""
        if not self.api_key:
            print("Authentic Jobs API key not configured. Skipping Authentic Jobs fetcher.")
            return []
        
        try:
            params = {
                'api_key': self.api_key,
                'method': 'aj.jobs.search',
                'format': 'json',
                'perpage': 100
            }
            
            response = requests.get(self.api_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            listings = data.get('listings', {}).get('listing', [])
            if not isinstance(listings, list):
                listings = [listings] if listings else []
            
            opportunities = []
            for listing in listings:
                try:
                    opp = self.parse_listing(listing)
                    if opp:
                        opportunities.append(self.normalize(opp))
                except Exception as e:
                    print(f"Error parsing Authentic Jobs listing: {e}")
                    continue
            
            self.fetch_count = len(opportunities)
            return opportunities
        except Exception as e:
            print(f"Error fetching from Authentic Jobs API: {e}")
            self.error_count += 1
            return []
    
    def parse_listing(self, listing: Dict) -> Optional[Dict]:
        """Parse an Authentic Jobs API response"""
        company = listing.get('company', {})
        company_name = company.get('name', 'Unknown Company') if isinstance(company, dict) else str(company)
        
        return {
            'title': listing.get('title', ''),
            'company': company_name,
            'location': listing.get('location', {}).get('name', 'Remote') if isinstance(listing.get('location'), dict) else listing.get('location', 'Remote'),
            'type': listing.get('type', {}).get('name', 'job') if isinstance(listing.get('type'), dict) else 'job',
            'category': listing.get('category', {}).get('name', 'Technology') if isinstance(listing.get('category'), dict) else 'Technology',
            'description': listing.get('description', ''),
            'application_url': listing.get('url', ''),
            'source_id': str(listing.get('id', '')),
            'source_url': listing.get('url', '')
        }
    
    def normalize(self, raw_opportunity: Dict) -> Dict:
        """Normalize Authentic Jobs opportunity"""
        normalized = super().normalize(raw_opportunity)
        normalized['source'] = self.source_name
        normalized['auto_fetched'] = True
        return normalized


class MeetupFetcher(OpportunityFetcher):
    """Fetcher for Meetup API (free, requires API key)"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__('meetup')
        self.api_key = api_key or os.environ.get('MEETUP_API_KEY')
        self.api_url = 'https://api.meetup.com'
    
    def fetch(self) -> List[Dict]:
        """Fetch opportunities from Meetup API"""
        if not self.api_key:
            print("Meetup API key not configured. Skipping Meetup fetcher.")
            return []
        
        try:
            # Search for events (workshops, conferences, etc.)
            params = {
                'key': self.api_key,
                'text': 'workshop OR conference OR tech OR career',
                'radius': 'global',
                'order': 'time',
                'status': 'upcoming',
                'page': 100
            }
            
            response = requests.get(
                f"{self.api_url}/find/events",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            events = response.json()
            if not isinstance(events, list):
                events = []
            
            opportunities = []
            for event in events:
                try:
                    opp = self.parse_event(event)
                    if opp:
                        opportunities.append(self.normalize(opp))
                except Exception as e:
                    print(f"Error parsing Meetup event: {e}")
                    continue
            
            self.fetch_count = len(opportunities)
            return opportunities
        except Exception as e:
            print(f"Error fetching from Meetup API: {e}")
            self.error_count += 1
            return []
    
    def parse_event(self, event: Dict) -> Optional[Dict]:
        """Parse a Meetup API event response"""
        group = event.get('group', {})
        group_name = group.get('name', 'Unknown Group') if isinstance(group, dict) else str(group)
        
        venue = event.get('venue', {})
        location = 'Remote'
        if venue:
            city = venue.get('city', '') if isinstance(venue, dict) else ''
            state = venue.get('state', '') if isinstance(venue, dict) else ''
            if city:
                location = f"{city}, {state}".strip(', ')
        
        return {
            'title': event.get('name', ''),
            'company': group_name,
            'location': location,
            'type': self.determine_type(event.get('name', ''), event.get('description', ''), 'meetup'),
            'category': self.categorize_by_keywords(event.get('name', ''), event.get('description', '')),
            'description': event.get('description', ''),
            'application_url': event.get('link', ''),
            'deadline': self.parse_date(event.get('local_date', '')),
            'source_id': event.get('id', ''),
            'source_url': event.get('link', '')
        }
    
    def normalize(self, raw_opportunity: Dict) -> Dict:
        """Normalize Meetup opportunity"""
        normalized = super().normalize(raw_opportunity)
        normalized['source'] = self.source_name
        normalized['auto_fetched'] = True
        return normalized


# Import os for environment variables
import os

