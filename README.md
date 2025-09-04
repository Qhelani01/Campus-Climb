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
├── backend/                 # Flask API backend
│   ├── app/
│   │   └── app.py         # Main Flask API application
│   ├── data/
│   │   └── opportunities.csv # Sample opportunities data
│   ├── campus_climb.db    # SQLite database
│   ├── requirements.txt    # Python dependencies
│   └── README.md          # Backend documentation
├── frontend/               # Frontend application
│   ├── index.html         # Main HTML file
│   ├── js/
│   │   └── app.js        # Main JavaScript application
│   ├── templates/        # Legacy templates (not used)
│   ├── static/           # Static assets
│   └── README.md         # Frontend documentation
├── run.py                 # Backend startup script
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

2. **Install backend dependencies**
   ```bash
   python3 -m pip install -r backend/requirements.txt
   ```

3. **Start the backend server**
   ```bash
   python3 run.py
   ```

4. **Access the frontend**
   - Open `frontend/index.html` in your web browser
   - Or serve with a local server:
     ```bash
     cd frontend
     python3 -m http.server 3000
     ```
   - Then visit: `http://localhost:3000`

5. **Register and login**
   - Use a WVSU email address (@wvstateu.edu)
   - Start exploring opportunities!

## 📊 Data Management

### Adding Opportunities
1. Edit `backend/data/opportunities.csv` with new opportunities
2. Restart the backend or call `/api/admin/load-csv` to reload data

### CSV Format
```csv
title,company,location,type,category,description,requirements,salary,deadline,application_url
"Job Title","Company Name","Location","type","category","Description","Requirements","Salary","YYYY-MM-DD","URL"
```

## 🔐 Authentication

- Only WVSU students with `@wvstateu.edu` email addresses can register
- Passwords are securely hashed using bcrypt
- Session management with localStorage on frontend

## 🌐 API Endpoints

### Opportunities
- `GET /api/opportunities` - Get all opportunities with optional filtering
- `GET /api/opportunities/<id>` - Get specific opportunity
- `GET /api/opportunities/types` - Get all opportunity types
- `GET /api/opportunities/categories` - Get all categories

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile

### Admin
- `POST /api/admin/load-csv` - Reload data from CSV file
- `GET /api/health` - Health check endpoint

## 🎯 Learning Objectives

This project demonstrates:
- **Full-Stack Development**: Separate frontend and backend architecture
- **API Design**: RESTful API endpoints with proper HTTP methods
- **Database Design**: SQLAlchemy ORM and database relationships
- **Authentication**: User registration, login, and session management
- **Frontend Development**: Modern JavaScript with async/await
- **Data Processing**: CSV import/export functionality
- **Responsive Design**: Mobile-first web design
- **Project Structure**: Organized code architecture

## 🔧 Development

### Running the Backend
```bash
python3 run.py
```
Backend will be available at: `http://localhost:8000`

### Running the Frontend
```bash
cd frontend
python3 -m http.server 3000
```
Frontend will be available at: `http://localhost:3000`

### Database
- SQLite database file: `backend/campus_climb.db`
- Automatically created on first run
- Data loaded from CSV file

### Adding New Features
1. **Backend**: Add routes in `backend/app/app.py`
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
