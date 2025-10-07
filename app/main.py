import os
import uuid
import shutil
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from . import db
from .falai_client import edit_image_with_falai
import aiofiles
import traceback

load_dotenv()

# Handle CORS origins properly
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*")
if allowed_origins == "*":
    ALLOWED = ["*"]
else:
    ALLOWED = allowed_origins.split(",")

app = FastAPI(title="haybi-falai-backend", docs_url="/docs", redoc_url="/redoc")

# Configure CORS middleware with more permissive settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    allow_origin_regex="https?://.*"  # Allow any HTTP/HTTPS origin
)

# Remove file system dependency to avoid Render's ephemeral storage issues
# We'll process images directly in memory now

@app.post("/api/jobs", response_model=dict)
async def create_job(background_tasks: BackgroundTasks, image: UploadFile = File(...), prompt: str = Form(...)):
    job_id = str(uuid.uuid4())
    
    try:
        # Read the image data directly into memory
        image_data = await image.read()
        print(f"Received image data of size: {len(image_data)} bytes")
    except Exception as e:
        print(f"Error reading image data for job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error reading image data: {str(e)}")

    # Store job in database with pending status
    await db.db.execute(
        "INSERT INTO jobs(id,status,prompt,original_path) VALUES(:id,:status,:prompt,:path)",
        values={"id": job_id, "status": "pending", "prompt": prompt, "path": f"memory://{job_id}"}
    )

    async def worker(jid, img_data, pr):
        try:
            print(f"Starting image editing for job {jid}")
            resp_json = await edit_image_with_falai(img_data, pr)
            print(f"Image editing completed for job {jid}")
            print(f"Full response: {resp_json}")
            # Extract the result URL from the new response structure
            # The new response has an 'images' array with objects containing 'url' field
            images = resp_json.get("images", [])
            print(f"Images array: {images}")
            if images and isinstance(images, list) and len(images) > 0:
                result_url = images[0].get("url", "")
                print(f"Extracted result URL: {result_url}")
            else:
                result_url = ""
                print("No images found in response")
                # Log the entire response for debugging
                print(f"Full response when no images found: {resp_json}")
                
            if not result_url:
                print(f"No result URL found for job {jid}")
                # Log more details about why we couldn't find a result URL
                if "error" in resp_json:
                    print(f"Error in response: {resp_json['error']}")
                await db.db.execute("UPDATE jobs SET status=:s WHERE id=:id", values={"s": "error", "id": jid})
            else:
                print(f"Result URL for job {jid}: {result_url}")
                await db.db.execute(
                    "UPDATE jobs SET status=:s, result_url=:r WHERE id=:id",
                    values={"s": "done", "r": result_url, "id": jid}
                )
        except Exception as e:
            print(f"Error processing job {jid}: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            # Update job status with error message for better debugging
            error_message = str(e)[:255]  # Limit to 255 characters to avoid DB issues
            await db.db.execute("UPDATE jobs SET status=:s WHERE id=:id", values={"s": "error", "id": jid})

    background_tasks.add_task(worker, job_id, image_data, prompt)
    return {"job_id": job_id}

@app.get("/api/jobs/{job_id}", response_model=dict)
async def get_job(job_id: str):
    row = await db.db.fetch_one("SELECT * FROM jobs WHERE id = :id", values={"id": job_id})
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    return dict(row)

@app.get("/api/jobs", response_model=list)
async def list_jobs():
    rows = await db.db.fetch_all("SELECT id,status,prompt,result_url FROM jobs ORDER BY rowid DESC")
    return [dict(r) for r in rows]

# Health check endpoint
@app.get("/health", status_code=200)
@app.head("/health", status_code=200)
async def health_check():
    """
    Health check endpoint - returns the status of the service
    """
    return {"status": "healthy", "timestamp": __import__('datetime').datetime.utcnow().isoformat()}

# API Info endpoint
@app.get("/api/info", status_code=200)
@app.head("/api/info", status_code=200)
async def api_info():
    """
    API information endpoint
    """
    return {
        "name": "Haybi Image Editing API",
        "description": "API for editing images using AI",
        "version": "1.0.0",
        "endpoints": [
            "POST /api/jobs - Create a new image editing job",
            "GET /api/jobs - List all jobs",
            "GET /api/jobs/{job_id} - Get job details",
            "GET /health - Health check",
            "GET / - API root information"
        ]
    }