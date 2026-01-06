"""
Base class and utilities for opportunity fetchers.
All fetchers should inherit from OpportunityFetcher.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Optional

class OpportunityFetcher(ABC):
    """Base class for all opportunity fetchers"""
    
    def __init__(self, source_name: str):
        self.source_name = source_name
        self.last_fetch_time = None
        self.fetch_count = 0
        self.error_count = 0
    
    @abstractmethod
    def fetch(self) -> List[Dict]:
        """
        Fetch opportunities from the source.
        
        Returns:
            List of opportunity dictionaries with standardized format
        """
        pass
    
    def normalize(self, raw_opportunity: Dict) -> Dict:
        """
        Normalize raw opportunity data to standard format.
        
        Expected format:
        {
            'title': str,
            'company': str,
            'location': str,
            'type': str (job, internship, workshop, conference, competition),
            'category': str,
            'description': str,
            'requirements': str (optional),
            'salary': str (optional),
            'deadline': date string (optional, YYYY-MM-DD),
            'application_url': str,
            'source_id': str (unique ID from source),
            'source_url': str (original URL)
        }
        """
        return raw_opportunity
    
    def parse_date(self, date_str: Optional[str]) -> Optional[str]:
        """Parse and normalize date strings to YYYY-MM-DD format"""
        if not date_str:
            return None
        
        try:
            # Try common date formats manually
            from datetime import datetime
            # Try ISO format first
            try:
                parsed = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return parsed.strftime('%Y-%m-%d')
            except:
                pass
            
            # Try common formats
            formats = [
                '%Y-%m-%d',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d %H:%M:%S',
                '%a, %d %b %Y %H:%M:%S %Z',
                '%a, %d %b %Y %H:%M:%S %z',
                '%d %b %Y',
                '%m/%d/%Y',
            ]
            
            for fmt in formats:
                try:
                    parsed = datetime.strptime(date_str, fmt)
                    return parsed.strftime('%Y-%m-%d')
                except:
                    continue
            
            return None
        except:
            return None
    
    def categorize_by_keywords(self, title: str, description: str) -> str:
        """
        Auto-categorize opportunity based on keywords.
        Returns a category string.
        """
        text = (title + ' ' + description).lower()
        
        tech_keywords = ['software', 'developer', 'programming', 'coding', 'python', 'javascript', 'java', 'tech', 'it', 'computer']
        business_keywords = ['business', 'marketing', 'sales', 'finance', 'management', 'analyst']
        design_keywords = ['design', 'ui', 'ux', 'graphic', 'creative', 'art']
        education_keywords = ['education', 'teaching', 'research', 'academic']
        
        if any(kw in text for kw in tech_keywords):
            return 'Technology'
        elif any(kw in text for kw in business_keywords):
            return 'Business'
        elif any(kw in text for kw in design_keywords):
            return 'Design'
        elif any(kw in text for kw in education_keywords):
            return 'Education'
        else:
            return 'General'
    
    def determine_type(self, title: str, description: str, source: str) -> str:
        """
        Determine opportunity type based on content and source.
        Returns: 'job', 'internship', 'workshop', 'conference', or 'competition'
        """
        text = (title + ' ' + description).lower()
        source_lower = source.lower()
        
        # Check for explicit type indicators
        if 'internship' in text or 'intern' in text:
            return 'internship'
        elif 'conference' in text or 'conference' in source_lower:
            return 'conference'
        elif 'workshop' in text or 'workshop' in source_lower:
            return 'workshop'
        elif 'competition' in text or 'hackathon' in text or 'contest' in text:
            return 'competition'
        elif 'job' in text or 'position' in text or 'career' in text:
            return 'job'
        else:
            # Default based on source
            if 'meetup' in source_lower or 'eventbrite' in source_lower:
                return 'workshop'
            else:
                return 'job'

