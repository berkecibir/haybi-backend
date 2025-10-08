#!/usr/bin/env python3
"""
Setup script to help configure environment variables
"""
import os

def create_env_file():
    """Create a .env file with the correct API key configuration"""
    
    # Check if .env file already exists
    if os.path.exists('.env'):
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    # Get API key from user
    print("\n🔑 API Key Configuration")
    print("=" * 50)
    
    api_key = input("Enter your API_KEY (for backend authentication): ").strip()
    if not api_key:
        print("❌ API_KEY is required!")
        return
    
    falai_api_key = input("Enter your FALAI_API_KEY (for image processing): ").strip()
    if not falai_api_key:
        print("❌ FALAI_API_KEY is required!")
        return
    
    base_url = input("Enter BASE_URL (default: https://haybi-backend.onrender.com): ").strip()
    if not base_url:
        base_url = "https://haybi-backend.onrender.com"
    
    # Create .env file content
    env_content = f"""# API Key for backend authentication
API_KEY={api_key}

# FalAI API Key for image processing
FALAI_API_KEY={falai_api_key}

# Base URL for the application
BASE_URL={base_url}
"""
    
    # Write .env file
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("\n✅ .env file created successfully!")
        print("🔒 The .env file is already in .gitignore, so your API keys won't be committed to git.")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")

def main():
    print("🚀 Haybi Backend Environment Setup")
    print("=" * 50)
    print("This script will help you configure the required environment variables.")
    print("Make sure you have your API keys ready before proceeding.\n")
    
    create_env_file()
    
    print("\n📋 Next Steps:")
    print("1. Verify your .env file contains the correct API keys")
    print("2. Run the application: python -m uvicorn app.main:app --reload")
    print("3. Test the endpoints to ensure everything works")

if __name__ == "__main__":
    main()
