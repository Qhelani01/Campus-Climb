#!/usr/bin/env python3
"""Check database for auto-fetched opportunities"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))
os.chdir(os.path.join(os.path.dirname(__file__), 'api'))

from index import app, db, Opportunity
from datetime import datetime, timedelta

with app.app_context():
    total = Opportunity.query.filter_by(auto_fetched=True).count()
    print(f"Total auto-fetched opportunities: {total}")
    
    # Check recent ones (last hour)
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    recent = Opportunity.query.filter(
        Opportunity.auto_fetched == True,
        Opportunity.created_at >= one_hour_ago
    ).order_by(Opportunity.created_at.desc()).limit(10).all()
    
    print(f"\nOpportunities created in last hour: {len(recent)}")
    for opp in recent[:5]:
        print(f"  - {opp.title[:60]}... (source: {opp.source}, created: {opp.created_at})")
