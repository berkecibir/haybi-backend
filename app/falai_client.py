import os
import httpx
from dotenv import load_dotenv

load_dotenv()
FALAI_KEY = os.getenv("FALAI_API_KEY")

FALAI_URL = "https://api.fal.ai/v1/images/edit"  # örnek endpoint; fal.ai dokümana göre uyarlayın

async def edit_image_with_falai(image_path: str, prompt: str):
    headers = {"Authorization": f"Bearer {FALAI_KEY}"}
    # fal.ai API parametreleri model ve body’ye göre değişebilir
    with open(image_path, "rb") as f:
        files = {"image": (image_path, f, "image/jpeg")}
        data = {"prompt": prompt, "model": "seedream-v4"}
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(FALAI_URL, headers=headers, files=files, data=data)
            resp.raise_for_status()
            return resp.json()