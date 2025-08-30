"""
Opportunities API endpoints.

This module provides REST API endpoints for:
- Creating opportunities
- Searching and filtering opportunities
- Updating opportunity information
- CSV data import/export
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
import pandas as pd
import json
import logging
import io

# Import our modules
from ..core.database import get_db
from ..models.user import User
from ..models.opportunity import (
    Opportunity, OpportunityCreate, OpportunityUpdate, 
    OpportunityResponse, OpportunityFilter, OpportunityType, OpportunityCategory
)
from ..api.auth import get_current_user

# Set up logging
logger = logging.getLogger(__name__)

# Create router for opportunity endpoints
router = APIRouter()


@router.post("/", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
async def create_opportunity(
    opportunity_create: OpportunityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new opportunity.
    
    This endpoint allows authenticated users to create new opportunities.
    In a real application, you might restrict this to admin users only.
    """
    try:
        logger.info(f"Creating opportunity: {opportunity_create.title}")
        
        # Create opportunity object
        db_opportunity = Opportunity(
            title=opportunity_create.title,
            description=opportunity_create.description,
            company_organization=opportunity_create.company_organization,
            opportunity_type=opportunity_create.opportunity_type,
            category=opportunity_create.category,
            location=opportunity_create.location,
            is_remote=opportunity_create.is_remote,
            is_hybrid=opportunity_create.is_hybrid,
            min_gpa=opportunity_create.min_gpa,
            required_majors=json.dumps(opportunity_create.required_majors) if opportunity_create.required_majors else None,
            required_skills=json.dumps(opportunity_create.required_skills) if opportunity_create.required_skills else None,
            min_graduation_year=opportunity_create.min_graduation_year,
            max_graduation_year=opportunity_create.max_graduation_year,
            salary_min=opportunity_create.salary_min,
            salary_max=opportunity_create.salary_max,
            is_paid=opportunity_create.is_paid,
            benefits=json.dumps(opportunity_create.benefits) if opportunity_create.benefits else None,
            application_deadline=opportunity_create.application_deadline,
            application_url=opportunity_create.application_url,
            contact_email=opportunity_create.contact_email,
            contact_phone=opportunity_create.contact_phone,
            tags=json.dumps(opportunity_create.tags) if opportunity_create.tags else None,
            is_active=True,
            is_featured=False
        )
        
        # Save to database
        db.add(db_opportunity)
        db.commit()
        db.refresh(db_opportunity)
        
        logger.info(f"Opportunity created successfully: {db_opportunity.id}")
        
        # Convert to response model
        return OpportunityResponse.from_orm(db_opportunity)
        
    except Exception as e:
        logger.error(f"Error creating opportunity: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating opportunity"
        )


@router.get("/", response_model=List[OpportunityResponse])
async def get_opportunities(
    skip: int = Query(0, ge=0, description="Number of opportunities to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of opportunities to return"),
    opportunity_type: Optional[OpportunityType] = Query(None, description="Filter by opportunity type"),
    category: Optional[OpportunityCategory] = Query(None, description="Filter by category"),
    location: Optional[str] = Query(None, description="Filter by location"),
    is_remote: Optional[bool] = Query(None, description="Filter by remote work availability"),
    search: Optional[str] = Query(None, description="Search in title, description, and company"),
    db: Session = Depends(get_db)
):
    """
    Get opportunities with filtering and search.
    
    This endpoint supports:
    - Pagination (skip/limit)
    - Filtering by various criteria
    - Text search across multiple fields
    - Sorting by relevance
    """
    try:
        logger.info(f"Fetching opportunities with filters: skip={skip}, limit={limit}")
        
        # Build query
        query = db.query(Opportunity).filter(Opportunity.is_active == True)
        
        # Apply filters
        if opportunity_type:
            query = query.filter(Opportunity.opportunity_type == opportunity_type)
        
        if category:
            query = query.filter(Opportunity.category == category)
        
        if location:
            query = query.filter(Opportunity.location.ilike(f"%{location}%"))
        
        if is_remote is not None:
            query = query.filter(Opportunity.is_remote == is_remote)
        
        # Apply search
        if search:
            search_filter = or_(
                Opportunity.title.ilike(f"%{search}%"),
                Opportunity.description.ilike(f"%{search}%"),
                Opportunity.company_organization.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Apply pagination and ordering
        opportunities = query.order_by(Opportunity.is_featured.desc(), Opportunity.created_at.desc()).offset(skip).limit(limit).all()
        
        logger.info(f"Retrieved {len(opportunities)} opportunities")
        
        # Convert to response models
        return [OpportunityResponse.from_orm(opp) for opp in opportunities]
        
    except Exception as e:
        logger.error(f"Error fetching opportunities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving opportunities"
        )


@router.get("/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific opportunity by ID.
    
    This endpoint also increments the view count for analytics.
    """
    try:
        logger.info(f"Fetching opportunity: {opportunity_id}")
        
        # Get opportunity
        opportunity = db.query(Opportunity).filter(
            Opportunity.id == opportunity_id,
            Opportunity.is_active == True
        ).first()
        
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found"
            )
        
        # Increment view count
        opportunity.views_count += 1
        db.commit()
        
        logger.info(f"Opportunity retrieved successfully: {opportunity_id}")
        
        return OpportunityResponse.from_orm(opportunity)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching opportunity {opportunity_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving opportunity"
        )


@router.put("/{opportunity_id}", response_model=OpportunityResponse)
async def update_opportunity(
    opportunity_id: int,
    opportunity_update: OpportunityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an opportunity.
    
    This endpoint allows authenticated users to update opportunity information.
    In a real application, you might restrict this to the creator or admin users.
    """
    try:
        logger.info(f"Updating opportunity: {opportunity_id}")
        
        # Get opportunity
        opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
        
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found"
            )
        
        # Update fields
        update_data = opportunity_update.dict(exclude_unset=True)
        
        # Handle JSON fields
        if 'required_majors' in update_data and update_data['required_majors'] is not None:
            update_data['required_majors'] = json.dumps(update_data['required_majors'])
        
        if 'required_skills' in update_data and update_data['required_skills'] is not None:
            update_data['required_skills'] = json.dumps(update_data['required_skills'])
        
        if 'benefits' in update_data and update_data['benefits'] is not None:
            update_data['benefits'] = json.dumps(update_data['benefits'])
        
        if 'tags' in update_data and update_data['tags'] is not None:
            update_data['tags'] = json.dumps(update_data['tags'])
        
        # Apply updates
        for field, value in update_data.items():
            setattr(opportunity, field, value)
        
        # Save changes
        db.commit()
        db.refresh(opportunity)
        
        logger.info(f"Opportunity updated successfully: {opportunity_id}")
        
        return OpportunityResponse.from_orm(opportunity)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating opportunity {opportunity_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating opportunity"
        )


@router.delete("/{opportunity_id}")
async def delete_opportunity(
    opportunity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an opportunity.
    
    This endpoint soft-deletes an opportunity by setting is_active to False.
    In a real application, you might restrict this to admin users only.
    """
    try:
        logger.info(f"Deleting opportunity: {opportunity_id}")
        
        # Get opportunity
        opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
        
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found"
            )
        
        # Soft delete
        opportunity.is_active = False
        db.commit()
        
        logger.info(f"Opportunity deleted successfully: {opportunity_id}")
        
        return {"message": "Opportunity deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting opportunity {opportunity_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting opportunity"
        )


@router.post("/import-csv")
async def import_opportunities_csv(
    file: UploadFile = File(..., description="CSV file with opportunity data"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Import opportunities from a CSV file.
    
    This endpoint allows bulk import of opportunities from a CSV file.
    The CSV should have columns matching the opportunity fields.
    """
    try:
        logger.info(f"CSV import request from user: {current_user.email}")
        
        # Check file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a CSV"
            )
        
        # Read CSV
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        
        # Validate required columns
        required_columns = ['title', 'description', 'company_organization', 'opportunity_type', 'category', 'location']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {missing_columns}"
            )
        
        # Process each row
        imported_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Create opportunity object
                opportunity_data = {
                    'title': row['title'],
                    'description': row['description'],
                    'company_organization': row['company_organization'],
                    'opportunity_type': row['opportunity_type'],
                    'category': row['category'],
                    'location': row['location'],
                    'is_remote': row.get('is_remote', False),
                    'is_hybrid': row.get('is_hybrid', False),
                    'min_gpa': row.get('min_gpa'),
                    'required_majors': row.get('required_majors'),
                    'required_skills': row.get('required_skills'),
                    'min_graduation_year': row.get('min_graduation_year'),
                    'max_graduation_year': row.get('max_graduation_year'),
                    'salary_min': row.get('salary_min'),
                    'salary_max': row.get('salary_max'),
                    'is_paid': row.get('is_paid', True),
                    'benefits': row.get('benefits'),
                    'application_deadline': row.get('application_deadline'),
                    'application_url': row.get('application_url'),
                    'contact_email': row.get('contact_email'),
                    'contact_phone': row.get('contact_phone'),
                    'tags': row.get('tags')
                }
                
                # Create opportunity
                db_opportunity = Opportunity(**opportunity_data)
                db.add(db_opportunity)
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
        
        # Commit all opportunities
        db.commit()
        
        logger.info(f"CSV import completed: {imported_count} opportunities imported")
        
        return {
            "message": "CSV import completed",
            "imported_count": imported_count,
            "errors": errors if errors else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during CSV import: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error importing CSV"
        )


@router.get("/export-csv")
async def export_opportunities_csv(
    db: Session = Depends(get_db)
):
    """
    Export all opportunities to a CSV file.
    
    This endpoint creates a CSV file with all active opportunities
    for download or data analysis.
    """
    try:
        logger.info("CSV export request")
        
        # Get all active opportunities
        opportunities = db.query(Opportunity).filter(Opportunity.is_active == True).all()
        
        # Convert to DataFrame
        data = []
        for opp in opportunities:
            data.append({
                'id': opp.id,
                'title': opp.title,
                'description': opp.description,
                'company_organization': opp.company_organization,
                'opportunity_type': opp.opportunity_type.value,
                'category': opp.category.value,
                'location': opp.location,
                'is_remote': opp.is_remote,
                'is_hybrid': opp.is_hybrid,
                'min_gpa': opp.min_gpa,
                'required_majors': opp.required_majors,
                'required_skills': opp.required_skills,
                'min_graduation_year': opp.min_graduation_year,
                'max_graduation_year': opp.max_graduation_year,
                'salary_min': opp.salary_min,
                'salary_max': opp.salary_max,
                'is_paid': opp.is_paid,
                'benefits': opp.benefits,
                'application_deadline': opp.application_deadline,
                'application_url': opp.application_url,
                'contact_email': opp.contact_email,
                'contact_phone': opp.contact_phone,
                'tags': opp.tags,
                'created_at': opp.created_at,
                'views_count': opp.views_count,
                'application_count': opp.application_count
            })
        
        # Create DataFrame and CSV
        df = pd.DataFrame(data)
        csv_content = df.to_csv(index=False)
        
        logger.info(f"CSV export completed: {len(opportunities)} opportunities exported")
        
        # Return CSV file
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=opportunities.csv"}
        )
        
    except Exception as e:
        logger.error(f"Error during CSV export: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error exporting CSV"
        )
