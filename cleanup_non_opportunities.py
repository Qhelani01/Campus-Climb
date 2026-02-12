#!/usr/bin/env python3
"""
One-time script to find and soft-delete existing opportunities that the AI
classifies as non-opportunities (questions, discussions, etc.).

Usage:
  python3 cleanup_non_opportunities.py           # Run against all opportunities
  python3 cleanup_non_opportunities.py --dry-run   # Preview only, no deletions
  python3 cleanup_non_opportunities.py --source reddit   # Only reddit_* sources
"""
import sys
import os
import argparse

_project_root = os.path.dirname(os.path.abspath(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# App and models live under api/
os.chdir(os.path.join(_project_root, 'api'))
from api.index import app, db, Opportunity


def main():
    parser = argparse.ArgumentParser(description='Soft-delete opportunities classified as non-opportunities by AI')
    parser.add_argument('--dry-run', action='store_true', help='Only report what would be deleted; do not delete')
    parser.add_argument('--source', type=str, default='', help='Only process sources containing this (e.g. reddit)')
    parser.add_argument('--limit', type=int, default=None, help='Max number of opportunities to check (for testing)')
    args = parser.parse_args()

    with app.app_context():
        from api.ai_filter import classify_opportunity

        # Load active opportunities
        query = Opportunity.active_query().order_by(Opportunity.id.asc())
        if args.source:
            query = query.filter(Opportunity.source.ilike(f'%{args.source}%'))
        if args.limit:
            query = query.limit(args.limit)

        opportunities = query.all()
        total = len(opportunities)

        print("=" * 60)
        print("Cleanup: Remove non-opportunities (AI classification)")
        print("=" * 60)
        print(f"Opportunities to check: {total}")
        if args.source:
            print(f"Filtered by source containing: {args.source}")
        if args.dry_run:
            print("Mode: DRY RUN (no changes will be made)")
        print()

        if total == 0:
            print("Nothing to check.")
            return 0

        to_delete = []
        errors = 0
        for i, opp in enumerate(opportunities, 1):
            title = opp.title or ''
            description = (opp.description or '')[:500]
            source = opp.source or 'unknown'
            try:
                result = classify_opportunity(title, description, source)
                is_opportunity = result.get('is_opportunity')
                confidence = result.get('confidence', 0)
                err = result.get('error')

                if err:
                    # AI failed (e.g. timeout) – skip; don't delete on uncertainty
                    print(f"  [{i}/{total}] SKIP (AI error): {title[:50]}...")
                    errors += 1
                    continue

                if is_opportunity is False:
                    to_delete.append((opp, confidence))
                    print(f"  [{i}/{total}] NON-OPP (confidence={confidence:.2f}): {title[:50]}...")
                else:
                    print(f"  [{i}/{total}] OK: {title[:50]}...")
            except Exception as e:
                print(f"  [{i}/{total}] ERROR: {title[:50]}... -> {e}")
                errors += 1

        print()
        print("=" * 60)
        print(f"Summary: {len(to_delete)} non-opportunities, {total - len(to_delete) - errors} kept, {errors} errors")
        print("=" * 60)

        if not to_delete:
            print("No non-opportunities to remove.")
            return 0

        if args.dry_run:
            print("\nWould soft-delete these opportunities:")
            for opp, _ in to_delete:
                print(f"  - id={opp.id} | {opp.title[:60]}...")
            print("\nRun without --dry-run to apply.")
            return 0

        # Soft-delete
        for opp, _ in to_delete:
            opp.is_deleted = True
        db.session.commit()
        print(f"\nSoft-deleted {len(to_delete)} opportunities.")

        return 0


if __name__ == '__main__':
    sys.exit(main())
