import os
from dotenv import load_dotenv

from fastapi import FastAPI, Request, UploadFile, File, HTTPException, Form, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import base64
import uuid
import asyncio
from typing import Optional, List
from app.falai_client import FalAIClient
from app.schemas import JobCreateResponse, Job
from app.db import db, init_db, create_job, get_job, get_all_jobs, update_job_status

# Load environment variables from .env file
load_dotenv()

app = FastAPI()
falai_client = FalAIClient()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Configure CORS to allow all origins, specific methods and all headers as required
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,  # Must be False when allow_origins="*"
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=[],
)

# Required API key for authentication (loaded from environment variable)
REQUIRED_API_KEY = os.getenv("API_KEY")

# Authentication dependency
def verify_auth(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    token = authorization[len("Bearer "):]
    if not REQUIRED_API_KEY:
        raise HTTPException(status_code=500, detail="API key not configured on server")
    
    if token != REQUIRED_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return True

@app.on_event("startup")
async def startup():
    await db.connect()
    await init_db()

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

@app.post("/edit-image/")
async def edit_image(
    image: UploadFile = File(...),
    prompt: str = Form(...),
    auth: bool = Depends(verify_auth)
):
    logging.info(f"Received image edit request with prompt: {prompt}")
    
    try:
        # Validate image
        if not image:
            raise HTTPException(status_code=422, detail="No image provided")
        
        if not prompt:
            raise HTTPException(status_code=422, detail="No prompt provided")
        
        # Generate a unique job ID
        job_id = str(uuid.uuid4())
        logging.info(f"Generated job ID: {job_id}")
        
        # Save job to database
        await create_job(job_id, prompt, f"memory://{job_id}")
        
        # Read image data
        image_data = await image.read()
        logging.info(f"Image data read. Size: {len(image_data)} bytes")
        
        # Start processing the image in the background
        asyncio.create_task(process_image_job(job_id, prompt, image))
        
        # Return job ID immediately
        return {"job_id": job_id}
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred during image processing. Please try again.")

# Create a new job for image editing
@app.post("/api/jobs", response_model=JobCreateResponse)
async def create_job_endpoint(request: Request, prompt: str = Form(...), image: UploadFile = File(...)):
    origin = request.headers.get("origin")
    logging.info(f"Incoming Origin: {origin}")
    logging.info(f"Job creation request received. Prompt: {prompt}, Image filename: {image.filename}, Content type: {image.content_type}")
    
    # Validate image
    if not image:
        raise HTTPException(status_code=400, detail="No image provided")
    
    if not prompt:
        raise HTTPException(status_code=400, detail="No prompt provided")
    
    # Generate a unique job ID
    job_id = str(uuid.uuid4())
    logging.info(f"Generated job ID: {job_id}")
    
    # Save job to database
    await create_job(job_id, prompt, f"memory://{job_id}")
    
    # Start processing the image in the background
    asyncio.create_task(process_image_job(job_id, prompt, image))
    
    return JobCreateResponse(job_id=job_id)

# Handle OPTIONS requests for CORS preflight
@app.options("/api/jobs")
async def options_jobs():
    return {}

# Get the status of a job
@app.get("/api/jobs/{job_id}", response_model=Job)
async def get_job_endpoint(job_id: str):
    logging.info(f"Job status request received. Job ID: {job_id}")
    
    job = await get_job(job_id)
    if not job:
        logging.error(f"Job not found: {job_id}")
        raise HTTPException(status_code=404, detail="Job not found")
    
    logging.info(f"Job status: {dict(job)}")
    return Job(**dict(job))

# Get the status of an image edit job
@app.get("/edit-image/{job_id}")
async def get_edit_image_job_status(
    job_id: str,
    auth: bool = Depends(verify_auth)
):
    logging.info(f"Image edit job status request received. Job ID: {job_id}")
    
    job = await get_job(job_id)
    if not job:
        logging.error(f"Job not found: {job_id}")
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Return the job status in the required format
    return {
        "id": job["id"],
        "status": job["status"],
        "prompt": job["prompt"],
        "original_path": job["original_path"],
        "result_url": job["result_url"]
    }

# List all jobs
@app.get("/api/jobs", response_model=List[Job])
async def list_jobs():
    logging.info("Listing all jobs")
    jobs = await get_all_jobs()
    return [Job(**dict(job)) for job in jobs]

# Background task to process the image
async def process_image_job(job_id: str, prompt: str, image: UploadFile):
    try:
        logging.info(f"Starting image processing for job {job_id}")
        # Update job status to processing
        await update_job_status(job_id, "processing")
        
        # Read image data
        image_data = await image.read()
        logging.info(f"Image data read. Size: {len(image_data)} bytes")
        
        # Process with FalAI
        logging.info(f"Processing job {job_id} with prompt: {prompt}")
        result = await falai_client.process(prompt, image_data)
        logging.info(f"FalAI processing result: {result}")
        
        # Update job with result
        if result and result.url:
            await update_job_status(job_id, "completed", result.url)
            logging.info(f"Job {job_id} completed successfully. Result URL: {result.url}")
        else:
            await update_job_status(job_id, "failed")
            logging.error(f"Job {job_id} failed. No result URL returned from FalAI.")
            
    except Exception as e:
        logging.error(f"Error processing job {job_id}: {str(e)}", exc_info=True)
        await update_job_status(job_id, "failed")

""" from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import base64
import io
import os
import uuid
import asyncio
from typing import Optional, List
from app.falai_client import FalAIClient
from app.schemas import JobCreateResponse, Job
from app.db import db, init_db, create_job, get_job, get_all_jobs, update_job_status

app = FastAPI()
falai_client = FalAIClient()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Configure CORS
# Use ALLOWED_ORIGINS environment variable if set, otherwise use default origins
allowed_origins = os.getenv("ALLOWED_ORIGINS", "https://haybi-backend.onrender.com,http://localhost:8000,http://localhost:8080")
if allowed_origins == "*":
    origins = ["*"]
else:
    origins = [origin.strip() for origin in allowed_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.on_event("startup")
async def startup():
    await db.connect()
    await init_db()

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
            return {"status": "error", "message": "Image processing failed. Please try again."}
            
        if not hasattr(result, 'url') or result.url is None:
            logging.error(f"FalAI result missing URL.")
            return {"status": "error", "message": "Image processing failed. Please try again with a different prompt."}
        
        logging.info("İşlem başarılı.")
        return {"status": "success", "result_url": result.url}
        
    except Exception as e:
        logging.error(f"Hata oluştu: {str(e)}", exc_info=True)
        return {"status": "error", "message": "An error occurred during image processing. Please try again."}

# Create a new job for image editing
@app.post("/api/jobs", response_model=JobCreateResponse)
async def create_job_endpoint(prompt: str = Form(...), image: UploadFile = File(...)):
    logging.info(f"Job creation request received. Prompt: {prompt}, Image filename: {image.filename}, Content type: {image.content_type}")
    
    # Validate image
    if not image:
        raise HTTPException(status_code=400, detail="No image provided")
    
    if not prompt:
        raise HTTPException(status_code=400, detail="No prompt provided")
    
    # Generate a unique job ID
    job_id = str(uuid.uuid4())
    logging.info(f"Generated job ID: {job_id}")
    
    # Save job to database
    await create_job(job_id, prompt, f"memory://{job_id}")
    
    # Start processing the image in the background
    asyncio.create_task(process_image_job(job_id, prompt, image))
    
    return JobCreateResponse(job_id=job_id)

# Handle OPTIONS requests for CORS preflight
@app.options("/api/jobs")
async def options_jobs():
    return {}

# Get the status of a job
@app.get("/api/jobs/{job_id}", response_model=Job)
async def get_job_endpoint(job_id: str):
    logging.info(f"Job status request received. Job ID: {job_id}")
    
    job = await get_job(job_id)
    if not job:
        logging.error(f"Job not found: {job_id}")
        raise HTTPException(status_code=404, detail="Job not found")
    
    logging.info(f"Job status: {dict(job)}")
    return Job(**dict(job))

# List all jobs
@app.get("/api/jobs", response_model=List[Job])
async def list_jobs():
    logging.info("Listing all jobs")
    jobs = await get_all_jobs()
    return [Job(**dict(job)) for job in jobs]

# Background task to process the image
async def process_image_job(job_id: str, prompt: str, image: UploadFile):
    try:
        logging.info(f"Starting image processing for job {job_id}")
        # Update job status to processing
        await update_job_status(job_id, "processing")
        
        # Read image data
        image_data = await image.read()
        logging.info(f"Image data read. Size: {len(image_data)} bytes")
        
        # Process with FalAI
        logging.info(f"Processing job {job_id} with prompt: {prompt}")
        result = await falai_client.process(prompt, image_data)
        logging.info(f"FalAI processing result: {result}")
        
        # Update job with result
        if result and result.url:
            await update_job_status(job_id, "completed", result.url)
            logging.info(f"Job {job_id} completed successfully. Result URL: {result.url}")
        else:
            await update_job_status(job_id, "failed")
            logging.error(f"Job {job_id} failed. No result URL returned from FalAI.")
            
    except Exception as e:
        logging.error(f"Error processing job {job_id}: {str(e)}", exc_info=True)
        await update_job_status(job_id, "failed")
 """

