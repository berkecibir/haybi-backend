# Environment Setup Guide

This guide explains how to set up the required environment variables for the Haybi Backend API.

## Required Environment Variables

The application requires the following environment variables:

1. **API_KEY**: Your backend authentication API key
2. **FALAI_API_KEY**: Your FalAI API key for image processing (format: `fal_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)
3. **BASE_URL**: The base URL for your application (optional, defaults to https://haybi-backend.onrender.com)

### FalAI API Key Format

The FalAI API key should be in the format: `fal_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

If you're getting "Authentication is required to access this application" errors, make sure:
- Your API key starts with `fal_`
- The API key is not a placeholder value
- The API key has the correct permissions for the `qwen-image-edit-plus-lora` model

## Setup Methods

### Method 1: Using the Setup Script (Recommended)

Run the setup script to interactively configure your environment variables:

```bash
python setup_env.py
```

The script will:
- Prompt you for each required API key
- Create a `.env` file with the correct configuration
- Ensure your API keys are not committed to git

### Method 2: Manual Setup

Create a `.env` file in the project root with the following content:

```env
# API Key for backend authentication
API_KEY=your_actual_api_key_here

# FalAI API Key for image processing
FALAI_API_KEY=your_actual_falai_api_key_here

# Base URL for the application
BASE_URL=https://haybi-backend.onrender.com
```

Replace `your_actual_api_key_here` and `your_actual_falai_api_key_here` with your real API keys.

## Security Notes

- ✅ The `.env` file is already included in `.gitignore`
- ✅ Your API keys will NOT be committed to git
- ✅ Never share your API keys publicly
- ✅ Use different API keys for development and production

## Verification

After setting up your environment variables, you can verify the configuration by running the application:

```bash
python -m uvicorn app.main:app --reload
```

The application will log whether the API keys are loaded successfully:
- ✅ "API key loaded successfully: 2c4bf872-d..."
- ✅ "FalAI client initialized successfully"

If you see error messages about placeholder API keys, make sure you've set real API key values in your `.env` file.

## Troubleshooting

### Error: "API key not configured on server"
- Make sure your `.env` file exists and contains the `API_KEY` variable
- Verify the API key is not a placeholder value

### Error: "FalAI API key is set to a placeholder value"
- Make sure your `.env` file contains a real `FALAI_API_KEY` value
- Replace any placeholder values like "your_falai_api_key_here" with your actual API key

### Error: "FalAI client is not initialized"
- Check that your `FALAI_API_KEY` is set correctly
- Ensure the API key is valid and has the necessary permissions

### Error: "Authentication is required to access this application"
This error indicates that the FalAI API key is not being properly authenticated. To fix this:

1. **Verify API Key Format**: Your FalAI API key should start with `fal_` and be approximately 32 characters long
2. **Check API Key Validity**: Make sure you're using a valid FalAI API key from your account
3. **Verify Permissions**: Ensure your API key has access to the `qwen-image-edit-plus-lora` model
4. **Test API Key**: You can test your API key by making a direct request to the FalAI API

Example of a valid FalAI API key format:
```
FALAI_API_KEY=fal_1234567890abcdef1234567890abcdef
```

### Error: "Access forbidden"
- Your API key may not have permission to access the specific model
- Check your FalAI account permissions and billing status
- Ensure you have sufficient credits for the API calls
