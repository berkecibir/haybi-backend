# Render.com Deployment Fix

## Issue
Your Flutter application is getting a 500 error with the message `{"detail":"API key not configured on server"}` when trying to connect to the backend at `https://haybi-backend.onrender.com/edit-image/`. This indicates that the Render.com deployment doesn't have the required environment variables configured.

## Solution

### Configure Environment Variables on Render.com

1. Go to your Render dashboard (https://dashboard.render.com)
2. Navigate to your haybi-backend service
3. Click on "Environment Variables" in the sidebar
4. Add the following environment variables:

```
API_KEY=your_actual_api_key_here
BASE_URL=https://haybi-backend.onrender.com
FALAI_API_KEY=your_falai_api_key_here
DATABASE_URL=sqlite+aiosqlite:///./jobs.db
ALLOWED_ORIGINS=*
```

5. Click "Save Changes"
6. Redeploy your service by clicking "Manual Deploy" -> "Clear build cache & deploy"

### Important Notes

1. **API_KEY**: This is the specific API key you provided that should be used for authentication
2. **FALAI_API_KEY**: If you're not using the Fal.ai service, you can leave this as is or remove it
3. **BASE_URL**: This should match your Render.com deployment URL
4. **DATABASE_URL**: For production, consider using a PostgreSQL database instead of SQLite
5. **ALLOWED_ORIGINS**: For production, specify exact origins instead of using "*"

### Verification

After redeploying, you can verify that the service is working by:

1. Visiting the health check endpoint: `https://haybi-backend.onrender.com/health`
2. This should return `{"status": "healthy"}`

### Additional Troubleshooting

If you continue to experience issues:

1. Check the Render logs for more detailed error messages
2. Ensure that your start command is set to: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Verify that all required dependencies are listed in requirements.txt

## Flutter Application Configuration

Make sure your Flutter application is configured to use the correct API key:

1. Ensure your Flutter app is loading the API key from environment variables correctly
2. The API key should match the one you set in Render.com
3. The base URL should be: `https://haybi-backend.onrender.com`

## Security Notes

- Never commit actual API keys to version control
- The .env file should be in .gitignore to prevent accidental exposure
- Rotate API keys regularly for security