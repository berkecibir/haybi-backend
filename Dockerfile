FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

# Use the PORT environment variable provided by Render, default to 8000 if not set
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]