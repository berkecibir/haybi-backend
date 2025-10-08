# Haybi Backend

This is the backend service for the Haybi application, built with FastAPI.

## Features
- Image editing using Fal.ai API
- Job queue management
- RESTful API endpoints
- CORS support for web applications

## Recent Fixes
- Fixed CORS issues and authentication errors
- Enhanced CORS configuration
- Updated Firebase proxy rules
- Improved authentication handling

## Deployment
The application is automatically deployed to Render when changes are pushed to the main branch.

## API Documentation
Once deployed, visit `/docs` for interactive API documentation.

## Environment Variables
- `API_KEY`: Backend API key for authentication (optional but recommended)
- `FALAI_API_KEY`: Required for image processing
- `DATABASE_URL`: Database connection string
- `ALLOWED_ORIGINS`: CORS configuration (use "*" for development)

## Testing
Run the test suite with:
```bash
python test_cors_and_auth_fix.py
```
