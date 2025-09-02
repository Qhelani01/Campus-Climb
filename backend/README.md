# Backend - Campus Climb

This directory contains the backend Flask application for the Campus Climb platform.

## Structure

```
backend/
├── app/
│   └── app.py              # Main Flask application
├── data/
│   └── opportunities.csv   # Opportunities data
├── templates/              # HTML templates
├── static/                 # Static assets
├── campus_climb.db         # SQLite database
└── requirements.txt        # Python dependencies
```

## Features

- **Flask Web Framework**: Lightweight and flexible Python web framework
- **SQLAlchemy ORM**: Database management and relationships
- **User Authentication**: Secure login with password hashing
- **CSV Data Management**: Import opportunities from CSV files
- **RESTful API**: JSON endpoints for data access
- **Template Engine**: Jinja2 templates with Tailwind CSS

## Database Models

### User
- `id`: Primary key
- `email`: Unique WVSU email address
- `password_hash`: Securely hashed password
- `first_name`, `last_name`: User information
- `created_at`: Registration timestamp

### Opportunity
- `id`: Primary key
- `title`, `company`, `location`: Basic information
- `type`: internship, job, conference, workshop, competition
- `category`: technology, business, arts, etc.
- `description`, `requirements`: Detailed information
- `salary`, `deadline`, `application_url`: Additional details
- `created_at`: Creation timestamp

## API Endpoints

- `GET /api/opportunities` - Returns all opportunities as JSON
- `GET /admin/load-csv` - Reloads data from CSV file

## Routes

- `/` - Dashboard (requires authentication)
- `/login` - User login
- `/register` - User registration
- `/logout` - User logout
- `/opportunities` - Browse opportunities
- `/opportunity/<id>` - Opportunity details
- `/profile` - User profile

## Security

- WVSU email validation (@wvstateu.edu only)
- Password hashing with Werkzeug
- Session-based authentication
- CSRF protection (Flask built-in)

## Data Management

The application loads opportunities from `data/opportunities.csv` on startup. The CSV file should have the following columns:

- title, company, location, type, category
- description, requirements, salary, deadline, application_url

## Development

To run the backend:

```bash
# From the project root
python3 run.py

# Or directly from backend directory
cd backend
python3 -m flask run --app app.app
```

## Dependencies

See `requirements.txt` for the complete list of Python packages.
