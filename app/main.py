from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import base64
import io
import os
import uuid
import asyncio
from typing import Optional
from app.falai_client import FalAIClient
from app.schemas import JobCreateResponse, Job
from app.db import db

app = FastAPI()
falai_client = FalAIClient()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://haybi-backend.onrender.com", "http://localhost:8000"],  # Belirli origin'ler
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# In-memory storage for jobs (in production, use a proper database)
jobs = {}

@app.on_event("startup")
async def startup():
    await db.connect()

@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()

# Root endpoint for API discoverability
@app.get("/")
@app.head("/")
async def root():
    return {
        "message": "Haybi Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "image_edit": "/edit-image/",
            "job_create": "/api/jobs",
            "job_status": "/api/jobs/{job_id}",
            "health": "/health",
            "api_info": "/api/info"
        }
    }

# Health check endpoint
@app.get("/health")
@app.head("/health")
async def health_check():
    return {"status": "healthy"}

# API info endpoint
@app.get("/api/info")
@app.head("/api/info")
async def api_info():
    return {
        "name": "Haybi Backend API",
        "version": "1.0.0",
        "description": "Backend API for Haybi image editing application",
        "endpoints": {
            "image_edit": {
                "method": "POST",
                "path": "/edit-image/",
                "description": "Edit images using AI"
            },
            "job_create": {
                "method": "POST",
                "path": "/api/jobs",
                "description": "Create a new image editing job"
            },
            "job_status": {
                "method": "GET",
                "path": "/api/jobs/{job_id}",
                "description": "Get the status of an image editing job"
            },
            "health": {
                "method": "GET",
                "path": "/health",
                "description": "Health check endpoint"
            },
            "api_info": {
                "method": "GET",
                "path": "/api/info",
                "description": "API information endpoint"
            }
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

# Create a new job for image editing
@app.post("/api/jobs", response_model=JobCreateResponse)
async def create_job(prompt: str = Form(...), image: UploadFile = File(...)):
    logging.info(f"Job creation request received. Prompt: {prompt}, Image filename: {image.filename}, Content type: {image.content_type}")
    
    # Validate image
    if not image:
        raise HTTPException(status_code=400, detail="No image provided")
    
    if not prompt:
        raise HTTPException(status_code=400, detail="No prompt provided")
    
    # Generate a unique job ID
    job_id = str(uuid.uuid4())
    logging.info(f"Generated job ID: {job_id}")
    
    # Save job to in-memory storage
    jobs[job_id] = {
        "id": job_id,
        "status": "pending",
        "prompt": prompt,
        "original_path": f"memory://{job_id}",
        "result_url": None
    }
    
    # Start processing the image in the background
    asyncio.create_task(process_image_job(job_id, prompt, image))
    
    return JobCreateResponse(job_id=job_id)

# Get the status of a job
@app.get("/api/jobs/{job_id}", response_model=Job)
async def get_job(job_id: str):
    logging.info(f"Job status request received. Job ID: {job_id}")
    
    if job_id not in jobs:
        logging.error(f"Job not found: {job_id}")
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    logging.info(f"Job status: {job}")
    return Job(
        id=job["id"],
        status=job["status"],
        prompt=job["prompt"],
        original_path=job["original_path"],
        result_url=job["result_url"]
    )

# Background task to process the image
async def process_image_job(job_id: str, prompt: str, image: UploadFile):
    try:
        logging.info(f"Starting image processing for job {job_id}")
        # Update job status to processing
        jobs[job_id]["status"] = "processing"
        
        # Read image data
        image_data = await image.read()
        logging.info(f"Image data read. Size: {len(image_data)} bytes")
        
        # Process with FalAI
        logging.info(f"Processing job {job_id} with prompt: {prompt}")
        result = await falai_client.process(prompt, image_data)
        logging.info(f"FalAI processing result: {result}")
        
        # Update job with result
        if result and result.url:
            jobs[job_id]["status"] = "completed"
            jobs[job_id]["result_url"] = result.url
            logging.info(f"Job {job_id} completed successfully. Result URL: {result.url}")
        else:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["result_url"] = None
            logging.error(f"Job {job_id} failed. No result URL returned from FalAI.")
            
    except Exception as e:
        logging.error(f"Error processing job {job_id}: {str(e)}", exc_info=True)
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["result_url"] = None