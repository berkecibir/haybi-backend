import requests
import json
import os
from PIL import Image

def test_cors_and_job_creation():
    """
    Test CORS fix and job creation without authentication header
    """
    print("🔍 Testing CORS fix and job creation...")
    
    # Create a test image
    test_image_path = "test_images/cors_test_image.png"
    os.makedirs(os.path.dirname(test_image_path), exist_ok=True)
    
    # Create a 256x256 test image
    image = Image.new('RGB', (256, 256), color='blue')
    image.save(test_image_path, 'PNG')
    
    # Test the API endpoint WITHOUT Authorization header (as it should be)
    url = "https://haybi-backend.onrender.com/api/jobs"
    prompt = "Create a cyberpunk version of the swans with neon lights and futuristic elements"
    
    print(f"Sending request to: {url}")
    print(f"Prompt: {prompt}")
    
    try:
        with open(test_image_path, "rb") as f:
            files = {
                'image': ('test_image.png', f, 'image/png'),
            }
            data = {
                'prompt': prompt
            }
            
            # Send request WITHOUT Authorization header
            response = requests.post(url, files=files, data=data)
            print(f"Response status code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success! Job ID: {result.get('job_id')}")
                return result.get('job_id')
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response text: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return None

def test_cors_preflight():
    """
    Test CORS preflight request
    """
    print("\n🔍 Testing CORS preflight request...")
    
    url = "https://haybi-backend.onrender.com/api/jobs"
    
    try:
        response = requests.options(
            url,
            headers={
                "Origin": "https://your-flutter-app.onrender.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        print(f"Preflight status code: {response.status_code}")
        
        if response.status_code == 200:
            allow_origin = response.headers.get('Access-Control-Allow-Origin', 'Not set')
            print(f"✅ CORS preflight successful!")
            print(f"Access-Control-Allow-Origin: {allow_origin}")
        else:
            print(f"❌ CORS preflight failed with status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing CORS preflight: {e}")

def test_with_custom_origin():
    """
    Test request with custom origin header
    """
    print("\n🔍 Testing request with custom origin...")
    
    # Create a test image
    test_image_path = "test_images/origin_test_image.png"
    os.makedirs(os.path.dirname(test_image_path), exist_ok=True)
    
    # Create a 256x256 test image
    image = Image.new('RGB', (256, 256), color='green')
    image.save(test_image_path, 'PNG')
    
    url = "https://haybi-backend.onrender.com/api/jobs"
    prompt = "Test image with custom origin"
    
    try:
        with open(test_image_path, "rb") as f:
            files = {
                'image': ('test_image.png', f, 'image/png'),
            }
            data = {
                'prompt': prompt
            }
            
            # Send request with Origin header
            response = requests.post(
                url, 
                files=files, 
                data=data,
                headers={
                    "Origin": "https://your-flutter-app.onrender.com"
                }
            )
            
            print(f"Response status code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success with custom origin! Job ID: {result.get('job_id')}")
                return result.get('job_id')
            else:
                print(f"❌ Error with custom origin: {response.status_code}")
                print(f"Response text: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Exception occurred with custom origin: {e}")
        return None

if __name__ == "__main__":
    print("🔧 Testing CORS fixes for Haybi Backend")
    print("=" * 50)
    
    # Test CORS preflight
    test_cors_preflight()
    
    # Test job creation without auth header
    job_id1 = test_cors_and_job_creation()
    
    # Test with custom origin
    job_id2 = test_with_custom_origin()
    
    print("\n" + "=" * 50)
    if job_id1 or job_id2:
        print("🎉 Tests completed successfully!")
        if job_id1:
            print(f"Job 1 ID: {job_id1}")
        if job_id2:
            print(f"Job 2 ID: {job_id2}")
    else:
        print("❌ Tests failed. Check the errors above.")
        
    print("\n💡 Next steps:")
    print("1. Update your Flutter app to NOT send Authorization header for /api/jobs endpoint")
    print("2. Make sure your Flutter app's origin is included in ALLOWED_ORIGINS")
    print("3. If deploying to Render, update the ALLOWED_ORIGINS environment variable")