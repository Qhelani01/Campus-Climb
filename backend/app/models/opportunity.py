"""
Opportunity model for managing career opportunities, internships, conferences, and workshops.

This model represents the core data structure for the Campus Climb platform,
allowing students to discover various opportunities available to them.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
import enum


# Create the base class for all database models
Base = declarative_base()


class OpportunityType(str, enum.Enum):
    """
    Enumeration of opportunity types.
    
    Using an enum ensures data consistency and makes it easier to
    filter and categorize opportunities.
    """
    INTERNSHIP = "internship"
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONFERENCE = "conference"
    WORKSHOP = "workshop"
    COMPETITION = "competition"
    RESEARCH = "research"
    VOLUNTEER = "volunteer"
    OTHER = "other"


class OpportunityCategory(str, enum.Enum):
    """
    Enumeration of opportunity categories by field of study.
    
    This helps students find opportunities relevant to their major.
    """
    COMPUTER_SCIENCE = "computer_science"
    ENGINEERING = "engineering"
    BUSINESS = "business"
    HEALTH_SCIENCES = "health_sciences"
    ARTS_HUMANITIES = "arts_humanities"
    SOCIAL_SCIENCES = "social_sciences"
    NATURAL_SCIENCES = "natural_sciences"
    EDUCATION = "education"
    AGRICULTURE = "agriculture"
    OTHER = "other"


class Opportunity(Base):
    """
    SQLAlchemy model for the opportunities table.
    
    This represents the actual database table structure for storing
    opportunity information including metadata, requirements, and application details.
    """
    
    __tablename__ = "opportunities"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic information
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    company_organization = Column(String(200), nullable=False, index=True)
    
    # Categorization
    opportunity_type = Column(Enum(OpportunityType), nullable=False, index=True)
    category = Column(Enum(OpportunityCategory), nullable=False, index=True)
    
    # Location and logistics
    location = Column(String(200), nullable=False)
    is_remote = Column(Boolean, default=False)
    is_hybrid = Column(Boolean, default=False)
    
    # Requirements and eligibility
    min_gpa = Column(Float, nullable=True)
    required_majors = Column(Text, nullable=True)  # JSON string of majors
    required_skills = Column(Text, nullable=True)  # JSON string of skills
    min_graduation_year = Column(Integer, nullable=True)
    max_graduation_year = Column(Integer, nullable=True)
    
    # Compensation and benefits
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    is_paid = Column(Boolean, default=True)
    benefits = Column(Text, nullable=True)  # JSON string of benefits
    
    # Application details
    application_deadline = Column(DateTime(timezone=True), nullable=True)
    application_url = Column(String(500), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    
    # Status and visibility
    is_active = Column(Boolean, default=True, index=True)
    is_featured = Column(Boolean, default=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    posted_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Additional metadata
    tags = Column(Text, nullable=True)  # JSON string of tags
    application_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)


# Pydantic models for API requests/responses
class OpportunityBase(BaseModel):
    """Base opportunity model with common fields."""
    title: str
    description: str
    company_organization: str
    opportunity_type: OpportunityType
    category: OpportunityCategory
    location: str
    is_remote: bool = False
    is_hybrid: bool = False
    min_gpa: Optional[float] = None
    required_majors: Optional[List[str]] = None
    required_skills: Optional[List[str]] = None
    min_graduation_year: Optional[int] = None
    max_graduation_year: Optional[int] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    is_paid: bool = True
    benefits: Optional[List[str]] = None
    application_deadline: Optional[datetime] = None
    application_url: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    tags: Optional[List[str]] = None


class OpportunityCreate(OpportunityBase):
    """Model for creating new opportunities."""
    
    @validator('title')
    def validate_title_length(cls, v):
        """Ensure title is not too long for database storage."""
        if len(v) > 200:
            raise ValueError('Title must be 200 characters or less')
        return v
    
    @validator('description')
    def validate_description_length(cls, v):
        """Ensure description is not empty."""
        if not v.strip():
            raise ValueError('Description cannot be empty')
        return v
    
    @validator('salary_min', 'salary_max')
    def validate_salary_range(cls, v, values):
        """Ensure salary range makes sense."""
        if v is not None and v < 0:
            raise ValueError('Salary cannot be negative')
        if 'salary_min' in values and 'salary_max' in values:
            if values['salary_min'] and values['salary_max']:
                if values['salary_min'] > values['salary_max']:
                    raise ValueError('Minimum salary cannot be greater than maximum salary')
        return v


class OpportunityUpdate(BaseModel):
    """Model for updating opportunities."""
    title: Optional[str] = None
    description: Optional[str] = None
    company_organization: Optional[str] = None
    opportunity_type: Optional[OpportunityType] = None
    category: Optional[OpportunityCategory] = None
    location: Optional[str] = None
    is_remote: Optional[bool] = None
    is_hybrid: Optional[bool] = None
    min_gpa: Optional[float] = None
    required_majors: Optional[List[str]] = None
    required_skills: Optional[List[str]] = None
    min_graduation_year: Optional[int] = None
    max_graduation_year: Optional[int] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    is_paid: Optional[bool] = None
    benefits: Optional[List[str]] = None
    application_deadline: Optional[datetime] = None
    application_url: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None


class OpportunityResponse(OpportunityBase):
    """Model for API responses with opportunity data."""
    id: int
    is_active: bool
    is_featured: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    posted_date: datetime
    application_count: int
    views_count: int
    
    class Config:
        # Enable ORM mode for SQLAlchemy integration
        from_attributes = True


class OpportunityFilter(BaseModel):
    """Model for filtering opportunities in search queries."""
    opportunity_type: Optional[OpportunityType] = None
    category: Optional[OpportunityCategory] = None
    location: Optional[str] = None
    is_remote: Optional[bool] = None
    min_gpa: Optional[float] = None
    required_majors: Optional[List[str]] = None
    salary_min: Optional[float] = None
    is_paid: Optional[bool] = None
    is_active: Optional[bool] = True
    search_query: Optional[str] = None
    page: int = 1
    limit: int = 20
