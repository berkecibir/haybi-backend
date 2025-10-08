# Haybi Backend - AI Image Editing API

This is the backend service for the Haybi AI Image Editing application. It provides a REST API for processing images using the fal.ai API.

## Features

- Image editing using fal.ai's Qwen Image Edit Plus LoRA model
- Asynchronous job processing with status tracking
- RESTful API with proper error handling
- Database persistence for job history
- CORS support for web frontend integration

## API Endpoints

### Direct Image Editing
- `POST /edit-image/` - Direct image editing (synchronous)
  - Request body: JSON with `prompt` and `image_base64`

### Job-based Image Editing
- `POST /api/jobs` - Create a new image editing job (asynchronous)
  - Form data: `prompt` (text) and `image` (file)
  - Response: JSON with `job_id`
- `GET /api/jobs/{job_id}` - Get the status and result of a job
- `GET /api/jobs` - List all jobs

### Utility Endpoints
- `GET /` - API root with endpoint information
- `GET /health` - Health check endpoint
- `GET /api/info` - Detailed API information

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv haybi-env
   source haybi-env/bin/activate  # On Windows: haybi-env\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file based on `.env.example` and fill in your values:
   ```bash
   cp .env.example .env
   ```
5. Set your fal.ai API key in the `.env` file

## Running the Application

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Deployment

The application is configured for deployment on Render.com. See `README_DEPLOY_RENDER.md` for detailed deployment instructions.

## Environment Variables

- `FALAI_API_KEY` - Your fal.ai API key
- `DATABASE_URL` - Database connection URL (default: SQLite)
- `ALLOWED_ORIGINS` - Comma-separated list of allowed CORS origins

## Database

The application uses SQLite for development and can be configured to use PostgreSQL for production deployments.

## Logging

The application uses Python's built-in logging module. Log levels can be configured through the logging configuration.