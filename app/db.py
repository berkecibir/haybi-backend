from databases import Database
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
DB_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./jobs.db")
db = Database(DB_URL)

# SQL to create jobs table
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    prompt TEXT,
    original_path TEXT,
    result_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

async def init_db():
    """Initialize the database and create tables if they don't exist"""
    await db.execute(CREATE_TABLE_SQL)

async def create_job(job_id: str, prompt: str, original_path: str):
    """Create a new job in the database"""
    query = """
    INSERT INTO jobs (id, status, prompt, original_path)
    VALUES (:job_id, :status, :prompt, :original_path)
    """
    values = {
        "job_id": job_id,
        "status": "pending",
        "prompt": prompt,
        "original_path": original_path
    }
    await db.execute(query, values)

async def get_job(job_id: str):
    """Get a job by its ID"""
    query = "SELECT * FROM jobs WHERE id = :job_id"
    return await db.fetch_one(query, {"job_id": job_id})

async def get_all_jobs():
    """Get all jobs"""
    query = "SELECT * FROM jobs ORDER BY created_at DESC"
    return await db.fetch_all(query)

async def update_job_status(job_id: str, status: str, result_url: str = None):
    """Update the status of a job"""
    query = """
    UPDATE jobs 
    SET status = :status, result_url = :result_url, updated_at = CURRENT_TIMESTAMP
    WHERE id = :job_id
    """
    values = {
        "job_id": job_id,
        "status": status,
        "result_url": result_url
    }
    await db.execute(query, values)