import os
import httpx
import base64
from dotenv import load_dotenv
import json
import asyncio
import logging
from typing import Optional

load_dotenv()
FALAI_KEY = os.getenv("FALAI_API_KEY")

# Using the Qwen Image Edit Plus LoRA model for better image editing capabilities
FALAI_URL = "https://fal.run/fal-ai/qwen-image-edit-plus-lora"

class FalAIResult:
    def __init__(self, url: Optional[str] = None):
        self.url = url

class FalAIClient:
    def __init__(self):
        self.api_key = FALAI_KEY
        self.url = FALAI_URL
    
    async def process(self, prompt: str, image_data: bytes, max_retries=3):
        """
        Process image directly with FalAI API using base64 encoded data
        This eliminates the need for local file storage and avoids Render's ephemeral storage issues
        """
        headers = {
            "Authorization": f"Key {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Encode the image data as base64
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
        
        # Set timeout to 300 seconds (5 minutes) as requested
        async with httpx.AsyncClient(timeout=300.0) as client:
            for attempt in range(max_retries):
                try:
                    logging.info(f"Sending request to {self.url} (attempt {attempt + 1}/{max_retries})")
                    logging.debug(f"Headers: {headers}")
                    # Only log payload details on first attempt to avoid log spam
                    if attempt == 0:
                        logging.debug(f"Payload: {json.dumps(payload, indent=2)}")
                    
                    resp = await client.post(self.url, headers=headers, json=payload)
                    logging.info(f"Response status: {resp.status_code}")
                    logging.debug(f"Response headers: {resp.headers}")
                    
                    # Check if the response is successful
                    if resp.status_code != 200:
                        logging.warning(f"Non-success status code: {resp.status_code}")
                        logging.debug(f"Response content: {resp.text}")
                        if attempt < max_retries - 1:
                            logging.info(f"Retrying in 2 seconds...")
                            await asyncio.sleep(2)
                            continue
                        resp.raise_for_status()
                    
                    try:
                        result = resp.json()
                        logging.debug(f"Response JSON: {json.dumps(result, indent=2)}")
                    except json.JSONDecodeError as e:
                        logging.error(f"Failed to decode JSON response: {e}")
                        logging.debug(f"Response content: {resp.text}")
                        if attempt < max_retries - 1:
                            logging.info(f"Retrying in 2 seconds...")
                            await asyncio.sleep(2)
                            continue
                        raise Exception(f"Invalid JSON response: {resp.text}")
                    
                    # Check if the response contains error information
                    if "error" in result:
                        logging.error(f"API returned error: {result['error']}")
                        if attempt < max_retries - 1:
                            logging.info(f"Retrying in 2 seconds...")
                            await asyncio.sleep(2)
                            continue
                        raise Exception(f"API error: {result['error']}")
                    
                    # Check if the response has the expected structure
                    if "images" not in result:
                        logging.error(f"Unexpected response structure. Missing 'images' key. Full response: {result}")
                        if attempt < max_retries - 1:
                            logging.info(f"Retrying in 2 seconds...")
                            await asyncio.sleep(2)
                            continue
                        raise Exception(f"Unexpected response structure: {result}")
                    
                    # Check if safety checker blocked the content
                    if "has_nsfw_concepts" in result and result["has_nsfw_concepts"]:
                        if any(result["has_nsfw_concepts"]):
                            logging.warning(f"Safety checker blocked content: {result['has_nsfw_concepts']}")
                            # Don't retry if safety checker blocked - it's unlikely to succeed on retry
                            raise Exception(f"Safety checker blocked content: {result['has_nsfw_concepts']}")
                    
                    # Extract URL from the images array
                    if result["images"] and len(result["images"]) > 0:
                        image_url = result["images"][0]["url"]
                        return FalAIResult(url=image_url)
                    else:
                        raise Exception("No images returned from FalAI")
                    
                except httpx.TimeoutException as e:
                    logging.error(f"Timeout error occurred: {e}")
                    if attempt < max_retries - 1:
                        logging.info(f"Retrying in 2 seconds...")
                        await asyncio.sleep(2)
                        continue
                    raise Exception(f"Timeout after {max_retries} attempts: {e}")
                    
                except httpx.HTTPStatusError as e:
                    logging.error(f"HTTP error occurred: {e}")
                    logging.debug(f"Response content: {e.response.text}")
                    if attempt < max_retries - 1:
                        logging.info(f"Retrying in 2 seconds...")
                        await asyncio.sleep(2)
                        continue
                    raise
                    
                except Exception as e:
                    logging.error(f"An error occurred: {e}")
                    if attempt < max_retries - 1:
                        logging.info(f"Retrying in 2 seconds...")
                        await asyncio.sleep(2)
                        continue
                    raise
            
            # If we get here, all retries have been exhausted
            raise Exception(f"Failed after {max_retries} attempts")

# Also keep the original function for backward compatibility
async def edit_image_with_falai(image_data: bytes, prompt: str, max_retries=3):
    """
    Process image directly with FalAI API using base64 encoded data
    This eliminates the need for local file storage and avoids Render's ephemeral storage issues
    """
    client = FalAIClient()
    return await client.process(prompt, image_data, max_retries)