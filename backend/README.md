# Campus Climb Backend

FastAPI backend for the Campus Climb WVSU Opportunities Platform.

## 🚀 Features

- **User Authentication**: JWT-based authentication with WVSU email validation
- **Opportunity Management**: CRUD operations for career opportunities
- **CSV Import/Export**: Bulk data management capabilities
- **Advanced Filtering**: Search and filter opportunities by various criteria
- **Automatic API Documentation**: Swagger UI and ReDoc
- **Database ORM**: SQLAlchemy with SQLite (development) / PostgreSQL (production)

## 🏗️ Architecture

```
backend/
├── app/
│   ├── api/           # API endpoints and routers
│   ├── core/          # Configuration and database setup
│   ├── models/        # SQLAlchemy models and Pydantic schemas
│   ├── services/      # Business logic layer
│   └── main.py        # FastAPI application entry point
├── data/              # CSV data files
└── requirements.txt   # Python dependencies
```

## 🛠️ Technology Stack

- **FastAPI**: Modern, fast Python web framework
- **SQLAlchemy**: Database ORM and migration management
- **Pydantic**: Data validation and serialization
- **JWT**: JSON Web Token authentication
- **bcrypt**: Secure password hashing
- **Pandas**: CSV data processing
- **SQLite**: Development database (easily switchable to PostgreSQL)

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)
- Git

## 🚀 Quick Start

### 1. Clone and Navigate

```bash
cd backend
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or run directly
python -m app.main
```

### 5. Access the Application

- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Security
SECRET_KEY=your-super-secret-key-change-in-production
DEBUG=true

# Database
DATABASE_URL=sqlite:///./campus_climb.db

# JWT Settings
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Default Settings

- **Database**: SQLite (development)
- **Port**: 8000
- **Host**: 0.0.0.0 (all interfaces)
- **CORS**: Enabled for frontend communication

## 🗄️ Database

### Initial Setup

The database is automatically created when you first run the application. Tables are created based on the SQLAlchemy models.

### Database Schema

- **users**: User accounts and authentication
- **opportunities**: Career opportunities and internships

### Sample Data

A sample CSV file is provided in `data/sample_opportunities.csv` with 10 sample opportunities.

## 📚 API Endpoints

### Authentication

- `POST /api/v1/register` - User registration
- `POST /api/v1/login` - User login
- `GET /api/v1/me` - Get current user profile
- `PUT /api/v1/me` - Update user profile
- `POST /api/v1/logout` - User logout

### Opportunities

- `GET /api/v1/` - List opportunities with filtering
- `POST /api/v1/` - Create new opportunity
- `GET /api/v1/{id}` - Get specific opportunity
- `PUT /api/v1/{id}` - Update opportunity
- `DELETE /api/v1/{id}` - Delete opportunity
- `POST /api/v1/import-csv` - Import opportunities from CSV
- `GET /api/v1/export-csv` - Export opportunities to CSV

### Public Endpoints

- `GET /` - Application information
- `GET /health` - Health check
- `GET /docs` - API documentation (Swagger UI)

## 🧪 Testing

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py
```

### Test Structure

```
tests/
├── test_auth.py          # Authentication tests
├── test_opportunities.py # Opportunity management tests
├── test_models.py        # Model validation tests
└── conftest.py           # Test configuration and fixtures
```

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt with automatic salt generation
- **Email Validation**: WVSU domain restriction
- **Input Validation**: Pydantic schema validation
- **CORS Protection**: Configurable cross-origin requests
- **Rate Limiting**: Built-in FastAPI rate limiting (configurable)

## 📊 Data Management

### CSV Import

The system supports bulk import of opportunities from CSV files. Required columns:

- `title` - Opportunity title
- `description` - Detailed description
- `company_organization` - Company or organization name
- `opportunity_type` - Type (internship, full_time, etc.)
- `category` - Field of study category
- `location` - Geographic location

### CSV Export

Export all opportunities to CSV for data analysis or backup purposes.

## 🚀 Deployment

### Production Considerations

1. **Database**: Switch to PostgreSQL for production
2. **Environment Variables**: Set proper SECRET_KEY and DEBUG=false
3. **CORS**: Configure allowed origins for production domain
4. **HTTPS**: Enable SSL/TLS encryption
5. **Logging**: Configure production logging levels
6. **Monitoring**: Add health checks and monitoring

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure SQLite file is writable
   - Check database URL in configuration

2. **Import Errors**
   - Verify CSV format and required columns
   - Check file encoding (UTF-8 recommended)

3. **Authentication Issues**
   - Verify JWT token format
   - Check token expiration
   - Ensure proper Authorization header

4. **CORS Errors**
   - Verify frontend URL is in allowed_origins
   - Check CORS middleware configuration

### Debug Mode

Enable debug mode by setting `DEBUG=true` in your `.env` file. This will:

- Show detailed error messages
- Enable SQL query logging
- Provide additional debugging information

## 📈 Performance

### Optimization Tips

1. **Database Indexing**: Proper indexes on frequently queried fields
2. **Pagination**: Use skip/limit for large datasets
3. **Caching**: Implement Redis caching for frequently accessed data
4. **Async Operations**: Leverage FastAPI's async capabilities
5. **Connection Pooling**: Configure database connection pooling

## 🤝 Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Use meaningful commit messages

## 📄 License

This project is part of the Campus Climb WVSU Opportunities Platform.

## 🆘 Support

For issues and questions:

1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check application logs
4. Create an issue in the project repository

---

**Happy Coding! 🚀**
