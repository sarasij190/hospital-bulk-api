from fastapi import FastAPI
from app.routes import bulk

app = FastAPI(title="Hospital Bulk Processing API")

app.include_router(bulk.router, prefix="/hospitals", tags=["bulk"]) 

@app.get("/health")
async def health():
    return {"status": "ok"}
