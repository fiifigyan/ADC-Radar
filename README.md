# ADC-Radar

Africa Digital Consultancy Radar - An automated tool that scans, filters, and publishes weekly shortlists of individual consultancy and roster opportunities in Africa focused on data, digital transformation, and IT.

## Features

### Dark/Light Mode
- 🌓 **Theme Toggle**: Switch between dark and light modes with one click
- 💾 **Theme Persistence**: Your preference is saved and restored
- 🎨 **Consistent Colors**: Professional color scheme for both themes
  - **Light Mode**: Clean, professional appearance
  - **Dark Mode**: Reduces eye strain during extended use
- ⚡ **Smooth Transitions**: Elegant theme switching animations
- 📱 **Responsive**: Full support on all devices

### Core Features
- 🔍 Automated web scraping from multiple sources
- 🤖 AI-powered classification and summarization
- 📊 Real-time opportunity dashboard
- 📧 Email notifications for new opportunities
- 💾 Local and Notion database support
- 📅 Scheduled automated scans

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Quick Start

```bash
# Clone repository
git clone <repository-url>
cd ADC-Radar

# Backend setup
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate   # Mac/Linux
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
npm run dev  # Start development server
```

In another terminal:
```bash
# Start backend
cd backend
.venv\Scripts\Activate.ps1  # Windows
python src/main.py
```

Backend: http://localhost:5000
Frontend: http://localhost:5173

## Production Deployment

See [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) for comprehensive production setup and deployment guidelines.

### Docker Deployment
```bash
docker-compose up -d
```

## Project Structure

```
├── backend/
│   ├── src/
│   │   ├── main.py
│   │   ├── scrapers/         # Web scrapers
│   │   ├── ai_processor/     # AI classification
│   │   ├── database/         # DB handlers
│   │   └── scheduling/       # Task scheduling
│   ├── config/               # Configuration
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/           # App pages
│   │   ├── contexts/        # React contexts (includes ThemeContext)
│   │   ├── styles/          # CSS files
│   │   └── App.jsx
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml
└── README.md
```

## API Endpoints

### Opportunities
- `GET /api/opportunities` - Get all opportunities
- `GET /api/search?q=<query>` - Search opportunities
- `GET /api/opportunities/filter` - Filter opportunities
- `POST /api/opportunities` - Create new opportunity

### System
- `GET /health` - Health check

## Theme System

The application includes a professional dark/light theme system:

### Light Mode Colors
- Primary: `#8C98C6`
- Background: `#FFFFFF`
- Text: `#1D1F29`
- Accent: `#AEB3CB`

### Dark Mode Colors
- Primary: `#8C98C6`
- Background: `#1D1F29`
- Text: `#FFFFFF`
- Accent: `#333A55`

### Using the Theme
The theme automatically detects your system preference and saves your choice locally. Click the theme toggle button in the header to switch modes.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

## License

See LICENSE file for details

## Support

For issues or questions, please open an issue on GitHub or contact the development team.

