# Campus Climb - WVSU Opportunities Platform

A modern web application for managing and displaying career opportunities, internships, conferences, workshops, and competitions for WVSU students.

## 🚀 Features

- **CSV-based Data Management**: Simple CSV file for easy data entry and management
- **Modern Web Interface**: Responsive design with filtering and search capabilities
- **FastAPI Backend**: High-performance Python backend with automatic API documentation
- **Real-time Updates**: Instant data refresh when CSV file is modified
- **Mobile Responsive**: Works seamlessly on all devices
- **WVSU Authentication**: Secure login system for WVSU students only

## 🏗️ Project Structure

```
campus-climb/
├── backend/                 # FastAPI backend server
│   ├── app/                # Main application code
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Configuration and core utilities
│   │   ├── models/        # Data models and schemas
│   │   ├── services/      # Business logic
│   │   └── main.py        # FastAPI application entry point
│   ├── data/              # CSV data files
│   ├── requirements.txt    # Python dependencies
│   └── README.md          # Backend-specific documentation
├── frontend/               # React frontend application
│   ├── src/               # Source code
│   ├── public/            # Static assets
│   ├── package.json       # Node.js dependencies
│   └── README.md          # Frontend-specific documentation
├── docs/                  # Project documentation
└── README.md              # This file
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast Python web framework
- **Pydantic**: Data validation and serialization
- **SQLAlchemy**: Database ORM (we'll use SQLite for simplicity)
- **Python 3.8+**: Modern Python features

### Frontend
- **React 18**: Modern React with hooks
- **TypeScript**: Type safety and better developer experience
- **Tailwind CSS**: Utility-first CSS framework for rapid UI development
- **Vite**: Fast build tool and development server

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 📚 Learning Objectives

This project is designed to teach you:
1. **Full-stack development** with modern technologies
2. **API design** and RESTful principles
3. **Database design** and data modeling
4. **Authentication** and security best practices
5. **Responsive web design** and modern UI/UX
6. **Project structure** and code organization
7. **Testing** and deployment strategies

## 🎯 Why This Tech Stack?

- **FastAPI**: Industry-standard for modern Python APIs, great for learning async programming
- **React + TypeScript**: Most in-demand frontend skills for SWE roles
- **Tailwind CSS**: Rapid UI development, widely used in industry
- **CSV + SQLite**: Simple data management that's easy to understand and modify

## 🔮 Future Enhancements

- User profiles and preferences
- Email notifications for new opportunities
- Admin dashboard for data management
- Integration with WVSU student systems
- Mobile app using React Native
- Advanced search and filtering
- Analytics and reporting

---

**Built with ❤️ for WVSU students**
