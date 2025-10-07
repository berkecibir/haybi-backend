import os
import uuid
import shutil
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from . import db
from .falai_client import edit_image_with_falai
import aiofiles
import traceback

load_dotenv()
ALLOWED = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app = FastAPI(title="haybi-falai-backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED,
    allow_methods=["*"],
    allow_headers=["*"]
)

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.on_event("startup")
async def startup():
    await db.db.connect()
    # basit tablo
    await db.db.execute("""
    CREATE TABLE IF NOT EXISTS jobs(
        id TEXT PRIMARY KEY,
        status TEXT,
        prompt TEXT,
        original_path TEXT,
        result_url TEXT
    )""")

@app.on_event("shutdown")
async def shutdown():
    await db.db.disconnect()

@app.post("/api/jobs", response_model=dict)
async def create_job(background_tasks: BackgroundTasks, image: UploadFile = File(...), prompt: str = Form(...)):
    job_id = str(uuid.uuid4())
    # Use only the filename, not the full path
    filename = f"{job_id}_{image.filename}"
    save_path = os.path.join(UPLOAD_DIR, filename)
    
    # Save the uploaded file
    async with aiofiles.open(save_path, "wb") as f:
        content = await image.read()
        await f.write(content)

    await db.db.execute(
        "INSERT INTO jobs(id,status,prompt,original_path) VALUES(:id,:status,:prompt,:path)",
        values={"id": job_id, "status": "pending", "prompt": prompt, "path": save_path}
    )

    async def worker(jid, path, pr):
        try:
            print(f"Starting image editing for job {jid}")
            resp_json = await edit_image_with_falai(path, pr)
            print(f"Image editing completed for job {jid}")
            # Extract the result URL from the new response structure
            # The new response has an 'images' array with objects containing 'url' field
            images = resp_json.get("images", [])
            if images and isinstance(images, list) and len(images) > 0:
                result_url = images[0].get("url", "")
            else:
                result_url = ""
                
            if not result_url:
                print(f"No result URL found for job {jid}")
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
            await db.db.execute("UPDATE jobs SET status=:s WHERE id=:id", values={"s": "error", "id": jid})

    background_tasks.add_task(worker, job_id, save_path, prompt)
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