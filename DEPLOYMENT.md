# Campus Climb - Vercel Deployment Guide

## Overview
This guide will help you deploy the Campus Climb application to Vercel.

## Prerequisites
- Vercel account (free at vercel.com)
- GitHub repository with the project
- Vercel CLI (optional)

## Deployment Steps

### 1. Connect to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Sign up/login with your GitHub account
3. Click "New Project"
4. Import your GitHub repository: `Qhelani01/Campus-Climb`

### 2. Configure Project
- **Framework Preset**: Other
- **Root Directory**: `./` (root of project)
- **Build Command**: Leave empty (Vercel will auto-detect)
- **Output Directory**: Leave empty

### 3. Environment Variables (Optional)
For production, you might want to add:
- `FLASK_ENV=production`
- `DATABASE_URL` (if using external database)

### 4. Deploy
Click "Deploy" and wait for the build to complete.

## Project Structure for Vercel
```
/
├── api/
│   └── index.py          # Vercel serverless function entry point
├── backend/
│   └── app/
│       └── app.py        # Flask application
├── frontend/
│   ├── index.html       # Main user interface
│   ├── admin.html       # Admin panel
│   └── js/
│       ├── config.js     # Environment configuration
│       ├── app.js        # Main app logic
│       └── admin.js      # Admin panel logic
├── vercel.json          # Vercel configuration
└── requirements.txt     # Python dependencies
```

## How It Works
- **API Routes** (`/api/*`) → Serverless function (`api/index.py`)
- **Admin Panel** (`/admin`) → Static file (`frontend/admin.html`)
- **Main App** (`/`) → Static file (`frontend/index.html`)

## Post-Deployment
1. Your app will be available at: `https://your-project-name.vercel.app`
2. Admin panel: `https://your-project-name.vercel.app/admin`
3. API: `https://your-project-name.vercel.app/api/*`

## Troubleshooting
- If the API doesn't work, check the Vercel function logs
- If static files don't load, verify the `vercel.json` routes
- Database will be SQLite (local to each function instance)

## Local Development
The app still works locally with:
```bash
# Backend
python3 run.py

# Frontend
cd frontend && python3 server.py
```
