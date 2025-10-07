# Deployment Fixes for CORS Issues

## Problem
The Flutter web app was unable to communicate with the backend due to CORS restrictions:
```
Exception: Job creation from bytes failed: ClientException: Failed to fetch, uri=https://haybi-backend.onrender.com/api/jobs
```

## Root Causes
1. Incorrect CORS configuration in the backend
2. Environment variables not properly set in Render deployment
3. Missing CORS headers in responses

## Fixes Applied

### 1. Improved CORS Configuration (app/main.py)
- Enhanced CORS middleware to properly handle credentials and expose headers
- Added better parsing of ALLOWED_ORIGINS environment variable
- Set `allow_credentials=True` and `expose_headers=["*"]`

### 2. Updated Environment Variables
Created `.env.example` with proper documentation for:
- FALAI_API_KEY
- DATABASE_URL
- ALLOWED_ORIGINS

### 3. Enhanced README Documentation
Updated `README_DEPLOY_RENDER.md` with:
- Clear instructions for CORS configuration
- Production vs development settings for ALLOWED_ORIGINS

## Render Deployment Update Instructions

1. Go to your Render dashboard
2. Navigate to your haybi-backend service
3. Go to "Environment Variables" section
4. Ensure these variables are set:
   ```
   FALAI_API_KEY=your_actual_falai_api_key
   DATABASE_URL=your_database_url  # or keep sqlite for simple deployment
   ALLOWED_ORIGINS=*  # For development, or specify exact origins for production
   ```

5. If you're using a specific Flutter web app URL, set ALLOWED_ORIGINS to that exact URL:
   ```
   ALLOWED_ORIGINS=https://your-flutter-app.onrender.com
   ```

## Testing the Fix

1. After deployment, test CORS with a preflight request:
   ```bash
   curl -H "Origin: https://your-flutter-app.onrender.com" \
        -H "Access-Control-Request-Method: POST" \
        -H "Access-Control-Request-Headers: Content-Type" \
        -X OPTIONS \
        https://haybi-backend.onrender.com/api/jobs
   ```

2. The response should include:
   ```
   Access-Control-Allow-Origin: https://your-flutter-app.onrender.com
   Access-Control-Allow-Methods: POST
   Access-Control-Allow-Headers: Content-Type
   ```

## Common Issues and Solutions

### Issue: CORS error persists
**Solution**: Check that ALLOWED_ORIGINS in Render matches your Flutter app's exact origin (including protocol and port)

### Issue: Backend not responding
**Solution**: Verify the Start Command in Render:
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Issue: 500 Internal Server Error
**Solution**: Check the Render logs for specific error messages and ensure all environment variables are correctly set

## Verification Steps

1. After deployment, visit your Render service URL
2. Check that the API endpoints are accessible
3. Test with the provided test scripts
4. Verify that CORS headers are present in responses

This should resolve the "Failed to fetch" error and allow your Flutter web app to communicate with the backend successfully.