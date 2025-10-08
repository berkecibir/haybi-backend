# Haybi Backend API

This is the backend API for the Haybi image editing application, built with FastAPI.

## Features

- Image editing using Fal.ai API
- Job tracking system
- Authentication with API key
- CORS support for web applications

## Requirements

- Python 3.8+
- FastAPI
- Uvicorn
- Other dependencies listed in [requirements.txt](requirements.txt)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd haybi-backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv haybi-env
   source haybi-env/bin/activate  # On Windows: haybi-env\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your configuration:
   ```bash
   cp .env.example .env
   ```
   Then edit the `.env` file to add your Fal.ai API key and other configuration.

## Running the Application

To run the application in development mode:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API Endpoints

### Authentication

All endpoints require authentication with an API key in the Authorization header:
```
Authorization: Bearer YOUR_API_KEY
```

### POST /edit-image/

Submit an image for editing.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Parameters:
  - `image`: The image file to edit
  - `prompt`: Text prompt describing the desired edit

**Response:**
```json
{
  "job_id": "uuid-string"
}
```

### GET /edit-image/{job_id}

Get the status of an image editing job.

**Request:**
- Method: GET
- Path Parameter: `job_id` - The ID of the job to check

**Response:**
```json
{
  "id": "job_id",
  "status": "completed|processing|failed",
  "prompt": "string",
  "original_path": "string",
  "result_url": "string"
}
```

## Error Codes

- `401`: Unauthorized - Invalid or missing API key
- `422`: Unprocessable Entity - Invalid request data
- `500`: Internal Server Error - Server-side error

## Deployment

The application can be deployed to any platform that supports Python applications. For Render deployment, see [README_DEPLOY_RENDER.md](README_DEPLOY_RENDER.md).

## Environment Variables

- `API_KEY`: Your Fal.ai API key (required)
- `DATABASE_URL`: Database connection URL (default: sqlite+aiosqlite:///./jobs.db)
- `ALLOWED_ORIGINS`: CORS allowed origins (default: *)

## Security

- Never commit your `.env` file to version control
- Use strong, unique API keys
- Rotate API keys regularly
- Use HTTPS in production

## License

This project is licensed under the MIT License.