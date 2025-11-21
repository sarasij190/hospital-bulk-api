# Hospital Bulk Processing Service (FastAPI)

This project implements the Bulk Processing System for creating and activating hospitals by integrating with the supplied Hospital Directory API.

## Features
- POST /hospitals/bulk accepts CSV file (name,address,phone)
- Validates up to 20 rows
- Generates a UUID batch id
- Creates hospitals using the external Hospital Directory API
- Activates the batch when creation completes
- Returns a comprehensive result report

## Run locally (dev)

1. Create virtualenv and install deps

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

2. Open docs: http://localhost:8000/docs

## Docker

```bash
docker build -t hospital-bulk-api .
docker run -p 8000:8000 hospital-bulk-api
```

