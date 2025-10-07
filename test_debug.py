import requests
import json
import os
import time
from PIL import Image
import io

# Create a test image in memory
image = Image.new('RGB', (256, 256), color='blue')
img_byte_arr = io.BytesIO()
image.save(img_byte_arr, format='JPEG')
img_byte_arr.seek(0)

# Test the image editing endpoint
url = "http://127.0.0.1:8000/api/jobs"
prompt = "Change bag to a silver laptop"

files = {
    'image': ('debug_test_image.jpg', img_byte_arr, 'image/jpeg'),
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