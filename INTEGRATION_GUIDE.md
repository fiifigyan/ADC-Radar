# Frontend-Backend Integration Guide

This guide explains how to run the ADC-Radar application with both the backend (Flask) and frontend (React) servers working together.

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

## Installation & Setup

### 1. Backend Setup

Navigate to the backend directory:
```bash
cd backend
```

Create and activate virtual environment:
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1  # On Windows PowerShell
# or
source .venv/bin/activate   # On Mac/Linux
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Frontend Setup

Navigate to the frontend directory:
```bash
cd frontend
```

Install dependencies:
```bash
npm install
```

## Running the Application

### Option 1: Run Both in Separate Terminals

**Terminal 1 - Backend (Flask API):**
```bash
cd backend
.venv\Scripts\Activate.ps1
python src/main.py
```
Backend will be available at: `http://localhost:5000`

**Terminal 2 - Frontend (React Dev Server):**
```bash
cd frontend
npm run dev
```
Frontend will be available at: `http://localhost:5173` (or similar)

### Option 2: Background Execution

**Start Backend (Windows PowerShell):**
```bash
cd backend
.venv\Scripts\Activate.ps1
python src/main.py
```

**Start Frontend (in another PowerShell):**
```bash
cd frontend
npm run dev
```

## API Endpoints

The backend provides the following REST API endpoints:

### GET Endpoints

- `GET /api/opportunities` - Get all opportunities
- `GET /api/opportunities/<id>` - Get a specific opportunity by ID
- `GET /api/search?q=<query>` - Search opportunities
- `GET /api/opportunities/filter?priority=High&source=Devex` - Filter opportunities
- `GET /health` - Health check

### POST Endpoints

- `POST /api/opportunities` - Create a new opportunity
  - Request body:
    ```json
    {
      "title": "Job Title",
      "organization": "Company Name",
      "description": "Job Description",
      "url": "https://example.com/job",
      "priority": "High",
      "source_platform": "Devex"
    }
    ```

## Frontend Features

### Dashboard Page (`/`)
- Displays all opportunities from the backend
- Real-time search functionality
- Priority and source filtering
- Direct links to job postings

### Submit Page (`/submit`)
- Form to submit new opportunities
- Data is sent directly to the backend API
- Includes validations and user feedback

### Stats Page (`/stats`)
- Displays statistics about opportunities (coming soon)

### About Page (`/about`)
- Information about the application

## Troubleshooting

### Backend Not Starting
- Ensure Python virtual environment is activated
- Check that port 5000 is not in use: `netstat -ano | findstr :5000`
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Frontend Not Connecting to Backend
- Ensure backend is running on `http://localhost:5000`
- Check browser console for CORS errors
- Verify CORS is enabled in Flask (`flask-cors` should be installed)

### CORS Errors
- Make sure `flask-cors` is installed: `pip install flask-cors`
- Backend CORS is configured to allow all origins in development

### Port Already in Use
- Backend (port 5000): Kill process on that port or change port in `backend/src/main.py`
- Frontend (port 5173): Vite will automatically use next available port

## Development Workflow

1. Make changes to backend files
2. Backend will auto-reload (Flask debug mode enabled)
3. Make changes to frontend files
4. Frontend will auto-reload (Vite dev server)
5. Test API endpoints in browser or API client (Postman, etc.)

## Building for Production

### Build Frontend
```bash
cd frontend
npm run build
```
This creates a `dist` folder with production-ready files.

### Prepare Backend
```bash
cd backend
# Ensure all dependencies are installed
pip install -r requirements.txt
```

## Environment Variables

Backend uses `.env` file for configuration:
- `OPENAI_API_KEY` - For AI processing features
- `NOTION_API_KEY` - For Notion database integration
- Other settings as needed

Frontend uses `.env` (if needed):
- Can be added in `frontend/` directory for API endpoints

## Data Flow

1. User interacts with React frontend
2. Frontend sends requests to Flask backend API
3. Backend processes requests and queries/updates database
4. Backend returns JSON responses
5. Frontend displays data to user

## Database

The application uses a local JSON database located at `backend/data/opportunities.json`. This is created automatically on first run.

## Next Steps

1. Ensure the Notion integration works (configure API key in `.env`)
2. Test the scraper functionality
3. Implement AI classification and summarization features
4. Deploy to production environment

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review backend logs in terminal
3. Check frontend browser console logs
4. Verify API endpoints using an API client like Postman
