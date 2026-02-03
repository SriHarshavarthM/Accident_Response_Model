# Accident Incident Responder System

An ML-based system for detecting road accidents from CCTV footage with automated police reporting and ambulance dispatch capabilities.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- (Optional) PostgreSQL for production

### One-Click Setup (Windows)

After cloning from GitHub, just double-click:

```
run.bat        # First time: installs everything + starts services
start.bat      # Quick start (after initial setup)
stop.bat       # Stop all services
install.bat    # Install dependencies only
```

### Manual Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Initialize database with demo data
python seed_data.py

# Start the server
python main.py
```

Backend runs at: http://localhost:8000
API Docs at: http://localhost:8000/docs

### ML Engine Setup

```bash
# Navigate to ML folder
cd ml

# Install dependencies (in same or separate venv)
pip install -r requirements.txt

# Run demo
python inference_pipeline.py --demo

# Process a video file
python inference_pipeline.py --video path/to/video.mp4 --camera-id 1
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at: http://localhost:3000

## 📁 Project Structure

```
HACKATHON(RMK)/
├── backend/                 # FastAPI Backend
│   ├── main.py             # Application entry
│   ├── models.py           # Database models
│   ├── schemas.py          # API schemas
│   ├── routers/            # API routes
│   │   ├── incidents.py    # Incident CRUD
│   │   ├── cameras.py      # Camera management
│   │   └── dispatch.py     # Police/Ambulance dispatch
│   └── services/           # Business logic
│       ├── report_generator.py
│       └── notification.py
├── ml/                      # ML Detection Engine
│   ├── detector.py         # YOLOv8 accident detector
│   ├── severity_scorer.py  # Severity calculation
│   ├── video_processor.py  # Video frame extraction
│   └── inference_pipeline.py
├── frontend/               # React Dashboard
│   └── src/
│       ├── pages/          # Dashboard, Analytics, etc.
│       ├── components/     # UI components
│       └── services/       # API & WebSocket
└── samples/                # Test videos
```

## 🎯 Features

### ML Detection
- YOLOv8-based vehicle detection
- Collision, rollover, pedestrian impact detection
- Configurable FPS sampling (5-10 FPS)
- Severity scoring (Low/Medium/High/Critical)

### Dashboard
- Real-time incident feed
- Color-coded severity indicators
- Interactive map with Leaflet
- Analytics with charts (Recharts)

### Dispatch System
- ✅ Verify Incident
- 📄 Send Police Report (email/API)
- 🚑 Dispatch Ambulance (with confirmation)
- ❌ Mark False Alarm

### Human-in-the-Loop
- Operator confirmation required for dispatch
- Incident verification workflow
- Status tracking: Detected → Verified → Reported → Dispatched → Closed

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/incidents/` | GET | List all incidents |
| `/api/v1/incidents/active` | GET | Get active incidents |
| `/api/v1/incidents/{id}/verify` | POST | Verify incident |
| `/api/v1/dispatch/send-police-report` | POST | Send police report |
| `/api/v1/dispatch/ambulance` | POST | Dispatch ambulance |

Full API docs: http://localhost:8000/docs

## 🇮🇳 India-Specific Notes

- **Legal**: System generates "Incident Intimation" reports, NOT official FIRs
- **Emergency Services**: Compatible with ERSS-112, 108 Ambulance APIs
- **Human Verification**: Mandatory operator confirmation before dispatch
- **Audit Trail**: All actions logged with timestamps

## 📊 Severity Scoring

| Factor | Weight |
|--------|--------|
| Pedestrian involved | +3.0 |
| Fire/smoke detected | +3.5 |
| Rollover | +2.5 |
| Multi-vehicle (3+) | +2.0 |
| High speed (>60 km/h) | +2.0 |

**Thresholds**: CRITICAL ≥6, HIGH ≥4, MEDIUM ≥2, LOW <2

## 🛠️ Tech Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL/SQLite
- **ML**: PyTorch, Ultralytics YOLOv8, OpenCV
- **Frontend**: React, Vite, Leaflet, Recharts
- **Real-time**: WebSockets

## 📜 License

MIT License

---

Built for Smart Cities, Highways, and Government Pilots 🚗
