# 🏔️ Campus Climb - WVSU Opportunities Platform

A modern web application for managing and displaying career opportunities, internships, conferences, workshops, and competitions for WVSU students.

## ✨ Features

- **User Authentication**: WVSU email-only registration and secure login
- **Opportunity Management**: Browse and search through various opportunities
- **Responsive Design**: Mobile-first design that works on all devices
- **Real-time Data**: CSV-based data management with API endpoints
- **Modern UI**: Clean, professional interface with Tailwind CSS
- **Search & Filter**: Find opportunities by type, category, and keywords
- **API-First Architecture**: Separate frontend and backend for scalability

## 🛠️ Technology Stack

### Backend
- **Flask**: Lightweight Python web framework
- **SQLAlchemy**: Database ORM for data management
- **SQLite**: Simple database for development
- **Werkzeug**: Password hashing and security
- **Flask-CORS**: Cross-origin resource sharing

### Frontend
- **HTML5**: Semantic markup
- **Tailwind CSS**: Modern utility-first CSS framework
- **JavaScript (ES6+)**: Modern JavaScript with async/await
- **Fetch API**: HTTP requests to backend
- **Local Storage**: Client-side session management

## 📁 Project Structure

```
Campus Climb/
├── api/                    # Flask API (Vercel serverless)
│   └── index.py          # Main Flask API application
├── backend/                # Data storage
│   └── data/
│       └── opportunities.csv # Opportunities data
├── frontend/               # Frontend application
│   ├── index.html         # Main HTML file
│   ├── Campus Climb LOGO.png # Logo
│   └── js/
│       ├── app.js         # Main JavaScript application
│       └── config.js      # Configuration
├── requirements.txt        # Python dependencies
├── vercel.json            # Vercel deployment config
├── README.md              # This file
└── .gitignore            # Git ignore rules
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Modern web browser
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Campus Climb
   ```

2. **Install dependencies**
   ```bash
   python3 -m pip install -r requirements.txt
   ```

3. **Deploy to Vercel**
   ```bash
   # The app is automatically deployed to Vercel
   # Visit: https://campus-climb.vercel.app
   ```

4. **Local development**
   ```bash
   # For local testing, you can run:
   cd api
   python3 index.py
   ```

5. **Register and login**
   - Use a WVSU email address (@wvstateu.edu)
   - Start exploring opportunities!

## 📊 Data Management

### Adding Opportunities
1. Edit `backend/data/opportunities.csv` with new opportunities
2. Commit and push to GitHub to trigger Vercel redeploy

### CSV Format
```csv
title,company,location,type,category,description,requirements,salary,deadline,application_url
"Job Title","Company Name","Location","type","category","Description","Requirements","Salary","YYYY-MM-DD","URL"
```

## 🔐 Authentication

- Only WVSU students with `@wvstateu.edu` email addresses can register
- Passwords are securely hashed using Werkzeug's password hashing
- Session management with Flask sessions and localStorage fallback for serverless environments
- Supports both cookie-based sessions and email parameter fallback for Vercel serverless functions

## 🌐 API Endpoints

### Opportunities
- `GET /api/opportunities` - Get all opportunities with optional filtering
- `GET /api/opportunities/<id>` - Get specific opportunity
- `GET /api/opportunities/types` - Get all opportunity types
- `GET /api/opportunities/categories` - Get all categories

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user profile (supports session or email parameter)
- `POST /api/auth/logout` - User logout

### Health
- `GET /api/health` - Health check endpoint

## 🎯 Learning Objectives

This project demonstrates:
- **Full-Stack Development**: Separate frontend and backend architecture
- **API Design**: RESTful API endpoints with proper HTTP methods
- **Database Design**: Supabase PostgreSQL with SQLAlchemy ORM
- **Authentication**: User registration, login, and session management
- **Deployment**: Vercel serverless functions
- **Frontend Development**: Modern JavaScript with async/await
- **Data Processing**: CSV import/export functionality
- **Responsive Design**: Mobile-first web design
- **Project Structure**: Organized code architecture

## 🔧 Development

### Local Development
```bash
# Run the API locally
cd api
python3 index.py
```
API will be available at: `http://localhost:5000`

### Database
- Supabase PostgreSQL database
- Environment variables: `DATABASE_URL` and `SECRET_KEY`
- Data loaded from CSV file

### Adding New Features
1. **Backend**: Add routes in `api/index.py`
2. **Frontend**: Update `frontend/js/app.js` and `frontend/index.html`
3. **Data**: Update CSV data as needed

## 🏗️ Architecture Benefits

### Separate Frontend/Backend
- ✅ **Scalability**: Can scale frontend and backend independently
- ✅ **Technology Flexibility**: Can use different frontend frameworks
- ✅ **API-First**: Backend can serve multiple clients
- ✅ **Modern Development**: Industry-standard architecture
- ✅ **Learning Value**: Experience with both frontend and backend

### API Communication
- **CORS Enabled**: Frontend can communicate with backend
- **JSON Responses**: All API endpoints return JSON
- **Error Handling**: Proper HTTP status codes and error messages
- **Authentication**: Secure user authentication flow

## 🚀 Future Enhancements

- [ ] React/Vue.js frontend migration
- [ ] Advanced search and filtering
- [ ] User favorites and bookmarks
- [ ] Admin panel for data management
- [ ] Email verification system
- [ ] Password reset functionality
- [ ] Opportunity application tracking
- [ ] Analytics dashboard
- [ ] Mobile app using React Native
- [ ] Real-time notifications

## 📝 License

This project is for educational purposes and learning web development concepts.

## 🤝 Contributing

This is a learning project. Feel free to experiment and improve the code!

---

**Built with ❤️ for WVSU students**
# Updated Thu Sep  4 12:38:19 EDT 2025
# Updated Thu Sep  4 12:59:37 EDT 2025
