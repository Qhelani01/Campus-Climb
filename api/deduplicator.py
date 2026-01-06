"""
Deduplication system for opportunities.
Prevents duplicate entries from multiple sources.
"""
import sys
import os
# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from datetime import datetime
from typing import Dict, Optional, Tuple
from api.index import db, Opportunity
from sqlalchemy import text

def deduplicate_opportunity(opportunity_dict: Dict) -> Tuple[Optional[Opportunity], bool]:
    """
    Check if opportunity already exists and return existing or None.
    
    Args:
        opportunity_dict: Dictionary with opportunity data including source and source_id
    
    Returns:
        Tuple of (existing_opportunity_or_None, is_duplicate)
    """
    source = opportunity_dict.get('source')
    source_id = opportunity_dict.get('source_id')
    title = opportunity_dict.get('title', '').strip()
    company = opportunity_dict.get('company', '').strip()
    opp_type = opportunity_dict.get('type', '')
    
    # First, try exact match by source + source_id
    if source and source_id:
        existing = Opportunity.query.filter_by(
            source=source,
            source_id=source_id,
            is_deleted=False
        ).first()
        
        if existing:
            return existing, True
    
    # Second, try fuzzy match by title + company + type
    if title and company:
        # Exact match first
        existing = Opportunity.query.filter(
            Opportunity.title.ilike(f'%{title}%'),
            Opportunity.company.ilike(f'%{company}%'),
            Opportunity.type == opp_type,
            (Opportunity.is_deleted == False) | (Opportunity.is_deleted.is_(None))
        ).first()
        
        if existing:
            # Check similarity (simple check - titles are very similar)
            if titles_similar(title, existing.title):
                return existing, True
    
    return None, False


def titles_similar(title1: str, title2: str, threshold: float = 0.85) -> bool:
    """
    Check if two titles are similar using fuzzy matching.
    
    Args:
        title1: First title
        title2: Second title
        threshold: Similarity threshold (0-1)
    
    Returns:
        True if titles are similar enough
    """
    try:
        from fuzzywuzzy import fuzz
        similarity = fuzz.ratio(title1.lower(), title2.lower()) / 100.0
        return similarity >= threshold
    except ImportError:
        # Fallback to simple string comparison if fuzzywuzzy not available
        title1_lower = title1.lower().strip()
        title2_lower = title2.lower().strip()
        
        # Exact match
        if title1_lower == title2_lower:
            return True
        
        # One contains the other
        if title1_lower in title2_lower or title2_lower in title1_lower:
            return True
        
        # Check word overlap (simple heuristic)
        words1 = set(title1_lower.split())
        words2 = set(title2_lower.split())
        if len(words1) > 0 and len(words2) > 0:
            overlap = len(words1 & words2) / max(len(words1), len(words2))
            return overlap >= threshold
        
        return False


def save_or_update_opportunity(opportunity_dict: Dict) -> Tuple[Opportunity, bool]:
    """
    Save opportunity or update existing one if duplicate found.
    
    Args:
        opportunity_dict: Dictionary with opportunity data
    
    Returns:
        Tuple of (opportunity_object, is_new)
    """
    existing, is_duplicate = deduplicate_opportunity(opportunity_dict)
    
    if is_duplicate and existing:
        # Update existing opportunity
        existing.title = opportunity_dict.get('title', existing.title)
        existing.company = opportunity_dict.get('company', existing.company)
        existing.location = opportunity_dict.get('location', existing.location)
        existing.type = opportunity_dict.get('type', existing.type)
        existing.category = opportunity_dict.get('category', existing.category)
        existing.description = opportunity_dict.get('description', existing.description)
        existing.requirements = opportunity_dict.get('requirements', existing.requirements)
        existing.salary = opportunity_dict.get('salary', existing.salary)
        existing.application_url = opportunity_dict.get('application_url', existing.application_url)
        existing.source_url = opportunity_dict.get('source_url', existing.source_url)
        existing.last_fetched = datetime.utcnow()
        existing.auto_fetched = opportunity_dict.get('auto_fetched', True)
        
        # Update deadline if provided
        deadline_str = opportunity_dict.get('deadline')
        if deadline_str:
            try:
                from datetime import datetime
                existing.deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
            except:
                pass
        
        db.session.commit()
        return existing, False
    else:
        # Create new opportunity
        new_opp = Opportunity(
            title=opportunity_dict.get('title', ''),
            company=opportunity_dict.get('company', ''),
            location=opportunity_dict.get('location', ''),
            type=opportunity_dict.get('type', 'job'),
            category=opportunity_dict.get('category', 'General'),
            description=opportunity_dict.get('description', ''),
            requirements=opportunity_dict.get('requirements'),
            salary=opportunity_dict.get('salary'),
            application_url=opportunity_dict.get('application_url'),
            source=opportunity_dict.get('source'),
            source_id=opportunity_dict.get('source_id'),
            source_url=opportunity_dict.get('source_url'),
            auto_fetched=opportunity_dict.get('auto_fetched', True),
            last_fetched=datetime.utcnow()
        )
        
        # Set deadline if provided
        deadline_str = opportunity_dict.get('deadline')
        if deadline_str:
            try:
                from datetime import datetime
                new_opp.deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
            except:
                pass
        
        db.session.add(new_opp)
        db.session.commit()
        return new_opp, True

