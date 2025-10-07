import requests
import json
import os
from PIL import Image

# Create a proper test image with minimum size (256x256)
test_image_path = "test_images/deployed_test_image.png"
os.makedirs(os.path.dirname(test_image_path), exist_ok=True)

# Create a 256x256 red square image
image = Image.new('RGB', (256, 256), color='red')
image.save(test_image_path, 'PNG')

# Test the deployed image editing endpoint
# Replace with your actual Render URL
url = "https://haybi-backend.onrender.com/api/jobs"
prompt = "Turn the red square into a blue circle"

# Test CORS preflight request
print("Testing CORS preflight request...")
try:
    options_response = requests.options(
        url,
        headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }
    )
    print(f"OPTIONS request status: {options_response.status_code}")
    print(f"Access-Control-Allow-Origin: {options_response.headers.get('Access-Control-Allow-Origin', 'Not set')}")
except Exception as e:
    print(f"Error with OPTIONS request: {e}")

# Test actual POST request
print("\nTesting POST request...")
try:
    with open(test_image_path, "rb") as f:
        files = {
            'image': ('test_image.png', f, 'image/png'),
        }
        data = {
            'prompt': prompt
        }
        
        response = requests.post(url, files=files, data=data)
        print(f"POST request status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result}")
        else:
            print(f"Error: {response.text}")
except Exception as e:
    print(f"Error with POST request: {e}")