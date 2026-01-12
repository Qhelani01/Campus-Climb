# 🏔️ Campus Climb - WVSU Opportunities Platform

A modern web application for managing and displaying career opportunities, internships, conferences, workshops, and competitions for WVSU students. Features automated opportunity fetching from multiple sources, intelligent deduplication, and a comprehensive admin panel.

## ✨ Features

### User Features
- **User Authentication**: WVSU email-only registration and secure login (admin users can use any email)
- **Opportunity Management**: Browse and search through various opportunities
- **Responsive Design**: Mobile-first design that works on all devices
- **Modern UI**: Clean, professional interface with Tailwind CSS
- **Search & Filter**: Find opportunities by type, category, and keywords
- **AI Assistant**: Get personalized application advice for opportunities

### Admin Features
- **Admin Panel**: Comprehensive dashboard for managing opportunities and users
- **Automated Fetching**: Automatically fetch opportunities from RSS feeds and APIs
- **Manual Fetching**: Trigger opportunity fetches on-demand
- **Opportunity Management**: Create, edit, delete, and restore opportunities
- **User Management**: View all users and promote users to admin
- **Fetch Logs**: View detailed logs of fetch operations
- **Fetcher Status**: Monitor configured fetchers and RSS feeds

### Automated Features
- **Multi-Source Fetching**: Automatically fetch from:
  - Reddit job boards (`/r/jobbit`, `/r/remotejs`, `/r/internships`, `/r/jobopenings`)
  - Stack Overflow Jobs (when accessible)
  - Custom RSS feeds
  - API-based sources (Jooble, Authentic Jobs, Meetup - when API keys are configured)
- **Smart Filtering**: Automatically filters out "For Hire" posts, only includes actual opportunities
- **Intelligent Deduplication**: Prevents duplicate opportunities using fuzzy matching
- **Connection Pool Management**: Optimized for serverless environments (Vercel)

## 🛠️ Technology Stack

### Backend
- **Flask**: Lightweight Python web framework
- **SQLAlchemy**: Database ORM for data management
- **Supabase PostgreSQL**: Production database with Row Level Security (RLS)
- **SQLite**: Local development database
- **Werkzeug**: Password hashing and security
- **Flask-CORS**: Cross-origin resource sharing
- **Flask-Session**: Session management
- **feedparser**: RSS feed parsing
- **requests**: HTTP client for API calls
- **BeautifulSoup4**: HTML parsing and cleaning

### Frontend
- **HTML5**: Semantic markup
- **Tailwind CSS**: Modern utility-first CSS framework
- **JavaScript (ES6+)**: Modern JavaScript with async/await
- **Fetch API**: HTTP requests to backend
- **Local Storage**: Client-side session management

### Infrastructure
- **Vercel**: Serverless deployment platform
- **Supabase**: PostgreSQL database hosting
- **GitHub**: Version control and CI/CD

## 📁 Project Structure

```
Campus Climb/
├── api/                          # Flask API (Vercel serverless)
│   ├── index.py                 # Main Flask API application
│   ├── scheduler.py             # Opportunity fetching scheduler
│   ├── deduplicator.py          # Deduplication logic
│   ├── fetcher_config.py       # Fetcher configuration
│   ├── opportunity_fetchers.py  # Base fetcher class
│   └── fetchers/                # Fetcher implementations
│       ├── rss_fetcher.py       # RSS feed fetcher
│       └── api_fetchers.py      # API-based fetchers
├── backend/                      # Data storage (legacy)
│   └── data/
├── frontend/                     # Frontend application
│   ├── index.html              # Main HTML file
│   ├── Campus Climb LOGO.png    # Logo
│   └── js/
│       ├── app.js              # Main JavaScript application
│       └── config.js           # Configuration
├── database/                     # Database setup scripts
│   ├── 01_complete_schema.sql  # Complete database schema
│   ├── 02_enable_rls.sql       # Row Level Security setup
│   └── README.md              # Database documentation
├── migrations/                   # Database migration scripts
├── requirements.txt             # Python dependencies
├── vercel.json                 # Vercel deployment config
└── README.md                   # This file
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Modern web browser
- pip (Python package manager)
- Supabase account (for production database)
- Vercel account (for deployment)

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

3. **Set up environment variables**
   
   Create a `.env` file or set environment variables in Vercel:
   ```bash
   # Database
   DATABASE_URL=postgresql://user:password@host:port/database
   
   # Security
   SECRET_KEY=your-secret-key-here
   ADMIN_SECRET_KEY=your-admin-secret-key-here
   SETUP_TOKEN=your-setup-token-here
   
   # Optional: API Keys for additional fetchers
   JOOBLE_API_KEY=your-jooble-api-key
   AUTHENTIC_JOBS_API_KEY=your-authentic-jobs-api-key
   MEETUP_API_KEY=your-meetup-api-key
   
   # Optional: Custom RSS feeds (comma-separated)
   RSS_FEEDS=https://example.com/feed1,https://example.com/feed2
   
   # Optional: Enabled fetchers (comma-separated)
   ENABLED_FETCHERS=stackoverflow_jobs_rss
   ```

4. **Set up database**
   
   See `database/README.md` for detailed instructions:
   - Run `01_complete_schema.sql` to create tables
   - Run `02_enable_rls.sql` to enable Row Level Security
   - Use Supabase Session Pooler connection string (not Direct connection)

5. **Deploy to Vercel**
   ```bash
   # Connect your GitHub repository to Vercel
   # Vercel will automatically deploy on push
   # Visit: https://campus-climb.vercel.app
   ```

6. **Set up admin user**
   
   Use the setup endpoint to create an admin user:
   ```bash
   curl -X POST https://your-app.vercel.app/api/setup/admin \
     -H "Content-Type: application/json" \
     -H "X-Setup-Token: your-setup-token" \
     -d '{"email": "admin@example.com", "password": "secure-password"}'
   ```

7. **Local development**
   ```bash
   # For local testing:
   cd api
   python3 index.py
   ```
   API will be available at: `http://localhost:5000`

## 🔐 Authentication

### User Authentication
- **Regular Users**: Must use `@wvstateu.edu` email addresses to register
- **Admin Users**: Can use any email address (set via admin panel or setup endpoint)
- **Password Security**: Passwords are securely hashed using Werkzeug's password hashing
- **Session Management**: 
  - Flask sessions with cookie-based storage
  - localStorage fallback for serverless environments
  - Email parameter fallback for Vercel serverless functions

### Admin Authentication
- Admin users have access to the admin panel
- Admin endpoints require authentication via `@admin_required` decorator
- Admin users can:
  - Fetch opportunities manually
  - Create, edit, delete opportunities
  - View and manage users
  - Promote users to admin

## 🌐 API Endpoints

### Opportunities
- `GET /api/opportunities` - Get all opportunities with optional filtering
- `GET /api/opportunities/<id>` - Get specific opportunity
- `GET /api/opportunities/types` - Get all opportunity types
- `GET /api/opportunities/categories` - Get all categories

### Authentication
- `POST /api/auth/register` - Register new user (WVSU email required for non-admins)
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user profile (supports session or email parameter)
- `POST /api/auth/logout` - User logout

### Admin Endpoints (Requires Admin Authentication)
- `POST /api/admin/fetch-opportunities` - Manually trigger opportunity fetch
- `GET /api/admin/opportunities` - Get all opportunities (including deleted)
- `POST /api/admin/opportunities` - Create new opportunity
- `PUT /api/admin/opportunities/<id>` - Update opportunity
- `DELETE /api/admin/opportunities/<id>` - Delete opportunity (soft delete)
- `POST /api/admin/opportunities/<id>/restore` - Restore deleted opportunity
- `GET /api/admin/users` - Get all users
- `POST /api/admin/promote` - Promote user to admin
- `GET /api/admin/dashboard` - Get admin dashboard data
- `GET /api/admin/fetch-logs` - Get fetch operation logs
- `GET /api/admin/fetchers/status` - Get fetcher configuration status

### Setup Endpoints
- `POST /api/setup/admin` - Create or update admin user (requires SETUP_TOKEN)

### Health
- `GET /api/health` - Health check endpoint

### Cron
- `GET /api/cron/fetch-opportunities` - Cron endpoint for scheduled fetching (optional CRON_SECRET)

## 🤖 Automated Opportunity Fetching

### How It Works
1. **Scheduler**: The `scheduler.py` module orchestrates fetching from all enabled sources
2. **Fetchers**: Multiple fetcher classes handle different sources:
   - `RSSFetcher`: Fetches from RSS/Atom feeds
   - `RedditJobsFetcher`: Specialized fetcher for Reddit job boards with filtering
   - `JoobleFetcher`: Fetches from Jooble API (requires API key)
   - `AuthenticJobsFetcher`: Fetches from Authentic Jobs API (requires API key)
   - `MeetupFetcher`: Fetches from Meetup API (requires API key)
3. **Deduplication**: The `deduplicator.py` module prevents duplicates using:
   - Exact matching by source + source_id
   - Fuzzy matching by title + company + type
4. **Filtering**: Reddit fetchers automatically filter out "For Hire" posts, only including actual opportunities

### Configuration
- **RSS Feeds**: Configured in `fetcher_config.py` or via `RSS_FEEDS` environment variable
- **Enabled Fetchers**: Configured via `ENABLED_FETCHERS` environment variable
- **Fetch Interval**: Set via `FETCH_INTERVAL_HOURS` environment variable (default: 24 hours)

### Default Sources
- Stack Overflow Jobs RSS feed
- Reddit `/r/jobbit` (job board)
- Reddit `/r/remotejs` (remote JavaScript jobs)
- Reddit `/r/jobopenings` (job openings)
- Reddit `/r/internships` (internship opportunities)

## 📊 Database

### Production (Supabase PostgreSQL)
- **Connection**: Use Supabase Session Pooler connection string
- **Row Level Security**: Enabled for data protection
- **Connection Pooling**: Optimized for serverless (pool_size=2, max_overflow=1)
- **Schema**: See `database/01_complete_schema.sql`

### Local Development (SQLite)
- Database file: `api/instance/campus_climb.db`
- Automatically created on first run
- No connection pooling needed

### Tables
- `users`: User accounts with authentication
- `opportunities`: Job/internship/workshop opportunities
- `user_profiles`: Extended user profile information

## 🔧 Development

### Local Development
```bash
# Run the API locally
cd api
python3 index.py
```

### Database Migrations
- See `database/` directory for schema setup
- See `migrations/` directory for migration scripts
- Run migrations in Supabase SQL Editor

### Adding New Features
1. **Backend**: Add routes in `api/index.py`
2. **Frontend**: Update `frontend/js/app.js` and `frontend/index.html`
3. **Fetchers**: Add new fetcher classes in `api/fetchers/`
4. **Database**: Update schema in `database/01_complete_schema.sql`

### Testing
```bash
# Test opportunity fetching
python3 test_fetch.py

# Test login
python3 test_login.py

# Check database
python3 check_db.py
```

## 🏗️ Architecture

### Serverless Architecture
- **Vercel Functions**: Each API route is a serverless function
- **Connection Pooling**: Optimized for serverless with immediate connection cleanup
- **Session Management**: Cookie-based with email parameter fallback
- **Error Handling**: Comprehensive error handling with JSON responses

### Database Connection Management
- **Connection Pool**: Limited to 2 connections per instance (Supabase Session Pooler)
- **Immediate Cleanup**: Connections released immediately after use
- **Retry Logic**: Exponential backoff for connection timeouts
- **Error Handling**: Graceful degradation on connection failures

### Deduplication Strategy
1. **Exact Match**: Check by source + source_id
2. **Fuzzy Match**: Check by title + company + type similarity
3. **Update Existing**: If duplicate found, update existing record
4. **Create New**: If no duplicate, create new opportunity

## 🚀 Deployment

### Vercel Deployment
1. Connect GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

### Environment Variables (Required)
- `DATABASE_URL`: Supabase Session Pooler connection string
- `SECRET_KEY`: Flask secret key for sessions
- `ADMIN_SECRET_KEY`: Secret key for admin operations
- `SETUP_TOKEN`: Token for admin setup endpoint

### Environment Variables (Optional)
- `JOOBLE_API_KEY`: Jooble API key
- `AUTHENTIC_JOBS_API_KEY`: Authentic Jobs API key
- `MEETUP_API_KEY`: Meetup API key
- `RSS_FEEDS`: Comma-separated list of custom RSS feeds
- `ENABLED_FETCHERS`: Comma-separated list of enabled fetchers
- `FETCH_INTERVAL_HOURS`: Hours between automatic fetches (default: 24)
- `CRON_SECRET`: Secret for cron endpoint authentication

## 🎯 Learning Objectives

This project demonstrates:
- **Full-Stack Development**: Separate frontend and backend architecture
- **API Design**: RESTful API endpoints with proper HTTP methods
- **Database Design**: Supabase PostgreSQL with SQLAlchemy ORM
- **Authentication**: User registration, login, and session management
- **Admin Panel**: Comprehensive admin interface for data management
- **Automated Fetching**: Multi-source data aggregation with deduplication
- **Serverless Deployment**: Vercel serverless functions
- **Connection Pooling**: Database connection management for serverless
- **Frontend Development**: Modern JavaScript with async/await
- **Responsive Design**: Mobile-first web design
- **Project Structure**: Organized code architecture

## 🐛 Troubleshooting

### Connection Pool Exhaustion
- **Symptom**: "QueuePool limit reached" errors
- **Solution**: Ensure `db.session.close()` is called after operations
- **Check**: Verify `DATABASE_URL` uses Session Pooler (not Direct connection)

### Opportunities Not Saving
- **Check**: Vercel function logs for deduplication errors
- **Verify**: Required fields (title, company, location, description) are present
- **Debug**: Check `deduplicator.py` logs for duplicate detection

### Admin Login Issues
- **Verify**: Admin user exists in database with `is_admin=true`
- **Check**: Password hash matches (use `/api/setup/admin` to reset)
- **Debug**: Check Vercel logs for authentication errors

### Fetching Not Working
- **Check**: RSS feeds are accessible (some may block bots)
- **Verify**: Fetcher configuration in `fetcher_config.py`
- **Debug**: Check `scheduler.py` logs for fetch errors

## 🚀 Future Enhancements

- [x] Admin panel for data management
- [x] Automated opportunity fetching
- [x] Intelligent deduplication
- [x] Multi-source aggregation
- [ ] React/Vue.js frontend migration
- [ ] Advanced search and filtering
- [ ] User favorites and bookmarks
- [ ] Email verification system
- [ ] Password reset functionality
- [ ] Opportunity application tracking
- [ ] Analytics dashboard
- [ ] Mobile app using React Native
- [ ] Real-time notifications
- [ ] Email notifications for new opportunities
- [ ] Opportunity recommendations based on user profile

## 📝 License

This project is for educational purposes and learning web development concepts.

## 🤝 Contributing

This is a learning project. Feel free to experiment and improve the code!

---

**Built with ❤️ for WVSU students**

*Last updated: January 2026*
