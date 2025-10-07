import requests
import json
import os
import time
from PIL import Image

# Create a proper test image with minimum size (256x256)
test_image_path = "test_images/test_image.png"
os.makedirs(os.path.dirname(test_image_path), exist_ok=True)

# Create a 256x256 red square image
image = Image.new('RGB', (256, 256), color='red')
image.save(test_image_path, 'PNG')

# Test the image editing endpoint
url = "http://127.0.0.1:8000/api/jobs"
prompt = "Turn the red square into a blue circle"

with open(test_image_path, "rb") as f:
    files = {
        'image': ('test_image.png', f, 'image/png'),
    }
    data = {
        'prompt': prompt
    }
    
    response = requests.post(url, files=files, data=data)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {result}")
        
        # Wait a bit for the job to process
        print("Waiting for job to process...")
        time.sleep(15)
        
        # Check job status
        job_id = result['job_id']
        status_url = f"http://127.0.0.1:8000/api/jobs/{job_id}"
        status_response = requests.get(status_url)
        if status_response.status_code == 200:
            status_result = status_response.json()
            print(f"Job Status: {status_result}")
        else:
            print(f"Failed to get job status: {status_response.text}")
    else:
        print(f"Error: {response.text}")