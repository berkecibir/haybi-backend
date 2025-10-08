# 500 Error: API Key Not Configured - Solution

## Problem
The backend server is returning a 500 error with the message `{"detail":"API key not configured on server"}`. This indicates that the server is unable to find the required API key configuration.

## Root Cause Analysis
After investigating the code, I found two potential causes:

1. **Missing FALAI_API_KEY Environment Variable**: The application requires both `API_KEY` (for backend authentication) and `FALAI_API_KEY` (for the Fal.ai image processing service). While `API_KEY` is correctly set in the .env file, `FALAI_API_KEY` is missing.

2. **Render.com Environment Variables Not Set**: When deploying to Render.com, environment variables must be manually configured in the Render dashboard. Even if they are present in the .env file locally, they won't be automatically available on Render.

## Solution

### 1. Local Development Fix
I've updated both `.env` and `.env.example` files to include the missing `FALAI_API_KEY` variable:

```
# Backend API Key for authentication
API_KEY=9bf4695a-429e-4afb-af94-103dfd235993:new_secret_key

# Fal.ai API Key - Get this from https://www.fal.ai/dashboard
FALAI_API_KEY=your_falai_api_key_here
```

To fix the issue locally:
1. Open the `.env` file
2. Replace `your_falai_api_key_here` with your actual Fal.ai API key
3. Save the file
4. Restart the server

### 2. Render.com Deployment Fix
To fix the issue on Render.com, you need to configure the environment variables in the Render dashboard:

1. Go to your Render dashboard
2. Navigate to your haybi-backend service
3. Go to the "Environment Variables" section
4. Add the following environment variables:
   ```
   API_KEY=9bf4695a-429e-4afb-af94-103dfd235993:new_secret_key
   FALAI_API_KEY=your_actual_falai_api_key
   DATABASE_URL=sqlite+aiosqlite:///./jobs.db
   ALLOWED_ORIGINS=*
   ```
5. Replace `your_actual_falai_api_key` with your actual Fal.ai API key
6. Click "Save Changes"
7. Redeploy your service

### 3. Verification
After making these changes, you can verify that the service is working correctly by:

1. Visiting the health check endpoint: `https://your-render-url.onrender.com/health`
2. This should return `{"status": "healthy"}`

## Additional Notes

- Never commit actual API keys to version control. The `.env` file should be in `.gitignore` to prevent accidental exposure.
- For production deployments, consider using more secure methods of managing secrets.
- If you continue to experience issues, check the Render logs for more detailed error messages.