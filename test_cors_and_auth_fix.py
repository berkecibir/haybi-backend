import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the API key from environment
API_KEY = os.getenv("API_KEY")
print(f"API Key from environment: {API_KEY}")

# Base URL
BASE_URL = "http://127.0.0.1:8000"

# Headers with authentication
headers_with_auth = {
    "Authorization": f"Bearer {API_KEY}"
}

# Headers without authentication
headers_without_auth = {}

def test_root_endpoint():
    """Test the root endpoint"""
    print("\n=== Testing root endpoint ===")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")
    return response.status_code == 200

def test_health_endpoint():
    """Test the health endpoint"""
    print("\n=== Testing health endpoint ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")
    return response.status_code == 200

def test_cors_preflight():
    """Test CORS preflight request"""
    print("\n=== Testing CORS preflight (OPTIONS) ===")
    response = requests.options(f"{BASE_URL}/api/jobs")
    print(f"Status Code: {response.status_code}")
    print(f"Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'Not set')}")
    print(f"Access-Control-Allow-Methods: {response.headers.get('Access-Control-Allow-Methods', 'Not set')}")
    print(f"Access-Control-Allow-Headers: {response.headers.get('Access-Control-Allow-Headers', 'Not set')}")
    return response.status_code in [200, 204]

def test_create_job_without_auth():
    """Test creating a job without authentication"""
    print("\n=== Testing job creation WITHOUT authentication ===")
    
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
        f"{BASE_URL}/api/jobs",
        files=files,
        data=data
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
        return response.json().get("job_id")
    else:
        print(f"Error: {response.text}")
    return None

def test_create_job_with_auth():
    """Test creating a job with authentication"""
    print("\n=== Testing job creation WITH authentication ===")
    
    # Create a simple test image (1x1 pixel PNG)
    import base64
    test_image_data = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    )
    
    files = {
        "image": ("test.png", test_image_data, "image/png")
    }
    data = {
        "prompt": "make it red"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/jobs",
        files=files,
        data=data,
        headers=headers_with_auth
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
        return response.json().get("job_id")
    else:
        print(f"Error: {response.text}")
    return None

def test_get_job_status(job_id):
    """Test getting job status"""
    if not job_id:
        print("\n=== Skipping job status test (no job ID) ===")
        return True
        
    print(f"\n=== Testing job status retrieval for {job_id} ===")
    response = requests.get(f"{BASE_URL}/api/jobs/{job_id}")
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_edit_image_without_auth():
    """Test the POST /edit-image/ endpoint without authentication"""
    print("\n=== Testing POST /edit-image/ WITHOUT authentication ===")
    
    # Create a simple test image (1x1 pixel PNG)
    import base64
    test_image_data = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    )
    
    files = {
        "image": ("test.png", test_image_data, "image/png")
    }
    data = {
        "prompt": "make it green"
    }
    
    response = requests.post(
        f"{BASE_URL}/edit-image/",
        files=files,
        data=data
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
        return response.json().get("job_id")
    elif response.status_code == 401:
        print("Expected: Authentication required for /edit-image/ endpoint")
        return None
    else:
        print(f"Error: {response.text}")
    return None

def test_edit_image_with_auth():
    """Test the POST /edit-image/ endpoint with authentication"""
    print("\n=== Testing POST /edit-image/ WITH authentication ===")
    
    # Create a simple test image (1x1 pixel PNG)
    import base64
    test_image_data = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    )
    
    files = {
        "image": ("test.png", test_image_data, "image/png")
    }
    data = {
        "prompt": "make it yellow"
    }
    
    response = requests.post(
        f"{BASE_URL}/edit-image/",
        files=files,
        data=data,
        headers=headers_with_auth
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
        return response.json().get("job_id")
    else:
        print(f"Error: {response.text}")
    return None

if __name__ == "__main__":
    print("Running CORS and authentication fix tests...\n")
    
    # Test basic endpoints
    test_root_endpoint()
    test_health_endpoint()
    test_cors_preflight()
    
    # Test job creation (should work without auth)
    job_id_1 = test_create_job_without_auth()
    job_id_2 = test_create_job_with_auth()
    
    # Test job status retrieval
    test_get_job_status(job_id_1)
    test_get_job_status(job_id_2)
    
    # Test edit-image endpoint (should require auth)
    edit_job_id_1 = test_edit_image_without_auth()
    edit_job_id_2 = test_edit_image_with_auth()
    
    print("\n=== All tests completed! ===")