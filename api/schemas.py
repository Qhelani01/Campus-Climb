"""
Marshmallow schemas for request validation.
Provides consistent validation and error messages across all API endpoints.
"""
from marshmallow import Schema, fields, validate, ValidationError, validates
import re


class RegisterSchema(Schema):
    """Schema for user registration"""
    email = fields.Email(required=True, error_messages={'required': 'Email is required', 'invalid': 'Invalid email format'})
    password = fields.Str(required=True, validate=validate.Length(min=8), error_messages={'required': 'Password is required'})
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=50), error_messages={'required': 'First name is required'})
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=50), error_messages={'required': 'Last name is required'})
    
    @validates('password')
    def validate_password_strength(self, value):
        """Validate password meets complexity requirements"""
        if not re.search(r'[A-Z]', value):
            raise ValidationError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', value):
            raise ValidationError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', value):
            raise ValidationError('Password must contain at least one digit')
    
    @validates('email')
    def validate_wvsu_email(self, value):
        """Validate email is from WVSU domain (unless admin)"""
        if not value.lower().endswith('@wvstateu.edu'):
            raise ValidationError('Only WVSU email addresses (@wvstateu.edu) are allowed')


class LoginSchema(Schema):
    """Schema for user login"""
    email = fields.Email(required=True, error_messages={'required': 'Email is required', 'invalid': 'Invalid email format'})
    password = fields.Str(required=True, error_messages={'required': 'Password is required'})


class OpportunityCreateSchema(Schema):
    """Schema for creating an opportunity"""
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200), error_messages={'required': 'Title is required'})
    company = fields.Str(required=True, validate=validate.Length(min=1, max=100), error_messages={'required': 'Company is required'})
    location = fields.Str(required=True, validate=validate.Length(min=1, max=100), error_messages={'required': 'Location is required'})
    type = fields.Str(required=True, validate=validate.OneOf(['internship', 'job', 'workshop', 'conference', 'competition']), error_messages={'required': 'Type is required'})
    category = fields.Str(required=True, validate=validate.Length(min=1, max=50), error_messages={'required': 'Category is required'})
    description = fields.Str(required=True, validate=validate.Length(min=10), error_messages={'required': 'Description is required'})
    requirements = fields.Str(allow_none=True, missing='')
    salary = fields.Str(allow_none=True, validate=validate.Length(max=50), missing='')
    application_url = fields.URL(allow_none=True, error_messages={'invalid': 'Invalid URL format'}, missing=None)
    deadline = fields.Date(allow_none=True, missing=None)


class OpportunityUpdateSchema(Schema):
    """Schema for updating an opportunity"""
    title = fields.Str(validate=validate.Length(min=1, max=200))
    company = fields.Str(validate=validate.Length(min=1, max=100))
    location = fields.Str(validate=validate.Length(min=1, max=100))
    type = fields.Str(validate=validate.OneOf(['internship', 'job', 'workshop', 'conference', 'competition']))
    category = fields.Str(validate=validate.Length(min=1, max=50))
    description = fields.Str(validate=validate.Length(min=10))
    requirements = fields.Str(allow_none=True)
    salary = fields.Str(allow_none=True, validate=validate.Length(max=50))
    application_url = fields.URL(allow_none=True, error_messages={'invalid': 'Invalid URL format'})
    deadline = fields.Date(allow_none=True)
    is_deleted = fields.Bool(allow_none=True)


class UserProfileUpdateSchema(Schema):
    """Schema for updating user profile (AI assistant)"""
    resume_summary = fields.Str(allow_none=True, validate=validate.Length(max=5000))
    skills = fields.Str(allow_none=True, validate=validate.Length(max=1000))
    career_goals = fields.Str(allow_none=True, validate=validate.Length(max=2000))


class AdminPromoteSchema(Schema):
    """Schema for promoting user to admin"""
    email = fields.Email(required=True, error_messages={'required': 'Email is required', 'invalid': 'Invalid email format'})
    secret_key = fields.Str(required=True, error_messages={'required': 'Secret key is required'})


class SetupAdminSchema(Schema):
    """Schema for setting up admin user"""
    email = fields.Email(required=True, error_messages={'required': 'Email is required', 'invalid': 'Invalid email format'})
    password = fields.Str(required=True, validate=validate.Length(min=8), error_messages={'required': 'Password is required'})
    first_name = fields.Str(validate=validate.Length(min=1, max=50), missing='Admin')
    last_name = fields.Str(validate=validate.Length(min=1, max=50), missing='User')
    
    @validates('password')
    def validate_password_strength(self, value):
        """Validate password meets complexity requirements"""
        if not re.search(r'[A-Z]', value):
            raise ValidationError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', value):
            raise ValidationError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', value):
            raise ValidationError('Password must contain at least one digit')


class OpportunityQuerySchema(Schema):
    """Schema for opportunity query parameters"""
    type = fields.Str(validate=validate.Length(max=50))
    category = fields.Str(validate=validate.Length(max=50))
    search = fields.Str(validate=validate.Length(max=200))
    page = fields.Int(validate=validate.Range(min=1), missing=1)
    per_page = fields.Int(validate=validate.Range(min=1, max=100), missing=50)


class AIAdviceRequestSchema(Schema):
    """Schema for AI assistant advice requests"""
    opportunity_id = fields.Int(required=True, error_messages={'required': 'Opportunity ID is required'})
    request_type = fields.Str(required=True, validate=validate.OneOf(['resume_tips', 'cover_letter', 'interview_prep']), error_messages={'required': 'Request type is required'})
