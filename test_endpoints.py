import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the API key from environment
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY not found in environment variables")

# Base URL
BASE_URL = "http://127.0.0.1:8000"

# Headers with authentication
headers = {
    "Authorization": f"Bearer {API_KEY}"
}

def test_root_endpoint():
    """Test the root endpoint"""
    print("Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_post_edit_image():
    """Test the POST /edit-image/ endpoint"""
    print("Testing POST /edit-image/ endpoint...")
    
    # Create a simple test image (1x1 pixel PNG)
    import base64
    test_image_data = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    )
    
    files = {
        "image": ("test.png", test_image_data, "image/png")
    }
    data = {
        "prompt": "make it blue"
    }
    
    response = requests.post(
        f"{BASE_URL}/edit-image/",
        files=files,
        data=data,
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
        return response.json().get("job_id")
    else:
        print(f"Error: {response.text}")
    print()

def test_get_edit_image_status(job_id):
    """Test the GET /edit-image/{job_id} endpoint"""
    if not job_id:
        print("No job ID provided, skipping GET test")
        return
        
    print(f"Testing GET /edit-image/{job_id} endpoint...")
    response = requests.get(
        f"{BASE_URL}/edit-image/{job_id}",
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")
    print()

def test_unauthorized_access():
    """Test accessing endpoint without proper authorization"""
    print("Testing unauthorized access (invalid key)...")
    # Test with invalid API key
    invalid_headers = {
        "Authorization": "Bearer invalid-key"
    }
    response = requests.get(f"{BASE_URL}/edit-image/test-job-id", headers=invalid_headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    print("Testing unauthorized access (missing header)...")
    # Test with missing authorization header
    response = requests.get(f"{BASE_URL}/edit-image/test-job-id")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

if __name__ == "__main__":
    print("Running endpoint tests...\n")
    
    # Test root endpoint
    test_root_endpoint()
    
    # Test POST endpoint
    job_id = test_post_edit_image()
    
    # Test GET endpoint
    test_get_edit_image_status(job_id)
    
    # Test unauthorized access
    test_unauthorized_access()
    
    print("All tests completed!")