import os
import httpx
import base64
from dotenv import load_dotenv
import json

load_dotenv()
FALAI_KEY = os.getenv("FALAI_API_KEY")

# Using the Qwen Image Edit Plus LoRA model for better image editing capabilities
FALAI_URL = "https://fal.run/fal-ai/qwen-image-edit-plus-lora"

async def edit_image_with_falai(image_path: str, prompt: str):
    headers = {
        "Authorization": f"Key {FALAI_KEY}",
        "Content-Type": "application/json"
    }
    
    # Read and encode the image as base64
    with open(image_path, "rb") as f:
        image_data = f.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        image_url = f"data:image/jpeg;base64,{image_base64}"
    
    # Prepare the payload according to Qwen Image Edit Plus LoRA API specification
    payload = {
        "image_urls": [image_url],
        "prompt": prompt,
        "num_inference_steps": 28,
        "guidance_scale": 4,
        "num_images": 1,
        "enable_safety_checker": True,
        "output_format": "png",
        "negative_prompt": "",
        "acceleration": "regular"
    }
    
    print(f"Sending request to {FALAI_URL}")
    print(f"Headers: {headers}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    async with httpx.AsyncClient(timeout=120) as client:
        try:
            resp = await client.post(FALAI_URL, headers=headers, json=payload)
            print(f"Response status: {resp.status_code}")
            print(f"Response headers: {resp.headers}")
            
            # Check if the response is successful
            if resp.status_code != 200:
                print(f"Non-success status code: {resp.status_code}")
                print(f"Response content: {resp.text}")
                resp.raise_for_status()
            
            try:
                result = resp.json()
                print(f"Response JSON: {json.dumps(result, indent=2)}")
            except json.JSONDecodeError as e:
                print(f"Failed to decode JSON response: {e}")
                print(f"Response content: {resp.text}")
                raise Exception(f"Invalid JSON response: {resp.text}")
            
            # Check if the response contains error information
            if "error" in result:
                print(f"API returned error: {result['error']}")
                raise Exception(f"API error: {result['error']}")
            
            # Check if the response has the expected structure
            if "images" not in result:
                print(f"Unexpected response structure. Missing 'images' key. Full response: {result}")
                raise Exception(f"Unexpected response structure: {result}")
                
            return result
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
            print(f"Response content: {e.response.text}")
            raise
        except Exception as e:
            print(f"An error occurred: {e}")
            raise