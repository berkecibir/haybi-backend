from databases import Database
import os
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./jobs.db")
db = Database(DB_URL)