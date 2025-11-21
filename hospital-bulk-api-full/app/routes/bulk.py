from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST

from app.clients.hospital_api import HospitalAPIClient
from app.services.bulk_processor import BulkProcessor
from app.utils import gen_batch_id
from typing import List
import os

HOSPITAL_API_BASE = os.getenv('HOSPITAL_API_BASE', 'https://hospital-directory.onrender.com')  # changeable via env if desired

router = APIRouter()

@router.post('/bulk')
async def bulk_upload(file: UploadFile = File(...)):
    contents = await file.read()

    # Basic CSV validation
    text = contents.decode('utf-8')
    lines = [l for l in text.splitlines() if l.strip()]
    if not lines:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='Empty CSV')

    # Validate header
    header = lines[0].strip().split(',')
    expected = ['name', 'address', 'phone']
    if len(header) < 2 or header[0].lower() != 'name' or header[1].lower() != 'address':
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='CSV header must be: name,address,phone')

    # Limit rows
    num_rows = max(0, len(lines) - 1)
    if num_rows == 0:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='No hospital rows found')
    if num_rows > 20:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='Maximum 20 hospitals allowed')

    batch_id = gen_batch_id()

    client = HospitalAPIClient(HOSPITAL_API_BASE)
    processor = BulkProcessor(client)

    try:
        report = await processor.process_csv_bytes(contents, batch_id)
        return JSONResponse(report)
    finally:
        await client.close()
