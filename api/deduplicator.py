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
from sqlalchemy import text
import json

# Import db and Opportunity lazily to avoid circular imports
def get_db():
    """Get database instance from Flask app"""
    # Get db from the current Flask app context
    # Flask-SQLAlchemy stores the db instance in the app
    from flask import current_app
    from flask_sqlalchemy import SQLAlchemy
    
    # Check if we're in app context
    try:
        app = current_app._get_current_object()
    except RuntimeError:
        raise RuntimeError("Database access requires Flask app context. Ensure fetch_all_opportunities is called within app.app_context()")
    
    # Get the SQLAlchemy extension from the app
    # Flask-SQLAlchemy registers itself, and we can access db through it
    if hasattr(app, 'extensions') and 'sqlalchemy' in app.extensions:
        # The extension object has the db attribute
        sqlalchemy_ext = app.extensions['sqlalchemy']
        if hasattr(sqlalchemy_ext, 'db'):
            return sqlalchemy_ext.db
    
    # Fallback: import directly (should work if app context is properly set)
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from api.index import db
    return db

def get_opportunity_model():
    """Get Opportunity model"""
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    from api.index import Opportunity
    return Opportunity

def deduplicate_opportunity(opportunity_dict: Dict, db=None, Opportunity=None) -> Tuple[Optional[object], bool]:
    """
    Check if opportunity already exists and return existing or None.
    
    Args:
        opportunity_dict: Dictionary with opportunity data including source and source_id
        db: SQLAlchemy database instance (optional, will be retrieved if not provided)
        Opportunity: Opportunity model class (optional, will be retrieved if not provided)
    
    Returns:
        Tuple of (existing_opportunity_or_None, is_duplicate)
    """
    if db is None:
    db = get_db()
    if Opportunity is None:
    Opportunity = get_opportunity_model()
    
    source = opportunity_dict.get('source')
    source_id = opportunity_dict.get('source_id')
    title = opportunity_dict.get('title', '').strip()
    company = opportunity_dict.get('company', '').strip()
    opp_type = opportunity_dict.get('type', '')
    
    # Log what we're checking
    print(f"DEDUP CHECK: source={source}, source_id={source_id}, title={title[:50]}, company={company[:30]}")
    
    # First, try exact match by source + source_id
    if source and source_id:
        # Use db.session.query() instead of Opportunity.query to avoid app context issues
        existing = db.session.query(Opportunity).filter_by(
            source=source,
            source_id=source_id,
            is_deleted=False
        ).first()
        
        if existing:
            print(f"DEDUP MATCH: Found existing by source+source_id: ID={existing.id}")
            return existing, True
    
    # Second, try fuzzy match by title + company + type
    if title and company:
        # Use db.session.query() instead of Opportunity.query to avoid app context issues
        existing = db.session.query(Opportunity).filter(
            Opportunity.title.ilike(f'%{title}%'),
            Opportunity.company.ilike(f'%{company}%'),
            Opportunity.type == opp_type,
            (Opportunity.is_deleted == False) | (Opportunity.is_deleted.is_(None))
        ).first()
        
        if existing:
            # Check similarity (simple check - titles are very similar)
            is_similar = titles_similar(title, existing.title)
            print(f"DEDUP FUZZY: Found existing by title+company, similarity={is_similar}, existing_id={existing.id}")
            if is_similar:
                return existing, True
    
    print(f"DEDUP RESULT: No duplicate found, will create new opportunity")
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


def save_or_update_opportunity(opportunity_dict: Dict, db=None, Opportunity=None) -> Tuple:
    """
    Save opportunity or update existing one if duplicate found.
    
    Args:
        opportunity_dict: Dictionary with opportunity data
        db: SQLAlchemy database instance (optional, will be retrieved if not provided)
        Opportunity: Opportunity model class (optional, will be retrieved if not provided)
    
    Returns:
        Tuple of (opportunity_object, is_new)
    """
    log_path = '/Users/qhelanimoyo/Desktop/Projects/Campus Climb/.cursor/debug.log'
    # #region agent log
    try:
        with open(log_path, 'a') as f:
            f.write(json.dumps({
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'C',
                'location': 'deduplicator.py:132',
                'message': 'save_or_update_opportunity entry',
                'data': {'title': opportunity_dict.get('title', '')[:50], 'source': opportunity_dict.get('source'), 'source_id': opportunity_dict.get('source_id'), 'db_provided': db is not None, 'Opportunity_provided': Opportunity is not None},
                'timestamp': int(datetime.utcnow().timestamp() * 1000)
            }) + '\n')
    except: pass
    # #endregion
    
    if db is None:
    db = get_db()
    if Opportunity is None:
    Opportunity = get_opportunity_model()
    
    # #region agent log
    try:
        with open(log_path, 'a') as f:
            f.write(json.dumps({
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'C',
                'location': 'deduplicator.py:145',
                'message': 'Before deduplicate_opportunity',
                'data': {},
                'timestamp': int(datetime.utcnow().timestamp() * 1000)
            }) + '\n')
    except: pass
    # #endregion
    
    try:
        existing, is_duplicate = deduplicate_opportunity(opportunity_dict, db=db, Opportunity=Opportunity)
    except Exception as dedup_err:
        # #region agent log
        import traceback
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'D',
                    'location': 'deduplicator.py:201',
                    'message': 'Error in deduplicate_opportunity',
                    'data': {
                        'error': str(dedup_err),
                        'error_type': type(dedup_err).__name__,
                        'error_traceback': traceback.format_exc()[:500],
                        'opp_title': opportunity_dict.get('title', '')[:50]
                    },
                    'timestamp': int(datetime.utcnow().timestamp() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        # Print detailed error to stdout (visible in Vercel logs)
        print(f"ERROR in deduplicate_opportunity:")
        print(f"  Title: {opportunity_dict.get('title', '')[:50]}")
        print(f"  Source: {opportunity_dict.get('source')}, Source ID: {opportunity_dict.get('source_id')}")
        print(f"  Error Type: {type(dedup_err).__name__}")
        print(f"  Error Message: {str(dedup_err)}")
        print(f"  Full Traceback:")
        traceback.print_exc()
        raise
    
    # #region agent log
    try:
        with open(log_path, 'a') as f:
            f.write(json.dumps({
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'C,F',
                'location': 'deduplicator.py:235',
                'message': 'After deduplicate_opportunity',
                'data': {
                    'is_duplicate': is_duplicate,
                    'existing_id': existing.id if existing else None,
                    'will_update': is_duplicate and existing is not None,
                    'will_create': not is_duplicate,
                    'source': opportunity_dict.get('source'),
                    'source_id': opportunity_dict.get('source_id'),
                    'has_source': bool(opportunity_dict.get('source')),
                    'has_source_id': bool(opportunity_dict.get('source_id')),
                    'title': opportunity_dict.get('title', '')[:50]
                },
                'timestamp': int(datetime.utcnow().timestamp() * 1000)
            }) + '\n')
    except: pass
    # #endregion
    
    # Print to stdout for Vercel logs
    print(f"DEDUP RESULT: is_duplicate={is_duplicate}, existing_id={existing.id if existing else None}, will_create={not is_duplicate}, source={opportunity_dict.get('source')}, source_id={opportunity_dict.get('source_id')}")
    
    if is_duplicate and existing:
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'C',
                    'location': 'deduplicator.py:148',
                    'message': 'Updating existing opportunity',
                    'data': {'existing_id': existing.id},
                    'timestamp': int(datetime.utcnow().timestamp() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
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
                existing.deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
            except:
                pass
        
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'C',
                    'location': 'deduplicator.py:171',
                    'message': 'Before db.session.commit (update)',
                    'data': {},
                    'timestamp': int(datetime.utcnow().timestamp() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        try:
        db.session.commit()
        except Exception as db_err:
            # #region agent log
            import traceback
            error_traceback = traceback.format_exc()
            try:
                with open(log_path, 'a') as f:
                    f.write(json.dumps({
                        'sessionId': 'debug-session',
                        'runId': 'run1',
                        'hypothesisId': 'C,D',
                        'location': 'deduplicator.py:272',
                        'message': 'Database commit error (update)',
                        'data': {
                            'error': str(db_err),
                            'error_type': type(db_err).__name__,
                            'error_traceback': error_traceback[:500],
                            'existing_id': existing.id if existing else None,
                            'opp_title': opportunity_dict.get('title', '')[:50]
                        },
                        'timestamp': int(datetime.utcnow().timestamp() * 1000)
                    }) + '\n')
            except: pass
            # #endregion
            # Print detailed error to stdout (visible in Vercel logs)
            print(f"ERROR committing updated opportunity to database:")
            print(f"  Existing ID: {existing.id if existing else None}")
            print(f"  Title: {opportunity_dict.get('title', '')[:50]}")
            print(f"  Error Type: {type(db_err).__name__}")
            print(f"  Error Message: {str(db_err)}")
            print(f"  Full Traceback:")
            print(error_traceback)
            db.session.rollback()
            raise
        
        return existing, False
    else:
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'C',
                    'location': 'deduplicator.py:177',
                    'message': 'Creating new opportunity',
                    'data': {},
                    'timestamp': int(datetime.utcnow().timestamp() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        # Create new opportunity
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'C',
                    'location': 'deduplicator.py:309',
                    'message': 'Creating Opportunity object',
                    'data': {
                        'title': opportunity_dict.get('title', '')[:50],
                        'has_company': bool(opportunity_dict.get('company')),
                        'has_location': bool(opportunity_dict.get('location')),
                        'has_type': bool(opportunity_dict.get('type')),
                        'has_category': bool(opportunity_dict.get('category')),
                        'has_description': bool(opportunity_dict.get('description')),
                        'source': opportunity_dict.get('source'),
                        'source_id': opportunity_dict.get('source_id')
                    },
                    'timestamp': int(datetime.utcnow().timestamp() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        # Validate required fields before creating
        title = opportunity_dict.get('title', '').strip()
        company = opportunity_dict.get('company', '').strip()
        location = opportunity_dict.get('location', '').strip()
        description = opportunity_dict.get('description', '').strip()
        
        if not title:
            raise ValueError("Title is required but was empty")
        if not company:
            raise ValueError("Company is required but was empty")
        if not location:
            raise ValueError("Location is required but was empty")
        if not description:
            # Description is required in the model, use a default if missing
            description = "No description provided"
            print(f"WARNING: Empty description for opportunity '{title[:50]}', using default")
        
        # Create new opportunity
        new_opp = Opportunity(
            title=title,
            company=company,
            location=location,
            type=opportunity_dict.get('type', 'job'),
            category=opportunity_dict.get('category', 'General'),
            description=description,
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
                new_opp.deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
            except:
                pass
        
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'C',
                    'location': 'deduplicator.py:201',
                    'message': 'Before db.session.add and commit (new)',
                    'data': {},
                    'timestamp': int(datetime.utcnow().timestamp() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        db.session.add(new_opp)
        try:
            db.session.commit()
            print(f"SUCCESS: Created new opportunity ID {new_opp.id if new_opp else 'None'}")
            print(f"SUCCESS: Created new opportunity ID {new_opp.id if new_opp else 'None'}")
        except Exception as db_err:
            # #region agent log
            import traceback
            error_traceback = traceback.format_exc()
            try:
                with open(log_path, 'a') as f:
                    f.write(json.dumps({
                        'sessionId': 'debug-session',
                        'runId': 'run1',
                        'hypothesisId': 'C,D',
                        'location': 'deduplicator.py:446',
                        'message': 'Database commit error (new)',
                        'data': {
                            'error': str(db_err),
                            'error_type': type(db_err).__name__,
                            'error_traceback': error_traceback[:500],
                            'opp_title': opportunity_dict.get('title', '')[:50],
                            'opp_source': opportunity_dict.get('source'),
                            'opp_source_id': opportunity_dict.get('source_id')
                        },
                        'timestamp': int(datetime.utcnow().timestamp() * 1000)
                    }) + '\n')
            except: pass
            # #endregion
            # Print detailed error to stdout (visible in Vercel logs)
            print(f"ERROR committing new opportunity to database:")
            print(f"  Title: {opportunity_dict.get('title', '')[:50]}")
            print(f"  Source: {opportunity_dict.get('source')}, Source ID: {opportunity_dict.get('source_id')}")
            print(f"  Error Type: {type(db_err).__name__}")
            print(f"  Error Message: {str(db_err)}")
            print(f"  Full Traceback:")
            print(error_traceback)
            db.session.rollback()
            raise
        
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'C',
                    'location': 'deduplicator.py:490',
                    'message': 'After db.session.commit (new)',
                    'data': {'new_opp_id': new_opp.id if new_opp else None},
                    'timestamp': int(datetime.utcnow().timestamp() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        return new_opp, True

