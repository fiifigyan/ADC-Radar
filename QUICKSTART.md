# Quick Start Guide - ADC-Radar

## For Developers

### First Time Setup

```bash
# Clone the repository
git clone <repo-url>
cd ADC-Radar

# Backend
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1          # Windows PowerShell
source .venv/bin/activate           # Mac/Linux
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### Running Locally

**Terminal 1 - Backend:**
```bash
cd backend
.venv\Scripts\Activate.ps1  # or source .venv/bin/activate
python src/main.py
# Running on http://localhost:5000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# Running on http://localhost:5173
```

### Theme Features

The app has a built-in dark/light mode:
- Click the sun/moon icon in the header to toggle
- Your preference is automatically saved
- All colors adjust instantly

## For Production

### Using Docker

```bash
# Build and start
docker-compose up -d

# Frontend: http://localhost:3000
# Backend: http://localhost:5000

# Stop everything
docker-compose down
```

### Before Deploying

1. **Create `.env` file in backend:**
```
FLASK_ENV=production
OPENAI_API_KEY=your-key
NOTION_INTEGRATION_TOKEN=your-token
```

2. **Update API URL in frontend** (if needed)

3. **Review PRODUCTION_DEPLOYMENT.md** for full checklist

## Common Commands

### Frontend
```bash
npm run dev       # Start dev server
npm run build     # Build for production
npm run lint      # Check code quality
npm run preview   # Preview production build
```

### Backend
```bash
python src/main.py        # Start server
flask shell              # Python shell with app context
```

## Project Structure

```
ADC-Radar/
├── backend/              # Flask API
│   ├── src/
│   │   ├── main.py      # Entry point
│   │   ├── scrapers/    # Web scrapers
│   │   └── ai_processor/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/             # React + Vite
│   ├── src/
│   │   ├── contexts/    # Theme context here ✨
│   │   ├── components/
│   │   ├── pages/
│   │   └── styles/
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml
├── README.md
└── PRODUCTION_DEPLOYMENT.md
```

## Features

✨ **Theme System**
- Dark/Light mode toggle
- Persistent user preference
- Smooth transitions
- Professional colors

📊 **Core Features**
- AI-powered opportunity classification
- Automated web scraping
- Real-time dashboard
- Email notifications
- Notion integration

## Troubleshooting

### Backend won't start
```bash
# Check Python version (need 3.8+)
python --version

# Check if dependencies installed
pip list | grep flask

# Check port 5000 isn't in use
netstat -ano | findstr :5000
```

### Frontend won't start
```bash
# Check Node version (need 16+)
node --version

# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules
npm install
```

### Theme not working
- Check browser console for errors
- Clear browser cache
- Verify localStorage is enabled
- Try incognito/private mode

## API Quick Reference

```bash
# Get all opportunities
curl http://localhost:5000/api/opportunities

# Search opportunities
curl "http://localhost:5000/api/search?q=data"

# Health check
curl http://localhost:5000/health
```

## Documentation Index

- **[README.md](README.md)** - Project overview
- **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** - Running both servers
- **[PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)** - Production setup
- **[THEME_DOCUMENTATION.md](THEME_DOCUMENTATION.md)** - Theme system details
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - What was done

## Next Steps

1. ✅ Setup complete
2. 🧪 Test theme toggle
3. 🐳 Try docker-compose setup
4. 📖 Read PRODUCTION_DEPLOYMENT.md
5. 🚀 Deploy to production

## Support

- Check error messages in browser console
- Review backend logs: `docker logs adc-radar-backend`
- See PRODUCTION_DEPLOYMENT.md troubleshooting section
- Check individual documentation files

---

**You're all set! The project is production-ready with a professional dark/light mode system.** 🚀
