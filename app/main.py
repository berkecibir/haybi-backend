from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import logging
import base64
import io
import os
from app.falai_client import FalAIClient

app = FastAPI()
falai_client = FalAIClient()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Root endpoint for API discoverability
@app.get("/")
async def root():
    return {
        "message": "Haybi Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "image_edit": "/edit-image/"
        }
    }

class ImageEditRequest(BaseModel):
    prompt: str
    image_base64: str

@app.post("/edit-image/")
async def edit_image(request: ImageEditRequest):
    logging.info(f"Gelen prompt: {request.prompt}")
    
    try:
        # Decode base64 image data
        image_data = base64.b64decode(request.image_base64)
        logging.info(f"Decoded image data length: {len(image_data)} bytes")
        
        # Process with FalAI
        logging.info("FalAI client processing started...")
        result = await falai_client.process(request.prompt, image_data)
        
        # Log the result object for debugging
        logging.info(f"Raw result from FalAI: {result}")
        
        # Check if result is valid and has URL
        if result is None:
            logging.error("FalAI returned None result")
            return {"status": "error", "message": "FalAI returned None result"}
            
        if not hasattr(result, 'url') or result.url is None:
            logging.error(f"FalAI result missing URL. Result: {result}")
            return {"status": "error", "message": f"FalAI result missing URL. Result: {result}"}
        
        logging.info("İşlem başarılı.")
        return {"status": "success", "result_url": result.url}
        
    except Exception as e:
        logging.error(f"Hata oluştu: {str(e)}", exc_info=True)
        return {"status": "error", "message": str(e)}