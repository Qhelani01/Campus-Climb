# Frontend - Campus Climb

This directory contains the frontend application for the Campus Climb platform.

## Structure

```
frontend/
├── index.html              # Main HTML file
├── js/
│   └── app.js             # Main JavaScript application
├── templates/             # Legacy templates (not used in new structure)
├── static/               # Static assets
└── README.md             # This file
```

## Features

- **Modern Single Page Application**: Built with vanilla JavaScript
- **Responsive Design**: Mobile-first design with Tailwind CSS
- **API Integration**: Communicates with Flask backend via REST API
- **User Authentication**: Login/register modals with local storage
- **Real-time Data**: Dynamic loading of opportunities from API
- **Search & Filtering**: Advanced filtering capabilities
- **Interactive UI**: Modal dialogs and smooth transitions

## Technology Stack

- **HTML5**: Semantic markup
- **CSS3**: Tailwind CSS for styling
- **JavaScript (ES6+)**: Modern JavaScript with async/await
- **Fetch API**: HTTP requests to backend
- **Local Storage**: Client-side session management

## Key Components

### CampusClimbApp Class
Main application class that handles:
- API communication
- User authentication
- UI state management
- Event handling
- Data rendering

### API Endpoints Used
- `GET /api/opportunities` - Fetch all opportunities
- `GET /api/opportunities/types` - Get opportunity types
- `GET /api/opportunities/categories` - Get categories
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/profile` - Get user profile

### UI Sections
1. **Welcome Section**: Landing page with call-to-action buttons
2. **Login Modal**: User authentication form
3. **Register Modal**: User registration form
4. **Dashboard**: User dashboard with stats and recent opportunities
5. **Opportunities Section**: Full opportunities listing with filters

## Development

### Running the Frontend
1. Start the backend server: `python3 run.py`
2. Open `frontend/index.html` in a web browser
3. Or serve with a local server:
   ```bash
   cd frontend
   python3 -m http.server 3000
   ```

### API Configuration
The frontend is configured to connect to the backend at `http://localhost:8000/api`. 
Update the `apiBaseUrl` in `js/app.js` if needed.

### Browser Compatibility
- Modern browsers with ES6+ support
- Requires CORS to be enabled on the backend
- Local storage for session management

## Features in Detail

### Authentication
- Email/password login
- WVSU email validation
- Session persistence with localStorage
- Secure logout functionality

### Opportunities Management
- Real-time data loading
- Search functionality
- Type and category filtering
- Responsive grid layout
- Application link handling

### User Experience
- Modal dialogs for forms
- Toast notifications
- Loading states
- Error handling
- Responsive design

## Future Enhancements

- [ ] React/Vue.js migration
- [ ] Advanced filtering
- [ ] User favorites
- [ ] Notifications
- [ ] Offline support
- [ ] Progressive Web App features
