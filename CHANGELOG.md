# Changelog

## [1.0.0] - 2026-03-28

### Changed
- Removed "v2.0" badge from navigation header
- Updated all version numbers from 2.0.0 to 1.0.0
- Fixed dropdown/select styling for better visibility on all backgrounds
- Renamed README_NEW.md to README.md

### Fixed
- Select/dropdown option text now visible with dark background color
- Font visibility in dropdown menus fixed

### Removed (Redundant Files)
- `app.py` - Old Streamlit application (replaced by React frontend)
- `build_index.py` - Moved to ai-service/
- `requirements.txt` - Moved to ai-service/
- `UI_INTEGRATION.md` - Content integrated into new documentation
- `WRITEUP.md` - Replaced by comprehensive documentation
- `EXAMPLE_RUNS.md` - No longer relevant
- `interview_preparation.md` - Generic file
- `packages.txt` - Streamlit-specific
- `runtime.txt` - Streamlit-specific
- `.env.example` (root) - Each service has its own now

### Removed (Redundant Folders)
- `.streamlit/` - Streamlit configuration no longer needed
- `src/` - Moved to ai-service/
- `config/` - Moved to ai-service/
- `tests/` - Old test structure
- `evaluation_results/` - Old evaluation data

### Project Structure (Clean)
```
resolve-ai/
├── ai-service/          # FastAPI AI microservice
├── web-api/             # Express.js API gateway
├── client/              # React frontend
├── data/                # Policy documents
├── screenshots/         # Project screenshots
├── docker-compose.yml   # Local development
├── render.yaml          # Deployment config
├── setup.sh             # Setup script
├── README.md            # Main documentation
├── DEPLOYMENT.md        # Deployment guide
├── API_SPEC.md          # API documentation
├── SYSTEM_DESIGN.md     # Architecture documentation
└── PROJECT_SUMMARY.md   # Project overview
```

## Notes
- All services now use version 1.0.0
- Clean microservices architecture with no redundant files
- Each service has its own dependencies and configuration
- Improved UI/UX with fixed dropdown styling
